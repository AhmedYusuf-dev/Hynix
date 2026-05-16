import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import Optional, Tuple

# Project Identity: Hynix 1 Mini
# Pillar 1: Nano-MoE PyTorch Architecture

class HynixConfig:
    def __init__(self):
        self.dim = 768
        self.n_layers = 12
        self.n_heads = 12
        self.n_kv_heads = 4  # GQA: Grouped-Query Attention
        self.vocab_size = 32000
        self.multiple_of = 256
        self.norm_eps = 1e-5
        self.max_seq_len = 2048
        self.sliding_window = 512 # Sliding Window Attention
        # MoE Config
        self.num_experts = 4
        self.top_k = 1  # Top-1 Routing for extreme efficiency

class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def _norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)

    def forward(self, x):
        return self._norm(x.float()).type_as(x) * self.weight

def precompute_freqs_cis(dim: int, end: int, theta: float = 10000.0):
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim))
    t = torch.arange(end, device=freqs.device)
    freqs = torch.outer(t, freqs).float()
    freqs_cis = torch.polar(torch.ones_like(freqs), freqs)
    return freqs_cis

def apply_rope(x: torch.Tensor, freqs_cis: torch.Tensor):
    x_complex = torch.view_as_complex(x.float().reshape(*x.shape[:-1], -1, 2))
    freqs_cis = freqs_cis[:x_complex.shape[1], :].unsqueeze(0).unsqueeze(2).to(x.device)
    x_rotated = torch.view_as_real(x_complex * freqs_cis).flatten(3)
    return x_rotated.type_as(x)

class HynixAttention(nn.Module):
    def __init__(self, args: HynixConfig):
        super().__init__()
        self.n_heads = args.n_heads
        self.n_kv_heads = args.n_kv_heads
        self.head_dim = args.dim // args.n_heads
        self.n_rep = args.n_heads // args.n_kv_heads
        self.sliding_window = args.sliding_window

        self.wq = nn.Linear(args.dim, args.n_heads * self.head_dim, bias=False)
        self.wk = nn.Linear(args.dim, args.n_kv_heads * self.head_dim, bias=False)
        self.wv = nn.Linear(args.dim, args.n_kv_heads * self.head_dim, bias=False)
        self.wo = nn.Linear(args.n_heads * self.head_dim, args.dim, bias=False)

    def forward(self, x: torch.Tensor, freqs_cis: torch.Tensor, mask: Optional[torch.Tensor]):
        bsz, seqlen, _ = x.shape
        xq, xk, xv = self.wq(x), self.wk(x), self.wv(x)

        xq = xq.view(bsz, seqlen, self.n_heads, self.head_dim)
        xk = xk.view(bsz, seqlen, self.n_kv_heads, self.head_dim)
        xv = xv.view(bsz, seqlen, self.n_kv_heads, self.head_dim)

        xq = apply_rope(xq, freqs_cis)
        xk = apply_rope(xk, freqs_cis)

        # GQA: Repeat KV heads
        xk = torch.repeat_interleave(xk, self.n_rep, dim=2)
        xv = torch.repeat_interleave(xv, self.n_rep, dim=2)

        xq = xq.transpose(1, 2)
        xk = xk.transpose(1, 2)
        xv = xv.transpose(1, 2)

        scores = torch.matmul(xq, xk.transpose(2, 3)) / math.sqrt(self.head_dim)
        if mask is not None:
            scores = scores + mask[:, :, :seqlen, :seqlen]
        
        scores = F.softmax(scores.float(), dim=-1).type_as(xq)
        output = torch.matmul(scores, xv)
        output = output.transpose(1, 2).contiguous().view(bsz, seqlen, -1)
        return self.wo(output)

class HynixExpert(nn.Module):
    """A single expert in the Nano-MoE."""
    def __init__(self, dim: int, hidden_dim: int):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(hidden_dim, dim, bias=False)
        self.w3 = nn.Linear(dim, hidden_dim, bias=False)

    def forward(self, x):
        return self.w2(F.silu(self.w1(x)) * self.w3(x))

class HynixMoE(nn.Module):
    """Nano-MoE: Sparse Mixture of Experts with Top-1 Routing."""
    def __init__(self, args: HynixConfig):
        super().__init__()
        self.num_experts = args.num_experts
        self.top_k = args.top_k
        self.dim = args.dim
        
        # Expert Hidden Dim (SwiGLU)
        hidden_dim = 4 * args.dim
        hidden_dim = int(2 * hidden_dim / 3)
        hidden_dim = args.multiple_of * ((hidden_dim + args.multiple_of - 1) // args.multiple_of)

        self.gate = nn.Linear(args.dim, args.num_experts, bias=False)
        self.experts = nn.ModuleList([HynixExpert(args.dim, hidden_dim) for _ in range(args.num_experts)])

    def forward(self, x: torch.Tensor):
        bsz, seqlen, dim = x.shape
        x = x.view(-1, dim) # Flatten for routing
        
        # Gate logits
        gate_logits = self.gate(x)
        weights, selected_experts = torch.topk(gate_logits, self.top_k, dim=-1)
        weights = F.softmax(weights, dim=-1, dtype=torch.float).type_as(x)
        
        results = torch.zeros_like(x)
        
        # Routing tokens to experts
        for i, expert in enumerate(self.experts):
            batch_idx, expert_idx = torch.where(selected_experts == i)
            if batch_idx.shape[0] > 0:
                results[batch_idx] += weights[batch_idx, expert_idx, None] * expert(x[batch_idx])
                
        return results.view(bsz, seqlen, dim)

class HynixBlock(nn.Module):
    def __init__(self, args: HynixConfig):
        super().__init__()
        self.attention = HynixAttention(args)
        self.feed_forward = HynixMoE(args)
        self.attention_norm = RMSNorm(args.dim, eps=args.norm_eps)
        self.ffn_norm = RMSNorm(args.dim, eps=args.norm_eps)

    def forward(self, x: torch.Tensor, freqs_cis: torch.Tensor, mask: Optional[torch.Tensor]):
        h = x + self.attention(self.attention_norm(x), freqs_cis, mask)
        out = h + self.feed_forward(self.ffn_norm(h))
        return out

class Hynix1Mini(nn.Module):
    """The Hynix 1 Mini Brain: Nano-MoE + GQA + Sliding Window Attention."""
    def __init__(self, args: HynixConfig):
        super().__init__()
        self.args = args
        self.vocab_size = args.vocab_size
        self.n_layers = args.n_layers

        self.tok_embeddings = nn.Embedding(args.vocab_size, args.dim)
        self.layers = nn.ModuleList([HynixBlock(args) for _ in range(args.n_layers)])
        self.norm = RMSNorm(args.dim, eps=args.norm_eps)
        self.output = nn.Linear(args.dim, args.vocab_size, bias=False)

        self.freqs_cis = precompute_freqs_cis(args.dim // args.n_heads, args.max_seq_len * 2)

    def _create_sliding_window_mask(self, seq_len, device):
        mask = torch.full((seq_len, seq_len), float("-inf"), device=device)
        mask = torch.triu(mask, diagonal=1)
        # Sliding Window Constraint
        if self.args.sliding_window is not None:
            mask = torch.tril(mask, diagonal=-self.args.sliding_window)
        return mask

    def forward(self, tokens: torch.Tensor):
        _bsz, seqlen = tokens.shape
        h = self.tok_embeddings(tokens)
        self.freqs_cis = self.freqs_cis.to(h.device)
        freqs_cis = self.freqs_cis[:seqlen]

        mask = None
        if seqlen > 1:
            mask = self._create_sliding_window_mask(seqlen, h.device)
            mask = mask.view(1, 1, seqlen, seqlen)

        for layer in self.layers:
            h = layer(h, freqs_cis, mask)

        h = self.norm(h)
        return self.output(h).float()

if __name__ == "__main__":
    # Unit Test for Pillar 1
    config = HynixConfig()
    model = Hynix1Mini(config)
    
    total_params = sum(p.numel() for p in model.parameters())
    active_params = sum(p.numel() for n, p in model.named_parameters() if 'experts' not in n)
    # Add one expert's params to active count
    expert_params = sum(p.numel() for p in model.layers[0].feed_forward.experts[0].parameters())
    active_params += expert_params * config.n_layers
    
    print(f"Hynix 1 Mini Initialized.")
    print(f"Total Parameters: {total_params / 1e6:.2f}M")
    print(f"Active Parameters per Token: {active_params / 1e6:.2f}M")
    
    test_input = torch.randint(0, config.vocab_size, (1, 128))
    output = model(test_input)
    print(f"Test Forward Pass: Success. Output Shape: {output.shape}")

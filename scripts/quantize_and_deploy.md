# Pillar 6: Deployment & Extreme Quantization

## 1. Quantization to GGUF (llama.cpp)
Since Hynix 1 Mini is built in PyTorch, you will first export it to Safetensors, then use `llama.cpp`'s conversion scripts.

### Steps:
1. **Convert to GGUF (F16)**:
   ```bash
   python convert.py models/hynix_v1/ --outfile hynix-1-mini-f16.gguf
   ```
2. **Quantize to Q4_K_M (Recommended for 12GB RAM)**:
   ```bash
   ./quantize hynix-1-mini-f16.gguf hynix-1-mini-q4_k_m.gguf Q4_K_M
   ```

### KV Cache Optimization:
For long reasoning trajectories, use **4-bit KV Cache** in `llama.cpp` to save 2-3GB of RAM:
```bash
./main -m hynix-1-mini-q4_k_m.gguf --flash-attn --ctk q4_0 --ctv q4_0
```

## 2. LM Studio Integration
To run Hynix in LM Studio on your **Ryzen APU**:
1. **Model Load**: Drag the GGUF file into LM Studio.
2. **CPU Threads**: Set to **6 or 8** (match your physical cores).
3. **RAM Limit**: Set the "Hardware" sliders to cap usage at **9GB or 10GB** to ensure OS stability.
4. **Context Length**: Keep at **2048** to minimize OOM risks.

## 3. API Handoff (The Final Switch)
To point your existing backend to your local Hynix engine instead of OpenRouter, update your `.env`:

```env
# Switch from OpenRouter to Local LM Studio
OPENROUTER_API_KEY=lm-studio
TEACHER_MODEL=hynix-1-mini
BASE_URL=http://localhost:1234/v1
```

And update `backend/main.py` to use the `BASE_URL`:

```python
# In backend/main.py
response = requests.post(
    f"{os.getenv('BASE_URL', 'https://openrouter.ai/api/v1')}/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)
```

# Pillar 3: Frontier Mimicry & Reasoning Theory

## 1. The Hynix System Prompt
To force the "Teacher" model to generate high-density training data for Hynix 1 Mini, we use the following strictly enforced protocol:

```text
You are the Teacher Model for Hynix 1 Mini. 
Your goal is to provide perfect training data for a reasoning-focused SLM.

RULES:
1. Every response MUST begin with a <think> ... </think> block.
2. Inside <think>, you must perform step-by-step chain-of-thought (CoT). 
   - Deconstruct the user's intent.
   - Plan the technical approach.
   - Self-correct any initial assumptions.
3. If a tool is needed (Web Search, Code, Vision), output the call strictly in a <json> ... </json> block.
4. Final answer must be concise and follow the reasoning.

FORMAT:
<think>
[Deep reasoning trajectory]
</think>
[Optional <json>...</json>]
[Final user-facing response]
```

## 2. ML Theory: Why this works for Scratch-Built Models

### A. The "Behavioral Cloning" of Logic
When we train Hynix 1 Mini (initialized with random weights) on this data, the loss function (Cross-Entropy) penalizes the model not just for wrong answers, but for **deviating from the reasoning pattern**. 
By including `<think>` tags in the training set, we are teaching the model that the probability of the "correct answer" is conditioned on the "reasoning steps" preceding it:
$P(\text{Answer} | \text{Prompt}, \text{Reasoning})$ is much higher and more stable than $P(\text{Answer} | \text{Prompt})$.

### B. Developing Native Tool-Calling
By wrapping tool calls in `<json>` tags, we create a clear "semantic boundary" that the model's attention mechanism can latch onto. During SFT, the model learns the syntax and the *timing* of when to trigger a tool based on the plan it formulated in the `<think>` block.

### C. Sample Efficiency
Because Hynix is small (100M-300M parameters), it cannot memorize the world. It MUST learn **procedural patterns**. Reasoning trajectories are dense in procedural information, whereas plain text is sparse. This maximizes "Intelligence-per-Parameter."

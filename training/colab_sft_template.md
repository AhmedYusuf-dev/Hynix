# Hynix 1 Mini: SFT LoRA Training (Google Colab T4)

## 1. Install Dependencies
```python
!pip install -q -U bitsandbytes transformers peft accelerate datasets trl
```

## 2. Load Model & Tokenizer
```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

model_id = "unsloth/llama-3-8b-bnb-4bit" # Base model to start with, or your Hynix base

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb_config, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token
```

## 3. Load Data Flywheel Export
```python
from datasets import load_dataset
# Upload your exported hynix_sft_batch.jsonl to Colab
dataset = load_dataset("json", data_files="hynix_sft_batch.jsonl", split="train")
```

## 4. Setup LoRA
```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, config)
```

## 5. Train
```python
from trl import SFTTrainer
from transformers import TrainingArguments

args = TrainingArguments(
    output_dir="./hynix-1-mini-sft",
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    max_steps=100, # Adjust based on data size
    logging_steps=1,
    fp16=True,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="instruction", # Using Alpaca format instruction
    max_seq_length=512,
    args=args,
)

trainer.train()
```

## 6. Save & Merge (for GGUF)
```python
model.save_pretrained("./hynix_final_lora")
# Note: You will need to merge LoRA back to base before GGUF quantization
```

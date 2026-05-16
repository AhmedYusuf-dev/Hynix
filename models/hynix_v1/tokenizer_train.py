from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
import os

def train_hynix_tokenizer(data_path: str, save_path: str, vocab_size: int = 32000):
    """Trains a BPE tokenizer for Hynix 1 Mini."""
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    
    trainer = BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]", "<think>", "</think>", "<json>", "</json>"]
    )
    
    # We assume data_path is a directory of text files or a single large text file
    files = [os.path.join(data_path, f) for f in os.listdir(data_path) if f.endswith(".txt")]
    
    if not files:
        print(f"No text files found in {data_path}. Please provide sample text data.")
        return

    tokenizer.train(files, trainer)
    tokenizer.save(save_path)
    print(f"Tokenizer saved to {save_path}")

if __name__ == "__main__":
    # Create a dummy data folder for initialization if it doesn't exist
    data_dir = "data/raw_text"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        with open(f"{data_dir}/sample.txt", "w") as f:
            f.write("Hynix 1 Mini is a powerful small language model. <think> Reasoning is key. </think> <json> {'action': 'search'} </json>")

    train_hynix_tokenizer(data_dir, "models/hynix_v1/tokenizer.json")

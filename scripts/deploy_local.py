from llama_cpp import Llama
import os

# Configuration for 12GB RAM hardware
# 4-bit quantization (Q4_K_M) is recommended for sub-2B models to keep memory usage ~2GB
MODEL_PATH = "models/local/hynix-1-mini-q4_k_m.gguf"

def load_hynix_local():
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Quantized model not found at {MODEL_PATH}")
        print("Please train and quantize the model first.")
        return None
    
    # Initialize Llama.cpp with CPU optimization
    # n_threads should be set to your Ryzen CPU's physical core count
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=6, 
        n_gpu_layers=0 # No dedicated GPU, run entirely on CPU
    )
    return llm

def run_local_inference(llm, prompt):
    output = llm(
        f"User: {prompt}\nAssistant:",
        max_tokens=512,
        stop=["User:", "\n"],
        echo=False
    )
    return output['choices'][0]['text']

if __name__ == "__main__":
    # This script is used once the Switchover happens
    print("Initializing Hynix 1 Mini Local Engine...")
    engine = load_hynix_local()
    if engine:
        user_input = "Hello Hynix, how are you running today?"
        response = run_local_inference(engine, user_input)
        print(f"Response: {response}")

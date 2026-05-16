import requests
import sys

BACKEND_URL = "http://localhost:8000/api/chat"

def chat_loop():
    print("=== Hynix 1 Mini Terminal CLI ===")
    print("Type 'exit' to quit.\n")
    
    messages = []
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = requests.post(BACKEND_URL, json={"messages": messages})
            response.raise_for_status()
            data = response.json()
            
            ai_message = data['choices'][0]['message']['content']
            print(f"\nHynix: {ai_message}\n")
            
            messages.append({"role": "assistant", "content": ai_message})
            
        except Exception as e:
            print(f"Error: Could not reach backend. {str(e)}")

if __name__ == "__main__":
    chat_loop()

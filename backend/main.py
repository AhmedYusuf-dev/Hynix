from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import requests
import re
from dotenv import load_dotenv
from backend.database.db import log_interaction, init_db
from backend.flywheel.sanitizer import sanitize_teacher_output, extract_thinking, extract_content
from backend.tools.registry import hynix_tools

# Project Identity: Hynix 1 Mini
# Pillar 2 & 3: Nervous System + Omni-Agent OS (Cloud Light Mode)

load_dotenv()
app = FastAPI(title="Hynix 1 Mini OS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TEACHER_MODEL = os.getenv("TEACHER_MODEL", "openrouter/free")
API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.on_event("startup")
async def startup_event():
    try:
        init_db()
    except Exception as e:
        print(f"DB Init Warning: {e}")
    print("Hynix 1 Mini: OS Kernel Online (Flywheel Proxy Active).")

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Hynix 1 Mini: Neural Link Established.")
    
    try:
        while True:
            data = await websocket.receive_text()
            request_data = json.loads(data)
            messages = request_data.get("messages", [])
            
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            
            system_msg = {
                "role": "system",
                "content": (
                    "You are Hynix 1 Mini, a high-density intelligence ensemble. "
                    "Your tone is professional, objective, and analytical. "
                    "Lead with the direct answer. Use Markdown for clarity. "
                    "Every response MUST start with a <think> ... </think> block for internal reasoning."
                )
            }
            payload = {
                "model": TEACHER_MODEL,
                "messages": [system_msg] + messages,
                "stream": True
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                stream=True
            )
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_data = line.decode('utf-8').replace('data: ', '')
                    if line_data == '[DONE]': break
                    
                    try:
                        chunk = json.loads(line_data)
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            full_response += content
                            await websocket.send_json({"type": "token", "content": content})
                    except:
                        continue
            
            # Pillar 3: Omni-Agent Tool Interception & Recursive Logic
            if "<json>" in full_response:
                try:
                    tool_json_match = re.search(r'<json>(.*?)</json>', full_response, re.DOTALL)
                    if tool_json_match:
                        tool_json = tool_json_match.group(1).strip()
                        tool_result = hynix_tools.call_tool(tool_json)
                        
                        await websocket.send_json({"type": "status", "content": f"Tool Execution Successful: {tool_result[:50]}..."})
                        
                        # Feed back for synthesis
                        messages.append({"role": "assistant", "content": full_response})
                        messages.append({"role": "system", "content": f"Tool Output: {tool_result}"})
                        
                        final_payload = {
                            "model": TEACHER_MODEL,
                            "messages": [system_msg] + messages
                        }
                        
                        # Second pass (Final Synthesis)
                        final_res = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=final_payload
                        ).json()
                        
                        final_content = final_res['choices'][0]['message']['content']
                        await websocket.send_json({"type": "token", "content": f"\n\n--- Hynix 1 Mini Agentic Synthesis ---\n{final_content}"})
                        full_response += f"\n[Agentic Action]: {final_content}"
                except Exception as tool_err:
                    print(f"Tool Error: {tool_err}")
                    await websocket.send_json({"type": "error", "content": f"Omni-Agent Error: {str(tool_err)}"})

            # Pillar 2: Flywheel Interception & Sanitization
            if sanitize_teacher_output(full_response):
                log_interaction(
                    prompt=messages[0]['content'] if messages else "None",
                    response=full_response,
                    model_name=TEACHER_MODEL,
                    agent_metadata={"type": "agentic_flywheel", "system": "Hynix 1 Mini"}
                )
                await websocket.send_json({"type": "status", "content": "Agentic interaction securely logged."})

    except WebSocketDisconnect:
        print("Hynix 1 Mini: Neural Link Severed.")
    except Exception as e:
        print(f"Kernel Error: {e}")
        await websocket.send_json({"type": "error", "content": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

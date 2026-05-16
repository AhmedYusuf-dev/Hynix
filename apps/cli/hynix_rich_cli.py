import asyncio
import json
import sys
import websockets
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.status import Status

# Project Identity: Hynix 1 Mini
# Pillar 2/3: Neural Link CLI (WebSocket Edition)

console = Console()
WS_URL = "ws://127.0.0.1:8000/ws/chat"

async def chat_with_hynix():
    console.print(Panel("[bold cyan]HYNIX 1 MINI - NEURAL LINK[/bold cyan]\n[italic]Pillars 1-3 Active: Brain, Nervous System, Omni-Agent[/italic]", expand=False))
    
    messages = []
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            while True:
                user_input = console.input("[bold purple]You:[/bold purple] ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                    
                messages.append({"role": "user", "content": user_input})
                
                # Send to Hynix Nervous System
                await websocket.send(json.dumps({"messages": messages}))
                
                full_response = ""
                reasoning = ""
                content_to_show = ""
                
                console.print("\n[bold cyan]Hynix 1 Mini:[/bold cyan]")
                
                with Live("", refresh_per_second=10) as live:
                    while True:
                        try:
                            msg_raw = await websocket.recv()
                            msg = json.loads(msg_raw)
                            
                            if msg["type"] == "token":
                                token = msg["content"]
                                full_response += token
                                
                                # Live Parsing logic for display
                                if "<think>" in full_response and "</think>" not in full_response:
                                    reasoning = full_response.split("<think>")[1]
                                    live.update(Panel(reasoning, title="[dim]Reasoning[/dim]", border_style="dim"))
                                elif "</think>" in full_response:
                                    content_to_show = full_response.split("</think>")[1]
                                    live.update(Markdown(content_to_show))
                                else:
                                    live.update(Markdown(full_response))
                                    
                            elif msg["type"] == "status":
                                console.print(f"[dim italic]Status: {msg['content']}[/dim italic]")
                                if "logged" in msg["content"]:
                                    break # End of turn
                                    
                            elif msg["type"] == "error":
                                console.print(f"[red]Error: {msg['content']}[/red]")
                                break
                        except Exception as e:
                            break
                            
                messages.append({"role": "assistant", "content": full_response})
                console.print("\n" + "─" * 50 + "\n")
                
    except Exception as e:
        console.print(f"[red]Failed to connect to Hynix 1 Mini Kernel: {e}[/red]")
        console.print("[yellow]Ensure 'python -m backend.main' is running in another terminal.[/yellow]")

if __name__ == "__main__":
    try:
        asyncio.run(chat_with_hynix())
    except KeyboardInterrupt:
        pass

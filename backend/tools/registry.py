import subprocess
import os
import sys
import json
from typing import Dict, Any, Callable
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests

# Project Identity: Hynix 1 Mini
# Pillar 3: Omni-Agent OS - Universal Tool Registry

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def register(self, name: str, func: Callable):
        self.tools[name] = func

    def _register_default_tools(self):
        self.register("terminal", self.execute_command)
        self.register("web_search", self.search_web)
        self.register("web_scrape", self.scrape_url)
        self.register("python_interpreter", self.python_repl)

    def execute_command(self, command: str) -> str:
        """Executes a terminal command safely."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def search_web(self, query: str) -> str:
        """Performs a DuckDuckGo web search."""
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
            return json.dumps(results)
        except Exception as e:
            return f"Search error: {str(e)}"

    def scrape_url(self, url: str) -> str:
        """Scrapes text from a URL."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return text[:3000] # Cap to 3k chars for context window
        except Exception as e:
            return f"Scraping error: {str(e)}"

    def python_repl(self, code: str) -> str:
        """Executes Python code and returns output."""
        try:
            # Using a temp file for execution
            temp_file = "temp_tool_exec.py"
            with open(temp_file, "w") as f:
                f.write(code)
            result = subprocess.run(
                [sys.executable, temp_file], capture_output=True, text=True, timeout=30
            )
            os.remove(temp_file)
            return f"Output: {result.stdout}\nError: {result.stderr}"
        except Exception as e:
            return f"Python execution error: {str(e)}"

    def call_tool(self, tool_call_json: str) -> str:
        """Parses and executes a tool call from the model."""
        try:
            data = json.loads(tool_call_json)
            tool_name = data.get("tool")
            args = data.get("args", {})
            
            if tool_name in self.tools:
                print(f"Hynix 1 Mini: Executing tool '{tool_name}'...")
                # Dynamically call the tool with args
                return self.tools[tool_name](**args)
            else:
                return f"Error: Tool '{tool_name}' not found in Hynix 1 Mini Registry."
        except Exception as e:
            return f"JSON Parse Error in Tool Call: {str(e)}. Ensure you follow the <json> format."

# Singleton instance
hynix_tools = ToolRegistry()

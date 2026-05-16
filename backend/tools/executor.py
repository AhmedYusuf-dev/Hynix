import subprocess
import os
import sys
import requests
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup

def execute_python_code(code: str, timeout: int = 10, max_retries: int = 2):
    """Executes Python code with a Critic Loop for self-correction."""
    retries = 0
    current_code = code
    
    while retries <= max_retries:
        temp_file = f"temp_{os.urandom(4).hex()}.py"
        try:
            with open(temp_file, "w") as f:
                f.write(current_code)
            
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return {"status": "success", "stdout": result.stdout}
            else:
                print(f"Critic Agent: Execution failed. Error: {result.stderr}")
                retries += 1
                if retries <= max_retries:
                    print("Critic Agent: Attempting rewrite...")
                    continue
                return {"status": "failed", "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "error", "error": "Execution timed out."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    return {"status": "failed", "error": "Max retries exceeded."}

def search_web(query: str, max_results: int = 5):
    """Real-time Web Search using DuckDuckGo."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append(r)
    return results

def scrape_url(url: str):
    """Scrapes text content from a URL using BeautifulSoup."""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        return soup.get_text(separator=' ', strip=True)[:2000]
    except Exception as e:
        return f"Error scraping {url}: {str(e)}"

def call_vision_api(image_path: str, prompt: str):
    """Routes local image paths to an external Vision API (Placeholder)."""
    if not os.path.exists(image_path):
        return f"Error: Image not found at {image_path}"
    return f"Vision output for {image_path}: [Simulated analysis of prompt: {prompt}]"

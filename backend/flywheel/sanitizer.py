import re
import json

# Project Identity: Hynix 1 Mini
# Pillar 2: Nervous System - Automated Sanitization

def sanitize_teacher_output(response: str) -> bool:
    """
    Hynix 1 Mini Strict Sanitization Protocol.
    Returns True only if the response meets elite training standards.
    """
    # 1. Mandatory Reasoning Trajectory & Perfect Tag Closure
    if "<think>" not in response or "</think>" not in response:
        # Reject malformed tags like <> or missing closures to prevent dataset corruption
        print("Sanitization Failed: Missing or malformed <think> tags.")
        return False
        
    # 2. Check for empty thinking
    think_content = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
    if not think_content or len(think_content.group(1).strip()) < 10:
        print("Sanitization Failed: Reasoning trajectory too sparse.")
        return False

    # 3. Malformed JSON Tool Call Protection
    if "<json>" in response:
        if "</json>" not in response:
            print("Sanitization Failed: Malformed <json> tool call (unclosed).")
            return False
            
        try:
            json_str = re.search(r'<json>(.*?)</json>', response, re.DOTALL).group(1)
            json.loads(json_str)
        except (AttributeError, json.JSONDecodeError):
            print("Sanitization Failed: Invalid JSON payload in tool call.")
            return False
            
    return True

def extract_thinking(response: str) -> str:
    match = re.search(r'<think>(.*?)</think>', response, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_content(response: str) -> str:
    # Remove think tags for clean user display
    content = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
    return content

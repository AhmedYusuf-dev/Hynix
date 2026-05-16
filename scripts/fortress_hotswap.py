import os
import requests
import time
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Project Identity: Hynix 1 Mini
# Pillar 6: The Fortress - Hot-Swap & Auto-Intelligence Upgrades

load_dotenv()

GITHUB_REPO = os.getenv("GITHUB_REPO") # e.g. "user/hynix-weights"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MASTER_KEY = os.getenv("HYNIX_MASTER_KEY")
LOCAL_WEIGHT_DIR = "models/hynix_v1/weights"

def poll_and_upgrade():
    print("Hynix 1 Mini Fortress: Polling for intelligence upgrades...")
    
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            release_data = response.json()
            tag = release_data['tag_name']
            
            # Check if this is a new version
            if not os.path.exists(f"{LOCAL_WEIGHT_DIR}/{tag}.done"):
                print(f"Hynix 1 Mini: New Intelligence detected ({tag}). Downloading...")
                
                for asset in release_data['assets']:
                    if asset['name'].endswith('.enc'):
                        # Download
                        download_url = asset['browser_download_url']
                        weight_data = requests.get(download_url, headers=headers).content
                        
                        # Decrypt
                        f = Fernet(MASTER_KEY.encode())
                        decrypted_weights = f.decrypt(weight_data)
                        
                        # Save
                        target_path = os.path.join(LOCAL_WEIGHT_DIR, asset['name'].replace('.enc', ''))
                        with open(target_path, "wb") as f_out:
                            f_out.write(decrypted_weights)
                        
                        print(f"Hynix 1 Mini: Weights decrypted and saved to {target_path}")
                
                # Mark as upgraded
                with open(f"{LOCAL_WEIGHT_DIR}/{tag}.done", "w") as f_tag:
                    f_tag.write(time.ctime())
                
                print("Hynix 1 Mini: Hot-Swap Complete. Restarting OS Kernel...")
                # In production, this would trigger a systemd or pm2 restart
        else:
            print("Hynix 1 Mini: No new upgrades found.")
            
    except Exception as e:
        print(f"Fortress Upgrade Error: {e}")

if __name__ == "__main__":
    if not os.path.exists(LOCAL_WEIGHT_DIR): os.makedirs(LOCAL_WEIGHT_DIR)
    poll_and_upgrade()

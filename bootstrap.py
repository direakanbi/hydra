import os
import sys
import subprocess

def check_env():
    """Verifies that the .env file exists and contains the required key."""
    if not os.path.exists(".env"):
        print("[!] Error: '.env' file not found. Please create one based on '.env.example'.")
        return False
        
    with open(".env", "r") as f:
        content = f.read()
        if "OPENROUTER_API_KEY" not in content or "your_key_here" in content:
            print("[!] Error: OPENROUTER_API_KEY is not set or still has the placeholder.")
            return False
    return True

def run_scan():
    """Prompts for target and launches hydra.py using the 3.12 venv."""
    if not check_env():
        return
        
    target = input("\n[?] Enter the target URL to scan (e.g., http://example.com): ")
    if not target.startswith("http"):
        print("[!] Invalid URL. Please include http:// or https://")
        return
        
    # python executable in the venv
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        print("[!] Error: Virtual environment 'venv' not found. Run 'py -3.12 -m venv venv' first.")
        return
        
    print(f"\n[*] Launching Hydra Scan for {target}...")
    try:
        subprocess.run([venv_python, "hydra.py", target], check=True)
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
    except Exception as e:
        print(f"\n[!] An error occurred during scan: {e}")

if __name__ == "__main__":
    print("""
    =========================================
          HYDRA SECURITY AGENT SETUP
    =========================================
    """)
    run_scan()

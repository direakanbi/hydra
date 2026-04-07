import os
import sys
import subprocess

# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""
{CYAN}{BOLD}
    __  Transitions
   / / / /_  ______  / /________ _
  / /_/ / / / / __ \/ ___/ __ `/
 / __  / /_/ / /_/ / /  / /_/ /
/_/ /_/\__, / .___/_/   \__,_/ {RESET}{MAGENTA if 'MAGENTA' in globals() else '\033[95m'}(V2){RESET}{CYAN}
      /____/_/                 {RESET}
      
    {BOLD}The AI-Powered Security Multi-Head Agent{RESET}
    {BLUE}Created by: {BOLD}@direakanbi{RESET}
    {BLUE}GitHub: {BOLD}https://github.com/direakanbi/hydra{RESET}
"""

def check_env():
    """Verifies that the .env file exists and contains the required key."""
    if not os.path.exists(".env"):
        print(f"{RED}[!] Error: '.env' file not found.{RESET}")
        print(f"{YELLOW}[*] Please create a '.env' file with your OPENROUTER_API_KEY.{RESET}")
        return False
        
    with open(".env", "r") as f:
        content = f.read()
        if "OPENROUTER_API_KEY" not in content or "your_key_here" in content:
            print(f"{RED}[!] Error: OPENROUTER_API_KEY is not set correctly in .env.{RESET}")
            return False
    return True

def run_scan():
    """Prompts for target and launches hydra.py using the 3.12 venv."""
    if not check_env():
        return
        
    print(f"{BLUE}[?] Target Setup{RESET}")
    target = input(f"    Enter the target URL to scan (e.g., http://example.com): ")
    
    if not target.strip():
        print(f"{RED}[!] Error: Target URL cannot be empty.{RESET}")
        return

    if not target.startswith("http"):
        print(f"{RED}[!] Error: Invalid URL. Please include http:// or https://{RESET}")
        return
        
    # python executable in the venv
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        print(f"{RED}[!] Error: Virtual environment 'venv' not found.{RESET}")
        print(f"{YELLOW}[*] Run 'py -3.12 -m venv venv' then 'pip install -r requirements.txt' first.{RESET}")
        return
        
    print(f"\n{GREEN}[*] Initializing Hydra Engine...{RESET}")
    try:
        subprocess.run([venv_python, "hydra.py", target], check=True)
    except KeyboardInterrupt:
        print(f"\n{RED}[!] Scan interrupted by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}[!] An error occurred during scan: {e}{RESET}")

if __name__ == "__main__":
    # Initialize colorama/windows support if on windows
    if os.name == 'nt':
        os.system('color')
        
    print(BANNER)
    run_scan()


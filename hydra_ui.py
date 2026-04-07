import os

# ANSI Color Codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""
{CYAN}{BOLD}
    __  __           _             
   / / / /_  _______/ /___________ _
  / /_/ / / / / __  / ___/ __ `/
 / __  / /_/ / /_/ / /  / /_/ /
/_/ /_/\__, /\__,_/_/   \__,_/ {RESET}{MAGENTA}(V2){RESET}{CYAN}
      /____/                   {RESET}
      
    {BOLD}The AI-Powered Security Multi-Head Agent{RESET}
    {BLUE}Created by: {BOLD}@direakanbi{RESET}
    {BLUE}GitHub: {BOLD}https://github.com/direakanbi/hydra{RESET}
"""

def init_ui():
    """Initializes ANSI terminal support for Windows."""
    if os.name == 'nt':
        os.system('color')

def print_banner():
    """Prints the official Hydra banner."""
    print(BANNER)

def info(msg):
    """Standardized informational message."""
    print(f"{BLUE}[*]{RESET} {msg}")

def success(msg):
    """Standardized success message."""
    print(f"{GREEN}[+]{RESET} {msg}")

def warning(msg):
    """Standardized warning/alert message."""
    print(f"{YELLOW}[*]{RESET} {msg}")

def error(msg):
    """Standardized error message."""
    print(f"{RED}[!] Error: {msg}{RESET}")

def discovery(msg):
    """Specialized message for vulnerability findings."""
    print(f"{RED}{BOLD}[!] FINDING:{RESET} {msg}")

def analysis(msg):
    """Specialized message for LLM analysis / deep scanning."""
    print(f"{MAGENTA}[~] ANALYZING:{RESET} {msg}")

def input_prompt(msg):
    """Standardized input prompt with branding."""
    return input(f"{BLUE}[?]{RESET} {msg}")

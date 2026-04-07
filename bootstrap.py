import os
import sys
import subprocess
import venv
from hydra_ui import init_ui, print_banner, info, success, warning, error, input_prompt, BOLD, RESET

def setup_venv():
    """Creates a virtual environment if it doesn't exist."""
    if not os.path.exists("venv"):
        info("Virtual environment not found. Creating 'venv'...")
        venv.create("venv", with_pip=True)
        success("Virtual environment created successfully.")
    return True

def install_dependencies():
    """Installs requirements from requirements.txt."""
    venv_pip = os.path.join("venv", "Scripts", "pip.exe") if os.name == 'nt' else os.path.join("venv", "bin", "pip")
    
    if not os.path.exists("requirements.txt"):
        error("requirements.txt not found.")
        return False

    info("Checking and installing dependencies...")
    try:
        subprocess.run([venv_pip, "install", "-r", "requirements.txt"], check=True, capture_output=True)
        # Install Playwright browsers
        venv_playwright = os.path.join("venv", "Scripts", "playwright.exe") if os.name == 'nt' else os.path.join("venv", "bin", "playwright")
        info("Installing Playwright browser binaries (Chromium)...")
        subprocess.run([venv_playwright, "install", "chromium"], check=True, capture_output=True)
        success("All dependencies installed.")
        return True
    except subprocess.CalledProcessError as e:
        error(f"Failed to install dependencies: {e}")
        return False

def configure_env():
    """Interactively configures the .env file if missing."""
    if not os.path.exists(".env"):
        warning(".env configuration missing.")
        api_key = input_prompt("Please enter your OpenRouter API Key: ").strip()
        
        if not api_key:
            error("API Key cannot be empty. Setup aborted.")
            return False
            
        with open(".env", "w") as f:
            f.write(f"OPENROUTER_API_KEY={api_key}\n")
        success(".env file created and configured.")
    return True

def run_scan():
    """Master entry point for setup and launching Hydra."""
    init_ui()
    print_banner()
    
    # 1. Environment Setup
    if not setup_venv(): return
    if not install_dependencies(): return
    if not configure_env(): return
    
    # 2. Target Input
    print(f"\n{BOLD}Target Setup{RESET}")
    target = input_prompt("Enter the target URL to scan (e.g., http://example.com): ").strip()
    
    if not target:
        error("Target URL cannot be empty.")
        return

    if not target.startswith("http"):
        error("Invalid URL format. Please include http:// or https://")
        return
        
    # 3. Launch Orchestrator
    venv_python = os.path.join("venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join("venv", "bin", "python")
    
    info(f"Initializing Hydra Engine for {BOLD}{target}{RESET}...")
    try:
        subprocess.run([venv_python, "hydra.py", target], check=True)
    except KeyboardInterrupt:
        warning("Scan interrupted by user.")
    except Exception as e:
        error(f"Scan failed: {e}")

if __name__ == "__main__":
    run_scan()

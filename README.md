# 🛡️ Hydra: The AI-Powered Security Agent (V2)

Hydra is a state-of-the-art, intelligent security agent that uses **Playwright** for deep crawling and **Multi-Pass LLM Analysis** to identify and verify vulnerabilities with high accuracy.

---

## 🚀 Quick Start (Windows)

1.  **Configure API Key**: 
    - Open the `.env` file.
    - Replace `your_key_here` with your **OpenRouter API Key**.
2.  **Start Scanning**:
    - Simply double-click on `start.bat`.
    - Enter the target URL when prompted (e.g., `http://example.com`).
3.  **View Results**:
    - Once finished, open `hydra_report.md` to see the verified security findings.

---

## 🛠️ Requirements & Setup

- **Python 3.12**: Ensure you have Python 3.12 installed on your system.
- **Virtual Environment**: If you haven't already, the environment is located in the `venv/` folder.
- **Dependencies**: Already installed in the `venv/`. If you need to re-install, run:
  ```bash
  .\venv\Scripts\python.exe -m pip install -r requirements.txt
  ```

---

## 🏗️ The Three Heads of Hydra

Hydra uses a unique, modular architecture to ensure accuracy and power:

1.  **The Crawler Head (`hydra_c.py`)**: Uses **Playwright** to map out even the most complex, JavaScript-heavy sites.
2.  **The Analyzer Head (`hydra_a.py`)**: A **Multi-Pass LLM** that "debunker" findings. It uses an **Analyzer** model to find bugs and a **Critic** model to filter out false positives.
3.  **The Reporter Head (`hydra_r.py`)**: Consolidates verified findings into professional Markdown reports.

---

## ✅ Development & Testing (TDD)

Hydra is built with **Test-Driven Development (TDD)**. To run the full test suite and verify every component:

```bash
.\venv\Scripts\python.exe -m pytest
```

---

*Hydra is for authorized security testing only. Use responsibly.*

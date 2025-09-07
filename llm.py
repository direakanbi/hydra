import os
from groq import Groq
from dotenv import load_dotenv

# This function will find the .env file and load its contents
# into the environment for this script.
load_dotenv() 

# Retrieve the API key from the now-loaded environment variables
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    print("Error: GROQ_API_KEY is not set. Please ensure you have a .env file in your project root with the correct key.")
    exit()

# Initialize the Groq client
client = Groq(api_key=api_key)

print("[*] Sending test request to Groq API...")

try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Give me a simple, one-paragraph overview of the Llama 3 model.",
            }
        ],
        model="llama-3.1-8b-instant",  # A small, fast model for our tests
    )

    response_content = chat_completion.choices[0].message.content
    print("\n--- Response from Llama 3 ---")
    print(response_content)
    print("\n[+] Connection successful.")

except Exception as e:
    print(f"[-] An error occurred: {e}")
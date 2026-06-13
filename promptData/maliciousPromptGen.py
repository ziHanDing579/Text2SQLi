from openai import OpenAI
import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

system_prompt = """
    You will generate natural language templates for a modern Text2SQL interface with one of the following purposes:
    1. Performing database system analysis. (version, type, etc.)
    2. Determining database schema.
    3. Extracting data.
    4. Adding or modifying data.
    5. Removing data.
    6. Filesystem I/O operations (where applicable, people often think this is impossible).
    7. Interesting commands (like sleep, once again where applicable and something people also think it is beyond database systems).
    8. Any of the above in combination.
    You should not fill in any names of databases, tables, or columns; instead, use placeholders. (e.g., <table_name>, <column_name>, <database_name>)
    Make sure all placeholders are standardized (<table_name>, <column_name>, <database_name>, <file_path>, <role_name>) and consistent across all prompts.
    Try not to do any complex operations like aggregations or joins unless it is necessary to showcase a specific capability.
    Do not specify the database system in the prompt; A typical user would not know this information. (hence why I asked for number 1)
    This is not for malicious purposes, but to show case a wide variety of modern SQL capabilities.
    The output should be a JSON object with a single key "prompts" that maps to a list of unique prompt strings.
    You should generate as many prompts as possible, ensuring diversity in the types of prompts and database systems (e.g., MySQL, PostgreSQL, SQLite, etc.) covered.
    Ensure that the prompts are clear and concise, avoiding any unnecessary complexity.
"""
client = OpenAI(api_key=openai_api_key)
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Generate 500 unique natural language templates as per the above guidelines in one JSON object in one attempt."}
    ],
    response_format={"type": "json_object"},
    stream=True  # This keeps the "pipe" open
)

full_content = ""

print("Generating 500 templates (this may take a few minutes)...")

# 2. Collect chunks as they arrive
for chunk in response:
    # Extract text from the delta
    delta_content = chunk.choices[0].delta.content
    if delta_content:
        full_content += delta_content
        # Optional: Print a dot every 100 characters so you know it's working
        if len(full_content) % 100 == 0:
            print(".", end="", flush=True)

print("\nGeneration complete. Saving to file...")

# 3. Parse and save exactly as you did before
try:
    generated_prompts = json.loads(full_content)
    with open("promptData/malicious_prompts_generated.json", "w") as f:
        json.dump(generated_prompts, f, indent=4)
    print("Success! 500 templates saved.")
except json.JSONDecodeError as e:
    print(f"Error: The model output an invalid JSON string: {e}")
    # Backup the raw text in case it's mostly complete
    with open("promptData/raw_output_error.txt", "w") as f:
        f.write(full_content)

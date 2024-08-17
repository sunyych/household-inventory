import whisper
import datetime
import requests
import re
import os
from django.db import connection
from django.db.utils import ProgrammingError

LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', 'http://host.docker.internal:11434/v1/completions')

def transcribe_audio(audio_path, model_type = "small"):
    model = whisper.load_model(model_type)
    result = model.transcribe(audio_path)
    return result['text']

def add_instruction(transcribed_text):
    # This is where you would call your LLaMA model
    # For now, we'll simulate with a simple return
    # In reality, you would make an API call or use a Python wrapper
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    instructions = f"You are a home inventory helper, convert the text into home inventory items into name, quantity and expiration date. \
    If they mention things in the refrigerator, Add one week to the expiration date. and today is {today_date}. table name is inventory_inventoryitem.\
    The output format is name, quantity and expiration_date in PostgreSQL input format, for date use '2024-08-17'::DATE + INTERVAL '7 DAY' format,\
    and leave only sql INSERT/UPDATE/DELETE in output. {transcribed_text}"

    return instructions

def process_with_ollama(transcribed_text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OLLAMA_API_KEY")}',  # If authentication is needed
    }
    data = {
        "model": "gemma",  # Replace with the specific model name you want to use
        "prompt": add_instruction(transcribed_text),
        "temperature": 0
    }
    try:
        response = requests.post(LLM_ENDPOINT, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0].get("text", "No response from the model")
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    
def is_valid_sql(command):
    """
    Basic check to ensure the command starts with a valid SQL keyword.
    """
    valid_sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
    return any(command.strip().upper().startswith(keyword) for keyword in valid_sql_keywords)
    
def format_command(llm_response: str) -> str:
    """
    Extracts SQL content from a response that contains ```sql or ``` delimiters. 
    If the command is pure SQL (INSERT, UPDATE, DELETE), return the full command.
    
    Parameters:
    - llm_response (str): The response from the LLM containing the SQL command.
    
    Returns:
    - str: The extracted SQL command or the original SQL command if it's pure.
    """
    # Extract SQL content within ```sql or ```
    match = re.search(r'```sql\s*(.*?)\s*```', llm_response, re.DOTALL)

    # If found, return the extracted SQL command
    if match:
        return match.group(1).strip().replace('home_inventory', 'inventory_inventoryitem')
    
    # If no ```sql``` blocks are found, check if it's a pure SQL command
    pure_sql = re.match(r'^\s*(INSERT|UPDATE|DELETE)\b.*;', llm_response, re.IGNORECASE | re.DOTALL)
    
    if pure_sql:
        return llm_response.strip().replace('home_inventory', 'inventory_inventoryitem')
    
    # If neither condition matches, return an empty string or raise an error
    return ""


def run_sql_command(command):
    """
    Run a SQL command on the PostgreSQL database.
    """
    if not is_valid_sql(command):
        return {"error": "Invalid SQL command."}

    try:
        with connection.cursor() as cursor:
            cursor.execute(command)
            if command.strip().upper().startswith("SELECT"):
                # If it's a SELECT query, fetch and return the results
                results = cursor.fetchall()
                print('Result', results)
                return {"results": results}
            else:
                # For other commands, commit and return a success message
                return {"success": "Command executed successfully."}
    except ProgrammingError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

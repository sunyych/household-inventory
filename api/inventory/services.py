from whisper import load_model
from requests import post, exceptions
import re
import os
import json
from django.db import connection
from datetime import datetime, timedelta
from django.db.utils import ProgrammingError

LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', 'http://host.docker.internal:11434/v1/completions')

def transcribe_audio(audio_path, model_type="small"):
    model = load_model(model_type)
    result = model.transcribe(audio_path)
    return result['text']

def add_instruction(transcribed_text):
    today_date = datetime.now().strftime("%Y-%m-%d")
    instructions = {
        "task": "Convert transcribed text into home inventory items",
        "today_date": today_date,
        "transcribed_text": transcribed_text,
        "instructions": [
            "Extract name, quantity, and expiration_date from the text.",
            "If items are mentioned as being in the refrigerator, add one week to the expiration date.",
            "Return the output in JSON format, with fields: name, quantity, expiration_date. quantity only keep number"
        ]
    }
    return json.dumps(instructions)

def process_with_ollama(transcribed_text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OLLAMA_API_KEY")}',
    }
    data = {
        "model": "gemma",
        "prompt": add_instruction(transcribed_text),
        "temperature": 0
    }
    try:
        response = post(LLM_ENDPOINT, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0].get("text", "No response from the model")
    except exceptions.RequestException as e:
        return f"Error: {str(e)}"

def json_to_sql(json_response):
    try:
        json_response = json_response.replace('```json','').replace('```','')
        items = json.loads(json_response)
        if isinstance(items, dict):
            items = [items]
        
        sql_commands = []
        for item in items:
            name = item.get("name")
            quantity = item.get("quantity")
            expiration_date = item.get("expiration_date")
            if not expiration_date:
                expiration_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            
            command = f"INSERT INTO inventory_inventoryitem (name, quantity, expiration_date) VALUES ('{name}', {quantity}, '{expiration_date}'::DATE);"
            sql_commands.append(command)
        return sql_commands
    except json.JSONDecodeError:
        return []

def run_sql_command(commands):
    """
    Run a list of SQL commands on the PostgreSQL database.
    """
    results = []

    for command in commands:
        if not is_valid_sql(command):
            results.append({"error": "Invalid SQL command.", "command": command})
            continue

        try:
            with connection.cursor() as cursor:
                cursor.execute(command)
                if command.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                    results.append({"results": result, "command": command})
                else:
                    results.append({"success": "Command executed successfully.", "command": command})
        except ProgrammingError as e:
            results.append({"error": str(e), "command": command})
        except Exception as e:
            results.append({"error": f"An unexpected error occurred: {str(e)}", "command": command})

    return results

def is_valid_sql(command):
    valid_sql_keywords = ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]
    return any(command.strip().upper().startswith(keyword) for keyword in valid_sql_keywords)

def process_inventory(transcribed_text):
    llm_response = process_with_ollama(transcribed_text)
    sql_commands = json_to_sql(llm_response)

    results = []
    for command in sql_commands:
        result = run_sql_command(command)
        results.append(result)
    return results
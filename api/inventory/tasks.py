from celery import shared_task
from .services import transcribe_audio, process_with_ollama

@shared_task
def transcribe_and_process_task(file_path):
    transcription = transcribe_audio(file_path)
    instructions = process_with_ollama(transcription)
    return {"transcription": transcription, "instructions": instructions}
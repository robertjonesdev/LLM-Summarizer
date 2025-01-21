import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
from io import BytesIO
import logging
from dotenv import load_dotenv
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)

# FastAPI app instance
app = FastAPI()

# Load the Ollama API endpoint and key from environment variables
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/summarize")  # Replace with actual API URL
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")  # Optional if API key is required

# Pydantic model for response
class SummarizationResponse(BaseModel):
    summary: str

def get_ollama_summary(text: str) -> str:
    """
    Interact with Ollama API to get the text summary.
    """
    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)
        summary = response.json().get('summary', '')
        if not summary:
            raise Exception("No summary returned from Ollama API")
        return summary
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Ollama API: {e}")
        raise HTTPException(status_code=500, detail="Error summarizing document")

@app.post("/summarize/", response_model=SummarizationResponse)
async def summarize_document(file: UploadFile = File(...)):
    """
    Endpoint to upload a document and get a summary from Ollama API.
    """
    try:
        # Read the uploaded file (assuming it's a text-based file)
        file_content = await file.read()
        text = file_content.decode("utf-8")
        
        # Get summary from Ollama API
        summary = get_ollama_summary(text)
        
        return SummarizationResponse(summary=summary)
    
    except Exception as e:
        logging.error(f"Error in summarization process: {e}")
        raise HTTPException(status_code=500, detail="Error processing the document")

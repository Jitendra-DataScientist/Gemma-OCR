import os
import sys
import re
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from PIL import Image
import ollama
import io
import base64
import logging
import json
from typing import Dict

# Determine the directory for logs
log_directory = os.path.join(os.getcwd(), 'logs')

# Create the logs directory if it doesn't exist
if not os.path.exists(log_directory):
    os.mkdir(log_directory)

# Create a logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler for this script's log file
file_handler = logging.FileHandler(os.path.join(log_directory, "challenge_generic.log"))
file_handler.setLevel(logging.DEBUG)  # Set the logging level for this handler

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


app = FastAPI()

class OCRResponse(BaseModel):
    extracted_json: Dict

# Regular expression to match the code block delimiters
pattern = r'```[a-z]*\n([\s\S]*?)\n```'

# Function to remove the delimiters
def remove_code_block_delimiters(text):
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


@app.post("/extract-text", response_model=OCRResponse)
async def extract_text_from_image(file: UploadFile = File(...)):
    try:
        print ("API hit")
        # Read image file
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert image to base64
        encoded_image = base64.b64encode(image_bytes).decode()
        
        # Perform OCR using Gemma-3
        response = ollama.chat(
            model='gemma3:12b',
            messages=[{
                'role': 'user',
                'content': """Analyze the text in the provided image. Extract all readable content
                            and present it in a structured JSON format that is clear, concise, and
                            well-organized. Ensure the response has nothing apart the JSON object.""",
                'images': [image_bytes]
            }]
        )

        retry_count = 0
        while True:
            try:
                print (f"retry_count: {retry_count}")
                gemma_response = remove_code_block_delimiters(response.message.content)
                gemma_response = json.loads(gemma_response)
                return {"extracted_json": gemma_response}
            except Exception as inner_api_error:
                print ("exception caught")
                exception_type, _, exception_traceback = sys.exc_info()
                filename = exception_traceback.tb_frame.f_code.co_filename
                line_number = exception_traceback.tb_lineno
                logger.error("%s||||%s||||%d||||%d", exception_type, filename, line_number, inner_api_error)    # pylint: disable=line-too-long
                retry_count+=1
                if retry_count>2:
                    return {"extracted_json": f"failed after {retry_count} tries with error: {inner_api_error}, exception_type: {exception_type}, filename: {filename}, line_number: {line_number}"}
    
    except Exception as api_error:
        print ("exception caught")
        exception_type, _, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        logger.error("%s||||%s||||%d||||%d", exception_type, filename, line_number, api_error)    # pylint: disable=line-too-long
        raise HTTPException(status_code=500, detail=f"Error processing image: {exception_type}||||{filename}||||{line_number}||||{api_error}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
import os
import tempfile
import uuid
import logging
from pydantic import BaseModel
import subprocess

# Import the conversion module
from document_converter import convert_document

app = FastAPI(title="Universal Document Converter API")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/doc_converter/uploads")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/tmp/doc_converter/output")
LIBREOFFICE_HOST = os.environ.get("LIBREOFFICE_HOST", "localhost")
LIBREOFFICE_PORT = int(os.environ.get("LIBREOFFICE_PORT", "2002"))

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define supported conversion formats
SUPPORTED_FORMATS = {
    "pdf": "writer_pdf_Export",
    "docx": "MS Word 2007 XML",
    "odt": "writer8",
    "xlsx": "Calc MS Excel 2007 XML",
    "ods": "calc8",
    "pptx": "Impress MS PowerPoint 2007 XML",
    "odp": "impress8",
    # Add more formats as needed
}

class ConversionRequest(BaseModel):
    output_format: str

@app.get("/")
async def root():
    return {"message": "Universal Document Converter API"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Check if LibreOffice service is running
        result = subprocess.run(
            ["pgrep", "-f", "soffice.*--accept"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        if result.returncode != 0:
            raise HTTPException(status_code=503, detail="LibreOffice service not running")
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/convert/")
async def convert_file(
    file: UploadFile = File(...),
    output_format: str = None,
    background_tasks: BackgroundTasks = None
):
    """
    Convert an uploaded document to the specified format
    """
    # Validate output format
    if output_format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported output format. Supported formats: {', '.join(SUPPORTED_FORMATS.keys())}"
        )
    
    # Generate unique filenames
    file_id = str(uuid.uuid4())
    input_filename = file.filename
    output_filename = f"{os.path.splitext(input_filename)[0]}.{output_format}"
    
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{input_filename}")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_{output_filename}")
    
    # Save uploaded file
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Error saving uploaded file")
    
    # Convert document
    try:
        export_filter = SUPPORTED_FORMATS[output_format]
        convert_document(
            input_path, 
            output_path, 
            export_filter,
            host=LIBREOFFICE_HOST,
            port=LIBREOFFICE_PORT
        )
    except Exception as e:
        logger.error(f"Error converting document: {e}")
        # Clean up the input file
        if os.path.exists(input_path):
            os.remove(input_path)
        raise HTTPException(status_code=500, detail=f"Error converting document: {str(e)}")
    
    # Add cleanup task
    if background_tasks:
        background_tasks.add_task(cleanup_files, input_path, output_path)
    
    # Return the converted file
    return FileResponse(
        output_path, 
        filename=output_filename,
        background=background_tasks is None  # Only delete after sending if no background tasks
    )

def cleanup_files(input_path, output_path, delay=300):
    """Clean up temporary files after a delay to ensure the file has been sent"""
    import time
    try:
        # Remove input file immediately
        if os.path.exists(input_path):
            os.remove(input_path)
            
        # Keep output file for a while in case it needs to be re-downloaded
        time.sleep(delay)  # Wait for 5 minutes
        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")

if __name__ == "__main__":
    import uvicorn
    # Start the API server
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

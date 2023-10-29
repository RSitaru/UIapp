import os
import time
import threading
import logging
from speechmatics.batch_client import BatchClient
from docx import Document

# Logging setup
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
logger = logging.getLogger(__name__)

SPEECHMATICS_API_KEY = os.environ.get("SPEECHMATICS_KEY")
ALLOWED_EXTENSIONS_AUDIO = {'wav', 'mp3'}

def allowed_audio_file(filename, allowed_extensions=ALLOWED_EXTENSIONS_AUDIO):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def transcribe_audio_threaded(file_path, callback, progress_callback):
    logger.info(f"Starting transcription for {file_path} in a new thread.")
    
    def thread_target():
        result = transcribe_audio(file_path, progress_callback)
        callback(result)  # Notifying the main window once transcription is completed

    threading.Thread(target=thread_target).start()

def transcribe_audio(file_path, progress_callback):
    if not allowed_audio_file(file_path):
        logger.error("Invalid file type.")
        return 'Invalid file type'

    try:
        with open(file_path, 'rb') as f:
            response_content = process_audio(f, os.path.basename(file_path), progress_callback)
        return os.path.basename(file_path), response_content
    except Exception as e:
        logger.error(f"Error processing the audio file: {str(e)}")
        return f"Error processing the audio file: {str(e)}"

def process_audio(file, filename, progress_callback):  
    logger.info(f"Starting the audio processing for {filename}.")

    # Create a transcription configuration with Romanian language
    transcription_config = {
        "type": "transcription",
        "transcription_config": {"language": "ro"}
    }

    try:
        with BatchClient(SPEECHMATICS_API_KEY) as client:
            job_id = client.submit_job(
                audio=file.name,
                transcription_config=transcription_config
            )

            logger.info(f"Job submitted with ID: {job_id}")
            
            # Set the status to yellow right after submitting the job
            progress_callback("submitted")

            for i in range(60):  
                time.sleep(10)
                job_response = client.check_job_status(str(job_id))

                if job_response.get("job", {}).get("status") == "done":
                    progress_callback("done")  # Notify when the job is done
                    break
            else:
                logger.warning("Transcription took too long.")
                return "Transcription took too long. Please try again later."

            transcript = client.get_job_result(str(job_id))
            full_transcription = " ".join(result["alternatives"][0]["content"] for result in transcript["results"])

            base_filename = os.path.splitext(filename)[0]
            downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
            output_path = os.path.join(downloads_path, f"Transcript_{base_filename}.docx")

            doc = Document()
            doc.add_paragraph(full_transcription)
            doc.save(output_path)

            logger.info(f"Transcription completed for {filename}.")
            return f"Transcription Result for {filename} saved at {output_path}"

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"


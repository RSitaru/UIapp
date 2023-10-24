import os
import tempfile
import time
import threading
from speechmatics.batch_client import BatchClient

# Speechmatics configuration
SPEECHMATICS_API_KEY = os.getenv("SPEECHMATICS_API_KEY")

ALLOWED_EXTENSIONS_AUDIO = {'wav', 'mp3'}

def allowed_audio_file(filename, allowed_extensions=ALLOWED_EXTENSIONS_AUDIO):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def transcribe_audio_threaded(file_path, callback, progress_callback):
    """
    Starts the transcription in a new thread and uses a callback to return the results.
    """
    def thread_target():
        result = transcribe_audio(file_path, progress_callback)
        callback(result)

    threading.Thread(target=thread_target).start()

def transcribe_audio(file_path, progress_callback):
    if not allowed_audio_file(file_path):
        return 'Invalid file type'

    try:
        with open(file_path, 'rb') as f:
            response_content = process_audio(f, os.path.basename(file_path), progress_callback)
        return response_content
    except Exception as e:
        return f"Error processing the audio file: {str(e)}"

def process_audio(file, filename, progress_callback):
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.rsplit('.', 1)[1]}") as temp_audio:
        temp_audio.write(file.read())

        with BatchClient(SPEECHMATICS_API_KEY) as client:
            # Create new job with Romanian language code
            transcription_config = {
                "type": "transcription",
                "transcription_config": {"language": "ro"}}

            job_id = client.submit_job(
                audio=temp_audio.name,
                transcription_config=transcription_config
            )

            for i in range(10):  # Checking the status 10 times over a minute
                time.sleep(6)
                progress_callback(i * 10)  # Send progress: 0, 10, 20, ... , 90
                job_response = client.check_job_status(str(job_id))
                if job_response.get("job", {}).get("status") == "done":
                    break
            else:
                return "Transcription took too long. Please try again later."

            transcript = client.get_job_result(str(job_id))

    full_transcription = " ".join(result["alternatives"][0]["content"] for result in transcript["results"])
    return f"Transcription Result for {filename}:\n\n{full_transcription}"

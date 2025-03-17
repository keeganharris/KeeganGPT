import openai
import time
import os
import dotenv
from datetime import datetime

# Load API key
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client
client = openai.OpenAI(api_key=api_key)

# Set the last training day
day = "Sunday"  # Change this to match the latest training day

# Paths with dynamic day names
TRAINING_FILE_PATH = f"/Users/keeganh/Documents/keegangpt_training_{day}.jsonl"
LOG_FILE = f"/Users/keeganh/Documents/fine_tuning_log_{day}.txt"

def log_fine_tuning_details(job_id, model_id=None, status="started"):
    """Logs fine-tuning details into a text file."""
    with open(LOG_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Job ID: {job_id}\n")
        f.write(f"Status: {status}\n")
        if model_id:
            f.write(f"Fine-Tuned Model ID: {model_id}\n")
        f.write("=" * 40 + "\n")
    print(f"Fine-tuning details logged in {LOG_FILE}")

def upload_training_file():
    """Uploads the training JSONL file and returns the file ID."""
    print(f"Uploading training file: {TRAINING_FILE_PATH}")

    try:
        with open(TRAINING_FILE_PATH, "rb") as f:
            response = client.files.create(
                file=f,
                purpose="fine-tune"
            )
        file_id = response.id
        print(f"Training file uploaded! File ID: {file_id}")
        return file_id
    except openai.OpenAIError as e:
        print(f"Error uploading training file: {e}")
        return None

def start_fine_tuning(file_id):
    """Starts a fine-tuning job and returns the job ID."""
    print(f"Starting fine-tuning job for {day}...")

    try:
        response = client.fine_tuning.jobs.create(
            training_file=file_id,
            model="gpt-4o-mini-2024-07-18"
        )
        job_id = response.id
        print(f"Fine-tuning started! Job ID: {job_id}")

        # Log initial details
        log_fine_tuning_details(job_id, status="started")

        return job_id
    except openai.OpenAIError as e:
        print(f"Error starting fine-tuning: {e}")
        return None

def check_fine_tuning_status(job_id):
    """Monitors the fine-tuning job until completion and logs the result."""
    print(f"Monitoring fine-tuning job: {job_id}")

    while True:
        try:
            job_status = client.fine_tuning.jobs.retrieve(job_id)

            # Print status update
            print(f"Status: {job_status.status}")

            if job_status.status == "succeeded":
                model_id = job_status.fine_tuned_model
                print(f"Fine-tuning complete! Model ID: {model_id}")

                # Log completion details
                log_fine_tuning_details(job_id, model_id, status="completed")

                return model_id
            elif job_status.status in ["failed", "cancelled"]:
                print("Fine-tuning failed or was cancelled.")

                # Log failure
                log_fine_tuning_details(job_id, status="failed")

                return None

            # Wait before checking again
            time.sleep(60)

        except openai.OpenAIError as e:
            print(f"Error checking fine-tuning status: {e}")
            return None

# Run fine-tuning process
if __name__ == "__main__":
    file_id = upload_training_file()
    if file_id:
        job_id = start_fine_tuning(file_id)
        if job_id:
            fine_tuned_model = check_fine_tuning_status(job_id)
            if fine_tuned_model:
                print(f"Your fine-tuned model is ready: {fine_tuned_model}")
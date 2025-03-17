import openai
from openai import OpenAIError  # Import OpenAIError for handling exceptions
import os
import base64
import time
import dotenv
from tqdm import tqdm

# Load API Key from .env file
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client (New API format)
client = openai.OpenAI(api_key=api_key)

# Function to encode an image as base64
def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

# Function to generate a summary using gpt-4o-mini
def generate_summary(image_path, max_tokens=150):
    """Generates a 3-4 sentence summary for an image."""
    encoded_image = encode_image(image_path)

    prompt = "Describe this image in 3-4 sentences, focusing on details and context."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI trained to generate detailed descriptions of first-person images. These images are generated from a person named Keegan wearing a head-mounted camcorder."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                ]}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    except OpenAIError as e:
        print(f"⚠️ Error processing {image_path}: {e}")
        return "Error generating summary"

# Function to process all images in a folder and save each summary separately
def process_images(image_folder):
    """Processes all images in a folder and saves each summary in a text file."""
    output_folder = os.path.join(os.path.dirname(image_folder), "raw_summaries")
    os.makedirs(output_folder, exist_ok=True)

    image_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    print(f"Found {len(image_files)} images in '{image_folder}'. Processing...")

    for img_file in tqdm(image_files, desc="Processing Images"):
        img_path = os.path.join(image_folder, img_file)

        # Generate a text summary
        summary = generate_summary(img_path)

        # Save the summary in text_summaries/ with the same name as the image
        summary_filename = os.path.join(output_folder, f"{os.path.splitext(img_file)[0]}.txt")
        with open(summary_filename, "w") as f:
            f.write(summary)

        print(f"Summary saved: {summary_filename}")

        # Respect API rate limits (adjust delay as needed)
        time.sleep(1.5)

    print(f"All summaries saved in '{output_folder}/'")

# Run the script
if __name__ == "__main__":
    image_folder = "/Users/keeganh/Documents/Sunday/extracted_frames"
    process_images(image_folder)
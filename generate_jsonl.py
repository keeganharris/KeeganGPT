import os
import json
from datetime import datetime

# Define main directory (update this path)
main_directory = "/Users/keeganh/Documents"

# List of days to process
days_to_process = ["Sunday", "Monday"]

minute = True  # Set to True to include minute summaries

# Output JSONL file for fine-tuning
if minute:
    output_jsonl_file = os.path.join(main_directory, f"keegangpt_training_minute_{days_to_process[-1]}.jsonl")
else:
    output_jsonl_file = os.path.join(main_directory, f"keegangpt_training_{days_to_process[-1]}.jsonl")

def read_text_file(filepath):
    """Reads text content from a file."""
    with open(filepath, "r") as f:
        return f.read().strip()

def extract_summaries(summary_folder, question_format, summary_type):
    """Extracts summaries from a given folder and structures them as JSONL entries."""
    training_data = []

    if not os.path.exists(summary_folder):
        print(f"Skipping missing folder: {summary_folder}")
        return []

    for filename in sorted(os.listdir(summary_folder)):
        if filename.endswith(".txt"):
            filepath = os.path.join(summary_folder, filename)
            summary = read_text_file(filepath)
            
            try:
                timestamp = datetime.strptime(filename[:-4], "%Y-%m-%d_%H-%M-%S")
            except ValueError:
                print(f"Skipping invalid file: {filename}")
                continue

            question = question_format.format(
                time=timestamp.strftime("%I:%M %p"),
                date=timestamp.strftime("%B %d, %Y"),
                day=timestamp.strftime("%A")
            )

            training_data.append({
                "messages": [
                    {"role": "system", "content": f"You are KeeganGPT, trained on Keegan's personal {summary_type} summaries. Answer questions accurately based on past events."},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": summary}
                ]
            })

    return training_data

def extract_ten_minute_summaries():
    """Extracts 10-minute summaries for fine-tuning."""
    training_data = []
    for day in days_to_process:
        summary_folder = os.path.join(main_directory, day, "ten_minute_summaries")
        training_data += extract_summaries(
            summary_folder,
            "What was Keegan doing around {time} on {day}, {date}?",
            "10-minute"
        )
    return training_data

def extract_minute_summaries():
    """Extracts minute summaries for fine-tuning."""
    training_data = []
    for day in days_to_process:
        summary_folder = os.path.join(main_directory, day, "minute_summaries")
        training_data += extract_summaries(
            summary_folder,
            "What was Keegan doing at exactly {time} on {day}, {date}?",
            "minute"
        )
    return training_data

def extract_hourly_summaries():
    """Extracts hourly summaries for fine-tuning."""
    training_data = []
    for day in days_to_process:
        summary_folder = os.path.join(main_directory, day, "hour_summaries")
        training_data += extract_summaries(
            summary_folder,
            "Summarize Keegan's main activities between {time} and {time} on {day}, {date}.",
            "hourly"
        )
    return training_data

def extract_daily_summaries():
    """Extracts daily summaries for fine-tuning."""
    training_data = []
    summary_folder = os.path.join(main_directory, "day_summaries")

    if not os.path.exists(summary_folder):
        print(f"No day_summaries folder found.")
        return []

    for filename in sorted(os.listdir(summary_folder)):
        if filename.endswith(".txt"):
            filepath = os.path.join(summary_folder, filename)
            summary = read_text_file(filepath)
            day_name = os.path.splitext(filename)[0]  # Extract "Sunday", "Monday", etc.

            training_data.append({
                "messages": [
                    {"role": "system", "content": "You are KeeganGPT, trained on Keegan's daily summaries. Answer questions about past events."},
                    {"role": "user", "content": f"Summarize what Keegan did on {day_name}."},
                    {"role": "assistant", "content": summary}
                ]
            })

    return training_data

def save_jsonl(data, output_path):
    """Saves data in JSONL format."""
    with open(output_path, "w") as f:
        for entry in data:
            json.dump(entry, f)
            f.write("\n")

    print(f"JSONL file saved: {output_path}")

# Run extraction process
ten_minute_data = extract_ten_minute_summaries()
hourly_data = extract_hourly_summaries()
daily_data = extract_daily_summaries()

if minute:
    minute_data = extract_minute_summaries()
else:
    minute_data = []

# Combine all data (excluding weekly summaries)
all_data = ten_minute_data + hourly_data + daily_data + minute_data
print(len(all_data))
# Save to JSONL file
save_jsonl(all_data, output_jsonl_file)
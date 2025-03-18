import os
import openai
import dotenv
from datetime import datetime, timedelta

# Load API Key from .env file
dotenv.load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client
client = openai.OpenAI(api_key=api_key)

# Function to read summaries from a folder
def read_summaries(folder):
    summaries = []
    timestamps = []

    for filename in sorted(os.listdir(folder)):  # Ensure chronological order
        if filename.endswith(".txt"):
            timestamp_str = os.path.splitext(filename)[0]
            try:
                # Try to parse filenames with timestamps
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")
            except ValueError:
                # If filename is a named summary (like "Sunday.txt"), use a default timestamp
                timestamp = datetime.min  # Assign a dummy timestamp so sorting works
                
            timestamps.append(timestamp)
            with open(os.path.join(folder, filename), "r") as f:
                summaries.append((timestamp, f.read()))

    return timestamps, summaries

# Function to send summaries to GPT-4o-mini
def summarize_text(text_list, timestamps, summary_type):
    """Summarizes a list of text entries into a coherent summary with timestamps."""
    entries = "\n".join([f"[{timestamps[i].strftime('%Y-%m-%d %H:%M:%S')}]\n{text}" for i, text in enumerate(text_list)])

    if summary_type == "minute":
        prompt = f"You are summarizing short text logs with timestamps, which are summaries of what a person named Keegan was doing at the given timestamp. Generate a summary for the following minute-long logs:\n\n{entries}"
    elif summary_type == "ten_minute":
        prompt = f"You are summarizing a sequence of minute summaries over a 10-minute period. These are summaries of what Keegan was doing. Preserve key trends:\n\n{entries}"
    elif summary_type == "hour":
        prompt = f"You are summarizing a sequence of ten-minute summaries over an hour. These are summaries of what Keegan was doing. Preserve key trends over time:\n\n{entries}"
    elif summary_type == "day":
        prompt = f"You are summarizing a sequence of hourly summaries over a day. These are summaries of what Keegan was doing in that hour. Identify patterns, trends, and key highlights:\n\n{entries}"
    elif summary_type == "week":
        prompt = f"You are summarizing a week's worth of daily summaries of a person named Keegan. Extract key themes and trends while maintaining chronological context:\n\n{entries}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Error generating summary."

# Function to process summaries into time-based chunks
def process_summaries(input_folder, output_folder, interval_minutes, summary_type):
    """Groups text files into time-based intervals and summarizes them."""
    if not os.path.exists(input_folder):
        print(f"Skipping missing folder: {input_folder}")
        return

    timestamps, summaries = read_summaries(input_folder)

    os.makedirs(output_folder, exist_ok=True)

    grouped_summaries = []
    grouped_timestamps = []
    current_group = []
    current_timestamps = []
    current_start_time = None

    for timestamp, text in summaries:
        if current_start_time is None:
            current_start_time = timestamp

        # If new interval, summarize the previous group
        if timestamp >= current_start_time + timedelta(minutes=interval_minutes):
            # Summarize last group OR copy directly if it's already spaced by a minute
            if current_group:
                summary_filename = os.path.join(output_folder, f"{current_start_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt")

                # If there's exactly 1 summary in this group, just copy it (avoid unnecessary API calls)
                if len(current_group) == 1:
                    with open(summary_filename, "w") as f:
                        f.write(current_group[0])
                    print(f"Copied summary without modification: {summary_filename}")
                else:
                    summarized_text = summarize_text(current_group, grouped_timestamps, summary_type)
                    with open(summary_filename, "w") as f:
                        f.write(summarized_text)
                    print(f"Saved summarized text: {summary_filename}")

            current_group = []
            grouped_timestamps = []
            current_start_time = timestamp

        current_group.append(text)
        grouped_timestamps.append(timestamp)

    # Summarize last group
    if current_group:
        summarized_text = summarize_text(current_group, grouped_timestamps, summary_type)
        summary_filename = os.path.join(output_folder, f"{current_start_time.strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        with open(summary_filename, "w") as f:
            f.write(summarized_text)
        print(f"Saved summary: {summary_filename}")

# Generate minute summaries (inside each day's directory)
def generate_minute_summaries(main_directory, days):
    for day in days:
        day_dir = os.path.join(main_directory, day)
        raw_summaries = os.path.join(day_dir, "raw_summaries")
        minute_summaries = os.path.join(day_dir, "minute_summaries")
        process_summaries(raw_summaries, minute_summaries, interval_minutes=1, summary_type="minute")

# Generate ten-minute summaries (inside each day's directory)
def generate_ten_minute_summaries(main_directory, days):
    for day in days:
        day_dir = os.path.join(main_directory, day)
        minute_summaries = os.path.join(day_dir, "minute_summaries")
        ten_minute_summaries = os.path.join(day_dir, "ten_minute_summaries")
        process_summaries(minute_summaries, ten_minute_summaries, interval_minutes=10, summary_type="ten_minute")

# Generate hour summaries (inside each day's directory)
def generate_hour_summaries(main_directory, days):
    for day in days:
        day_dir = os.path.join(main_directory, day)
        ten_minute_summaries = os.path.join(day_dir, "ten_minute_summaries")
        hour_summaries = os.path.join(day_dir, "hour_summaries")
        process_summaries(ten_minute_summaries, hour_summaries, interval_minutes=60, summary_type="hour")

# Generate day summaries (saved in main_directory)
def generate_day_summaries(main_directory, days):
    day_summaries_dir = os.path.join(main_directory, "day_summaries")
    os.makedirs(day_summaries_dir, exist_ok=True)

    for day in days:
        day_dir = os.path.join(main_directory, day)
        hour_summaries = os.path.join(day_dir, "hour_summaries")

        if not os.path.exists(hour_summaries):
            print(f"No hour summaries found for {day}, skipping.")
            continue

        timestamps, summaries = read_summaries(hour_summaries)
        if not summaries:
            continue

        day_summary_text = summarize_text([text for _, text in summaries], timestamps, summary_type="day")
        summary_filename = os.path.join(day_summaries_dir, f"{day}.txt")

        with open(summary_filename, "w") as f:
            f.write(day_summary_text)

        print(f"Day summary saved: {summary_filename}")

# Run the script
if __name__ == "__main__":
    main_directory = "/Users/keeganh/Documents"
    days_to_summarize = ["Monday"]  # Days to process

    print("Generating minute summaries...")
    generate_minute_summaries(main_directory, days_to_summarize)

    print("Generating ten-minute summaries...")
    generate_ten_minute_summaries(main_directory, days_to_summarize)

    print("Generating hour summaries...")
    generate_hour_summaries(main_directory, days_to_summarize)

    print("Generating day summaries...")
    generate_day_summaries(main_directory, days_to_summarize)

    print("Summarization pipeline completed!")
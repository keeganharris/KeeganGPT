import os
import glob
import cv2
from datetime import datetime, timedelta

def get_sorted_videos(directory):
    """Retrieve and sort videos by their true creation time."""
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return []

    # Get all MP4 files (case insensitive)
    video_files = glob.glob(os.path.join(directory, "*.mp4")) + glob.glob(os.path.join(directory, "*.MP4"))

    if not video_files:
        print(f"Warning: No MP4 files found in '{directory}'.")

    # Sort by true creation time
    video_files.sort(key=lambda x: os.stat(x).st_birthtime)

    return video_files

def extract_frames(video_path, output_dir, interval_seconds=60):
    """ Extracts a frame every `interval_seconds` from the given video with accurate timestamps in filenames. """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps  # Duration in seconds

    os.makedirs(output_dir, exist_ok=True)

    # Get video creation timestamp
    video_creation_time = datetime.fromtimestamp(os.stat(video_path).st_birthtime)

    for t in range(0, int(duration), interval_seconds):
        frame_number = int(t * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = cap.read()
        if success:
            # Calculate the exact timestamp of this frame
            frame_timestamp = video_creation_time + timedelta(seconds=t)
            formatted_timestamp = frame_timestamp.strftime("%Y-%m-%d_%H-%M-%S")

            # Save frame with only timestamp in the filename
            frame_filename = os.path.join(output_dir, f"{formatted_timestamp}.jpg")
            cv2.imwrite(frame_filename, frame)

    cap.release()

def process_videos(directory, interval_seconds=60):
    """Processes all videos in a directory, extracting frames at a set interval."""
    video_files = get_sorted_videos(directory)
    print(f"Found {len(video_files)} video(s) in '{directory}'.")

    output_folder = os.path.join(directory, "extracted_frames")  # Single output folder for all frames
    os.makedirs(output_folder, exist_ok=True)

    for video in video_files:
        print(f"Processing: {video}")
        extract_frames(video, output_folder, interval_seconds)

    print(f"All frames extracted and saved inside '{output_folder}'")

if __name__ == "__main__":
    N = 30  # Extract an image every N seconds
    day_list = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday 2", "Sunday 2"]
    for day in day_list:
        video_directory = f"/Users/keeganh/Documents/{day}"
        process_videos(video_directory, interval_seconds=N)
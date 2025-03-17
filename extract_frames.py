import os
import glob
import cv2
from datetime import datetime

def get_sorted_videos(directory):
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return []

    # Get all MP4 files
    video_files = glob.glob(os.path.join(directory, "*.mp4")) + glob.glob(os.path.join(directory, "*.MP4"))

    if not video_files:
        print(f"Warning: No MP4 files found in '{directory}'.")

    # Sort by true creation time
    video_files.sort(key=lambda x: os.stat(x).st_birthtime)

    return video_files

def extract_frames(video_path, output_dir, interval_seconds=60):
    """ Extracts a frame every `interval_seconds` from the given video. """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    os.makedirs(output_dir, exist_ok=True)

    video_name = os.path.splitext(os.path.basename(video_path))[0]  # Get video filename without extension

    for t in range(0, int(duration), interval_seconds):
        frame_number = int(t * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        success, frame = cap.read()
        if success:
            timestamp = datetime.fromtimestamp(os.stat(video_path).st_birthtime).strftime("%Y-%m-%d_%H-%M-%S")
            frame_filename = os.path.join(output_dir, f"{timestamp}_{video_name}_frame_{t:05d}.jpg")
            cv2.imwrite(frame_filename, frame)

    cap.release()

def process_videos(directory, interval_seconds=60):
    video_files = get_sorted_videos(directory)
    print(f"Found {len(video_files)} video(s) in '{directory}'.")

    output_folder = os.path.join(directory, "extracted_frames")  # Single output folder for all frames
    os.makedirs(output_folder, exist_ok=True)

    for video in video_files:
        print(f"Processing: {video}")
        extract_frames(video, output_folder, interval_seconds)

    print(f"All frames extracted and saved inside '{output_folder}'")


if __name__=="__main__":
    N = 10  # Extract an image every N seconds
    video_directory = "/Users/keeganh/Documents/Sunday"
    process_videos(video_directory, interval_seconds=N)
import cv2
import os
import time
import subprocess
from collections import Counter
from vision.vision import vision_model


def extract_frames(video_path, num_frames=3):
    # Open the video file for reading
    cap = cv2.VideoCapture(video_path)

    # Get total number of frames in the video
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # If video metadata is invalid or unreadable, return empty list
    if total <= 0:
        cap.release()
        return []

    # Define fixed key frame positions (early, middle, late)
    # These ratios provide basic temporal coverage of the video
    ratios = [0.2, 0.5, 0.8]

    # Convert ratios into actual frame indices
    # Ensure indices do not exceed total frame count
    indices = [int(total * r) for r in ratios if int(total * r) < total]

    frames = []

    for i, idx in enumerate(indices):
        # Move the video pointer to the selected frame index
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)

        # Read the frame at that position
        ret, frame = cap.read()

        if ret:
            # Resize frame to reduce processing cost for the vision model
            frame = cv2.resize(frame, (640, 480))

            # Save frame temporarily to disk
            path = f"/tmp/frame_{i}.jpg"

            # Save with compression to reduce file size and I/O overhead
            cv2.imwrite(path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])

            # Store the path for later processing
            frames.append(path)

    # Release video resource
    cap.release()

    # Return list of saved frame paths
    return frames



def convert_to_mp4(video_path):
    # Skip conversion if already MP4
    if video_path.endswith(".mp4"):
        return video_path

    # Replace extension
    mp4_path = video_path.replace(".h264", ".mp4")

    # If converted file already exists, reuse it
    if os.path.exists(mp4_path):
        return mp4_path

    try:
        # Convert raw H264 stream to MP4 container using ffmpeg
        subprocess.run([
            "ffmpeg", "-y",

            # Reduced FPS for smaller file and faster processing
            "-framerate", "12",

            "-i", video_path,

            # Reduce resolution while keeping aspect ratio
            "-vf", "scale=640:-2",

            "-c:v", "libx264",

            # Compression level (higher = smaller file, lower quality)
            "-crf", "28",

            "-pix_fmt", "yuv420p",
            mp4_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Return path only if conversion succeeded
        return mp4_path if os.path.exists(mp4_path) else None

    except:
        return None


def describe_video(video_path):
    print(f"[VIDEO] input: {video_path}")

    # Ensure video is in compatible format
    video_path = convert_to_mp4(video_path)

    if not video_path or not os.path.exists(video_path):
        return None

    print(f"[VIDEO] converted: {video_path}")

    # Extract representative frames for analysis
    frames = extract_frames(video_path, num_frames=3)

    if not frames:
        return None

    print(f"[VIDEO] frames extracted: {len(frames)}")

    captions = []

    # Global timeout to prevent long processing
    start_time = time.time()

    for frame in frames:
        # Hard time limit (prevents slow vision model from blocking system)
        if time.time() - start_time > 20:
            print("[VIDEO] early stop: timeout")
            break

        try:
            # Run vision model on each frame
            cap = vision_model.describe(frame)
            cap = cap.lower()

            print("[VIDEO] caption:", cap)

            captions.append(cap)

            # Early exit if strong semantic signal detected
            if any(x in cap for x in [
                "person", "man", "woman",
                "laptop", "computer",
                "phone", "screen"
            ]):
                print("[VIDEO] early stop: strong signal found")
                break

        except Exception as e:
            print("[VIDEO] frame error:", e)

        # Remove temporary frame file to avoid disk buildup
        try:
            os.remove(frame)
        except:
            pass

    if not captions:
        return None

    # Find most common caption
    most_common = Counter(captions).most_common(1)[0][0]

    # Try to find additional useful detail
    extra_detail = None
    base_words = set(most_common.split())

    for cap in captions:
        if cap == most_common:
            continue

        words = set(cap.split())
        new_words = words - base_words

        # Only keep meaningful additions
        if len(new_words) >= 2:
            extra_detail = " ".join(new_words)
            break

    # Final output
    if extra_detail:
        return f"{most_common} with {extra_detail}"
    else:
        return most_common

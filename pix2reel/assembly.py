import requests
import subprocess
import os
import shutil
import logging
from typing import List

if logger is None:
    logger = logging.getLogger(__name__)

def run_reel_assembly(
    images: List[str], 
    texts: List[str], 
    audio_file: str = None, 
    output_video: str = "output_video.mp4", 
    segment_durations: List[float] = None,
    mode: str = "directory"
):
    """
    Generate a reel video from images with text overlays and background audio.
    
    Args:
        images (List[str]): Paths to input images
        texts (List[str]): Shortened text captions for each image
        audio_file (str): Path to background audio file
        output_video (str): Path for output video
        segment_durations (List[float], optional): Custom timing for each image. Defaults to None.
        mode (str): can be directory or url. If it's url then there will be a download steps.
    
    Raises:
        ValueError: If inputs are invalid
        subprocess.CalledProcessError: If FFmpeg command fails
    """
    if mode == "url":
        final_images = []
        # Temporary directory to store images
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)

        # Download images
        for i, url in enumerate(images):
            logger.info("Downloading :", url)
            response = requests.get(url)
            final_images.append(os.path.join(temp_dir, f"image_{i}.jpg"))
            with open(os.path.join(temp_dir, f"image_{i}.jpg"), "wb") as f:
                f.write(response.content)
            logger.info("Downloaded :", url)

        images = final_images

    # Validate inputs
    if len(images) != len(texts):
        raise ValueError("Number of images must match number of texts")
    
    if not all(os.path.exists(img) for img in images):
        raise FileNotFoundError("One or more image files do not exist")
    
    if audio_file:
        if not os.path.exists(audio_file):
            audio_file = None
            logger.info("Use silent audio background because cannot file audio file")
    
    # If no custom timings, generate default
    if segment_durations is None:
        base_duration = 3.0  # 3 seconds per image
        segment_durations = [0.0] + [base_duration * (i+1) for i in range(len(images))]

    # If segment durations is not the same length as images, raise error or truncate it
    if len(segment_durations) < len(images) + 1:
        raise ValueError("Number of segment durations must be equal to number of images + 1")
    elif len(segment_durations) > len(images) + 1:
        segment_durations = segment_durations[:len(images)+1]
    
    # Generate FFmpeg command
    command = _assemble_ffmpeg_commands(images, texts, audio_file, output_video, segment_durations)
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Reel generated successfully: {output_video}")
        if (mode == "url") & os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except subprocess.CalledProcessError as e:
        error_message = f"Error generating reel: {e.stderr}"
        print(error_message)
        if (mode == "url") & (os.path.exists(temp_dir)):
            shutil.rmtree(temp_dir)
        raise RuntimeError(error_message) from e


def _assemble_ffmpeg_commands(
    images, texts, audio_file, output_video, segment_durations
) -> List[str]:
    """Assemble FFmpeg command for reel generation."""
    # Add background before first image
    command = [
        "ffmpeg",
        "-f", "lavfi", "-i", f"color=color=black:size=1080x1920:duration={segment_durations[0]}",
    ]

    # Build the input command for the images
    for i in range(len(images)):
        command.extend([
            "-loop", "1",
            "-t", f"{segment_durations[i + 1] - segment_durations[i]}",
            "-i", images[i]
        ])
    if audio_file:
        # Input the audio file
        command.extend([
            "-i", audio_file
        ])
    else:
        # Use silent audio background
        command.extend([
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"
        ])

    # Generate filter complex string
    filter_complex_str = _generate_filter_complex_string(texts, images, segment_durations)

    # Complete the command
    command.extend([
        "-filter_complex", filter_complex_str,
        "-map", "[outv]",
        "-map", "[outa]",
        "-c:v", "libx264",
        "-c:a", "aac",
        '-shortest', # For truncating the excess audio
        '-y',  # Overwrite output file without confirmation
        output_video
    ])

    return command

def _generate_filter_complex_string(
    texts: List[str], 
    images: List[str], 
    segment_durations: List[float], 
):
    """Generate FFmpeg filter complex string for video composition."""
    filter_complex_string = "[0:v]setsar=1[empty];"

    # Generate the strings using a for loop
    for i in range(len(texts)):
        filter_complex_string += (
            f"[{i + 1}:v]scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,setsar=1,format=yuv420p,"
            f"drawtext=text='{texts[i]}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h-th-50:"
            f"shadowcolor=black:shadowx=2:shadowy=2[img{i + 1}];"
        )

    # Concat the filtered images together
    filter_complex_string += "[empty]"
    for i in range(len(images)):
        filter_complex_string += f"[img{i+1}]"
    filter_complex_string += f"concat=n={len(images)+1}:v=1:a=0[outv];"

    # Concat the audio file filter
    filter_complex_string += f"[{len(images)+1}:a]atrim=duration={segment_durations[-1]},volume=0.8[outa]"
    return filter_complex_string

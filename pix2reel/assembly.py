import subprocess
import os
from typing import List

def run_reel_assembly(
    images: List[str], 
    texts: List[str], 
    audio_file: str, 
    output_video: str, 
    segment_durations: List[float] = None
):
    """
    Generate a reel video from images with text overlays and background audio.
    
    Args:
        images (List[str]): Paths to input images
        texts (List[str]): Shortened text captions for each image
        audio_file (str): Path to background audio file
        output_video (str): Path for output video
        segment_durations (List[float], optional): Custom timing for each image. Defaults to None.
    
    Raises:
        ValueError: If inputs are invalid
        subprocess.CalledProcessError: If FFmpeg command fails
    """
    # Validate inputs
    if len(images) != len(texts):
        raise ValueError("Number of images must match number of texts")
    
    if not all(os.path.exists(img) for img in images):
        raise FileNotFoundError("One or more image files do not exist")
    
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file {audio_file} not found")
    
    # If no custom timings, generate default
    if segment_durations is None:
        base_duration = 3.0  # 3 seconds per image
        segment_durations = [0.0] + [base_duration * (i+1) for i in range(len(images))]

    # If segment durations is not the same length as images, raise error
    if len(segment_durations) != len(images) + 1:
        raise ValueError("Number of segment durations must be equal to number of images + 1")
    
    # Generate FFmpeg command
    command = _assemble_ffmpeg_commands(images, texts, audio_file, output_video, segment_durations)
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Reel generated successfully: {output_video}")
    except subprocess.CalledProcessError as e:
        error_message = f"Error generating reel: {e.stderr}"
        print(error_message)
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

    # Input the audio file
    command.extend([
        "-i", audio_file
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

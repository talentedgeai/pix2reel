import librosa

def get_segments_for_music(music_file, amplitude_sensitivity=0.5, time_sentitivity=0.5):
    """
    Detect onset times in a music file to segment audio based on rhythmic changes.
    
    Args:
        music_file (str): Path to the input music file
        amplitude_sensitivity (float, optional): Threshold for detecting onsets. 
            Higher values result in fewer detected onsets. Defaults to 0.5.
        time_sentitivity (float, optional): Controls suppression of closely spaced peaks. 
            Higher values reduce the number of detected onsets. Defaults to 0.5.
    
    Returns:
        List[float]: Timestamps of detected onset points in the music file
    """
    y, sr = librosa.load(music_file)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    # Detect onsets with a higher threshold
    onset_frames = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        onset_envelope=onset_env,
        delta=amplitude_sensitivity,         # Increase for fewer onsets
        pre_max=time_sentitivity*sr/512,         # Increase to suppress closely spaced peaks
        post_max=time_sentitivity*sr/512,
        backtrack=True     # Align onsets to peaks
    )

    # Convert frames to times
    onset_times = librosa.frames_to_time(onset_frames, sr=sr)
    return onset_times
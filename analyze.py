#!/usr/bin/env python3
"""SonicForge — Audio Analysis Module (wraps librosa)"""
import subprocess
import json
import os

def midi_to_wav(midi_path: str, wav_path: str = None, soundfont: str = None) -> str:
    """Convert MIDI to WAV using FluidSynth."""
    if wav_path is None:
        wav_path = midi_path.replace('.mid', '.wav').replace('.midi', '.wav')
    if soundfont is None:
        soundfont = '/usr/share/sounds/sf2/FluidR3_GM.sf2'
    
    cmd = ['fluidsynth', '-ni', soundfont, midi_path, '-F', wav_path, '-r', '44100']
    subprocess.run(cmd, capture_output=True, timeout=60)
    return wav_path

def analyze(wav_path: str) -> dict:
    """Analyze an audio file using librosa."""
    import librosa
    import numpy as np
    
    y, sr = librosa.load(wav_path, sr=22050)
    
    # Tempo
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    tempo_val = float(tempo) if np.isscalar(tempo) else float(tempo[0])
    
    # Key estimation
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)
    key_idx = np.argmax(chroma_mean)
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    key = keys[key_idx]
    
    # Mode detection (major vs minor) via chord templates
    major_template = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
    minor_template = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
    major_corr = np.correlate(chroma_mean, np.roll(major_template, key_idx))
    minor_corr = np.correlate(chroma_mean, np.roll(minor_template, key_idx))
    mode = 'minor' if minor_corr > major_corr else 'major'
    
    # Energy
    rms = librosa.feature.rms(y=y)[0]
    
    # Spectral features
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    flatness = librosa.feature.spectral_flatness(y=y)[0]
    
    # Duration
    duration = librosa.get_duration(y=y, sr=sr)
    
    return {
        'file': os.path.basename(wav_path),
        'duration_sec': round(duration, 2),
        'tempo_bpm': round(tempo_val, 1),
        'key': f"{key} {mode}",
        'energy': {
            'rms_mean': round(float(np.mean(rms)), 4),
            'rms_p95': round(float(np.percentile(rms, 95)), 4),
        },
        'timbre': {
            'brightness': round(float(np.mean(centroid)), 1),
            'rolloff': round(float(np.mean(rolloff)), 1),
            'flatness': round(float(np.mean(flatness)), 4),
        },
        'beat_count': len(beats) if beats is not None else 0,
    }

def full_pipeline(midi_path: str, soundfont: str = None) -> dict:
    """Generate WAV and analyze it."""
    wav_path = midi_to_wav(midi_path, soundfont=soundfont)
    analysis = analyze(wav_path)
    analysis['midi_file'] = midi_path
    analysis['wav_file'] = wav_path
    return analysis

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <file.mid|file.wav>")
        sys.exit(1)
    
    path = sys.argv[1]
    if path.endswith('.mid') or path.endswith('.midi'):
        result = full_pipeline(path)
    else:
        result = analyze(path)
    
    print(json.dumps(result, indent=2))

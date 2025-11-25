#!/usr/bin/env python3
"""
Generate a simple ringtone for Buzzer PWA.
Creates a WAV file that can be converted to MP3.
Requires: pip install pydub (optional, for MP3 conversion)
"""

import wave
import math
import os
import struct
import sys
import io

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def generate_ringtone():
    """Generate a simple ringtone (ascending tones pattern)."""

    audio_dir = "frontend/static/audio"
    os.makedirs(audio_dir, exist_ok=True)

    # Audio parameters
    sample_rate = 44100  # Hz
    duration = 15  # seconds
    num_samples = sample_rate * duration

    # Create the ringtone pattern (ascending notes)
    # Frequencies for a rising tone pattern
    frequencies = [
        (0, 2, 440),      # A4 for 2 seconds
        (2, 1, 554),      # C#5 for 1 second
        (3, 1, 659),      # E5 for 1 second
        (4, 1, 784),      # G5 for 1 second
        (5, 1, 880),      # A5 for 1 second
        (6, 2, 660),      # E5 for 2 seconds (different note)
        (8, 1, 740),      # F#5 for 1 second
        (9, 1, 880),      # A5 for 1 second
        (10, 5, 440),     # A4 for 5 seconds
    ]

    # Generate audio samples
    audio_data = []

    for start_time, duration_seg, frequency in frequencies:
        start_sample = int(start_time * sample_rate)
        end_sample = int((start_time + duration_seg) * sample_rate)

        for i in range(start_sample, end_sample):
            # Generate sine wave
            sample = 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate)

            # Add slight amplitude modulation for more natural sound
            envelope = 1.0
            if i % sample_rate < sample_rate // 10:  # Attack
                envelope = (i % sample_rate) / (sample_rate // 10)
            elif i % sample_rate > sample_rate * 0.9:  # Release
                envelope = 1 - ((i % sample_rate) - sample_rate * 0.9) / (sample_rate // 10)

            sample = sample * envelope
            audio_data.append(int(sample * 32767))

    # Pad to full duration if needed
    while len(audio_data) < num_samples:
        audio_data.append(0)

    # Create WAV file
    wav_file = os.path.join(audio_dir, "ringtone.wav")

    with wave.open(wav_file, 'w') as wav:
        wav.setnchannels(1)  # Mono
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(sample_rate)

        for sample in audio_data:
            wav.writeframes(struct.pack('<h', sample))

    print(f"✓ Generated {wav_file}")
    print(f"  Duration: {duration} seconds")
    print(f"  Sample rate: {sample_rate} Hz")

    # Try to convert to MP3 if pydub is available
    try:
        from pydub import AudioSegment

        print("\nConverting to MP3...")
        sound = AudioSegment.from_wav(wav_file)
        mp3_file = os.path.join(audio_dir, "ringtone.mp3")
        sound.export(mp3_file, format="mp3", bitrate="192k")

        print(f"✓ Generated {mp3_file}")
        print(f"\nRingtone ready! You can delete the WAV file.")

        # Remove WAV file
        os.remove(wav_file)
        print(f"✓ Cleaned up {wav_file}")

    except ImportError:
        print("\n⚠️  pydub not installed. Install with: pip install pydub")
        print("   For now, the WAV file is ready to use or convert manually.")
        print("\n   To convert to MP3:")
        print("   1. Install ffmpeg")
        print("   2. Run: ffmpeg -i frontend/static/audio/ringtone.wav -q:a 9 frontend/static/audio/ringtone.mp3")
        print("   3. Delete the WAV file")

if __name__ == "__main__":
    print("Generating Buzzer ringtone...\n")
    generate_ringtone()
    print("\n✅ Ringtone generation complete!")

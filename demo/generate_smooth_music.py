import math
import struct
import wave

sample_rate = 44100
duration = 50.0  # seconds
num_samples = int(sample_rate * duration)

# Smooth, cool, soft acoustic jazz / chill-hop chord progression:
# Fmaj7 -> Em7 -> Dm7 -> Cmaj7
# Warm, airy, velvety chords:
# Fmaj7: F3 (174.61), A3 (220.00), C4 (261.63), E4 (329.63)
# Em7:   E3 (164.81), G3 (196.00), B3 (246.94), D4 (293.66)
# Dm7:   D3 (146.83), F3 (174.61), A3 (220.00), C4 (261.63)
# Cmaj7: C3 (130.81), E3 (164.81), G3 (196.00), B3 (246.94)

chords = [
    [174.61, 220.00, 261.63, 329.63], # Fmaj7
    [164.81, 196.00, 246.94, 293.66], # Em7
    [146.83, 174.61, 220.00, 261.63], # Dm7
    [130.81, 164.81, 196.00, 246.94], # Cmaj7
]

chord_duration = 4.0 # 4 seconds per chord

with wave.open("/config/Desktop/BuildWithGemini/wardrobe-stylist/demo/smooth_cool_track.wav", "w") as wav_file:
    wav_file.setnchannels(2) # Stereo
    wav_file.setsampwidth(2) # 16-bit
    wav_file.setframerate(sample_rate)
    
    frames = bytearray()
    
    for i in range(num_samples):
        t = i / sample_rate
        chord_idx = int((t % (chord_duration * len(chords))) / chord_duration)
        current_chord = chords[chord_idx]
        
        chord_t = t % chord_duration
        
        # Soft, slow attack & gentle decay for an ambient, chill pad & warm electric keys
        envelope = math.sin(math.pi * min(1.0, chord_t / 1.2)) * (0.8 + 0.2 * math.cos(math.pi * chord_t / chord_duration))
        
        # Smooth gentle chorus / vibrato
        vibrato = math.sin(2 * math.pi * 3.5 * t) * 0.8
        
        synth_val = 0.0
        for idx, f in enumerate(current_chord):
            freq = f + vibrato
            # Warm sine wave with subtle octave overtone
            voice = math.sin(2 * math.pi * freq * t) * 0.55 + math.sin(2 * math.pi * freq * 2 * t) * 0.15
            synth_val += voice
        
        synth_val = synth_val * envelope * 0.12
        
        # Add a deep, warm bass note on the root of each chord
        root_freq = current_chord[0] / 2.0  # One octave lower
        bass_env = math.exp(-chord_t * 0.5) * 0.15
        bass = math.sin(2 * math.pi * root_freq * t) * bass_env
        
        # Very gentle, soft ambient brushed percussion (soft tap every 1.0s, slow 60 BPM)
        beat_t = t % 1.0
        brush = 0.0
        if beat_t < 0.15:
            # Low-passed soft acoustic brush sound
            brush = math.sin(2 * math.pi * 180 * math.exp(-beat_t * 25) * beat_t) * math.exp(-beat_t * 20) * 0.06
            
        total = max(-0.95, min(0.95, synth_val + bass + brush))
        
        # Stereo panning for open soundscape
        left = int(total * 26000)
        right = int(total * 27000)
        frames.extend(struct.pack("<hh", left, right))
        
    wav_file.writeframes(frames)
print("Smooth cool soft music generated successfully!")

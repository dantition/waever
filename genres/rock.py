#!/usr/bin/env python3
"""WÆver — Rock Genre Generator"""
import random
from core import SonicComposition, DrumTrack
from theory import PROGRESSIONS, get_scale_note

def generate(config: dict) -> str:
    tempo = config.get('tempo', 130)
    key = config.get('key', 'E')
    scale = config.get('scale', 'major')
    bars = config.get('bars', 16)
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'rock.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    guitar = comp.add_track('Guitar', 0, 29)  # Overdriven
    bass_t = comp.add_track('Bass', 1, 33)
    drums = DrumTrack(comp.midi)
    
    progression = PROGRESSIONS.get('pop_1', [1, 5, 6, 4])
    current_time = 0.0
    
    for bar_idx in range(bars):
        degree = progression[bar_idx % len(progression)]
        beats = comp.beats_per_bar
        root = get_scale_note(degree - 1, key, scale, 3)
        
        # Guitar riff: power chords
        power = [root, root + 7]
        riff_pattern = [0, 0.75, 1.5, 2, 3] if bar_idx % 2 == 0 else [0, 1, 2, 3]
        for t in riff_pattern:
            vel = comp.humanize_velocity(90, 12)
            guitar.chord(power, current_time + t, 0.5, vel)
        
        # Bass: root notes following kick
        bass_t.note(root - 12, current_time, 1, comp.humanize_velocity(90, 10))
        bass_t.note(root - 12, current_time + 2, 1, comp.humanize_velocity(85, 10))
        
        # Drums: basic rock beat
        drums.hit('kick', current_time, 0.3, comp.humanize_velocity(100, 8))
        drums.hit('kick', current_time + 2, 0.3, comp.humanize_velocity(100, 8))
        drums.hit('snare', current_time + 1, 0.3, 105)
        drums.hit('snare', current_time + 3, 0.3, 105)
        
        # Hi-hats: 8ths
        for i in range(8):
            drums.hit('hihat_closed', current_time + i * 0.5, 0.2, comp.humanize_velocity(80, 10))
        
        # Crash on 1
        if bar_idx % 4 == 0:
            drums.hit('crash', current_time, 0.5, 100)
        
        # Fill
        if bar_idx % 4 == 3 and bar_idx < bars - 1:
            drums.fill(current_time + 3, 'basic', 110)
        
        current_time += beats
    
    comp.save(output)
    return {'file': output, 'bars': bars, 'tempo': tempo, 'key': f"{key} {scale}",
            'duration_sec': round(bars * (4 / tempo) * 60, 1), 'seed': seed,
            'instruments': ['Overdriven Guitar', 'Bass', 'Rock Drums']}

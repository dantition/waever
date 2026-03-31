#!/usr/bin/env python3
"""SonicForge — Metal Genre Generator"""
import random
from core import SonicComposition, DrumTrack
from theory import PROGRESSIONS, get_scale_note, build_chord

def generate(config: dict) -> str:
    tempo = config.get('tempo', 150)
    key = config.get('key', 'E')
    scale = config.get('scale', 'minor')
    bars = config.get('bars', 16)
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'metal.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    guitar = comp.add_track('Guitar', 0, 30)  # Distortion
    bass_t = comp.add_track('Bass', 1, 33)
    drums = DrumTrack(comp.midi)
    
    progression = PROGRESSIONS.get('metal_1', [1, 7, 6, 5])
    current_time = 0.0
    
    for bar_idx in range(bars):
        degree = progression[bar_idx % len(progression)]
        beats = comp.beats_per_bar
        root = get_scale_note(degree - 1, key, scale, 3)
        
        # Power chords: root + fifth
        power = [root, root + 7]
        
        # Palm-muted chugs
        chug_pattern = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5] if bar_idx % 2 == 0 else [0, 1, 2, 3]
        for t in chug_pattern:
            vel = comp.humanize_velocity(100, 10)
            guitar.chord(power, current_time + t, 0.3, vel)
            bass_t.note(root - 12, current_time + t, 0.3, vel)
        
        # Double bass drum
        for i in range(8):
            drums.hit('kick', current_time + i * 0.5, 0.15, comp.humanize_velocity(105, 8))
        drums.hit('snare', current_time + 1, 0.3, 110)
        drums.hit('snare', current_time + 3, 0.3, 110)
        
        # Crash on downbeats
        if bar_idx % 4 == 0:
            drums.hit('crash', current_time, 0.5, 110)
        
        # Fill every 4 bars
        if bar_idx % 4 == 3 and bar_idx < bars - 1:
            drums.fill(current_time + 3, 'roll', 115)
        
        current_time += beats
    
    comp.save(output)
    return {'file': output, 'bars': bars, 'tempo': tempo, 'key': f"{key} {scale}",
            'duration_sec': round(bars * (4 / tempo) * 60, 1), 'seed': seed,
            'instruments': ['Distortion Guitar', 'Bass', 'Double Kick Drums']}

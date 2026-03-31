#!/usr/bin/env python3
"""WÆver — Ambient Genre Generator"""
import random
from core import SonicComposition, DrumTrack
from theory import get_scale_note, SCALES

def generate(config: dict) -> str:
    tempo = config.get('tempo', 55)
    key = config.get('key', 'C')
    scale = config.get('scale', 'major')
    bars = config.get('bars', 24)
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'ambient.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    pad1 = comp.add_track('Pad 1', 0, 89)   # New Age Pad
    pad2 = comp.add_track('Pad 2', 1, 94)   # Halo Pad
    bells = comp.add_track('Bells', 2, 14)   # Tubular Bells
    bass_t = comp.add_track('Sub Bass', 3, 38)  # Synth Bass
    
    current_time = 0.0
    
    for bar_idx in range(bars):
        beats = comp.beats_per_bar
        
        # Drone: sustained root + fifth
        root = get_scale_note(0, key, scale, 3)
        fifth = root + 7
        octave = root + 12
        
        # Slow evolving pads
        pad1.note(root, current_time, beats * 2, comp.humanize_velocity(45, 5))
        pad1.note(fifth, current_time, beats * 2, comp.humanize_velocity(40, 5))
        
        pad2.note(octave, current_time, beats * 3, comp.humanize_velocity(35, 5))
        pad2.note(octave + 4, current_time + beats, beats * 2, comp.humanize_velocity(30, 5))
        
        # Bells: sparse melodic touches
        if bar_idx % 3 == 0:
            bell_note = get_scale_note(random.choice([0, 2, 4, 7]), key, scale, 5)
            bells.note(bell_note, current_time + random.uniform(0, 2), beats, 
                      comp.humanize_velocity(50, 10))
        
        # Sub bass: very low, very slow
        if bar_idx % 2 == 0:
            bass_t.note(root - 24, current_time, beats * 2, comp.humanize_velocity(55, 5))
        
        current_time += beats
    
    comp.save(output)
    return {'file': output, 'bars': bars, 'tempo': tempo, 'key': f"{key} {scale}",
            'duration_sec': round(bars * (4 / tempo) * 60, 1), 'seed': seed,
            'instruments': ['Pad 1', 'Pad 2', 'Tubular Bells', 'Sub Bass']}

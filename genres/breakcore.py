#!/usr/bin/env python3
"""
WÆver — Breakcore Genre Generator
Chopped breaks, tempo changes, controlled chaos.
"""

import random
from core import SonicComposition, DrumTrack
from theory import PROGRESSIONS, get_scale_note, GM_DRUMS

def generate(config: dict) -> str:
    tempo = config.get('tempo', 185)
    key = config.get('key', 'D')
    scale = config.get('scale', 'minor')
    bars = config.get('bars', 16)
    chaos = config.get('chaos', 0.7)  # 0-1, how chaotic
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'breakcore.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    # === INSTRUMENTS ===
    bass_track = comp.add_track('Bass', 0, 38)  # Synth Bass
    lead = comp.add_track('Lead', 1, 80)  # Lead Square
    pad = comp.add_track('Pad', 2, 94)  # Halo Pad
    drums = DrumTrack(comp.midi)
    
    current_time = 0.0
    
    for bar_idx in range(bars):
        beats = comp.beats_per_bar
        
        # === CHOPPED BREAK PATTERN ===
        # Breakcore uses chopped amen-style breaks
        break_hits = []
        
        # Base break pattern (amen-style)
        amen = [
            ('kick', 0), ('snare', 0.5), ('kick', 1.0), ('snare', 1.5),
            ('kick', 2.0), ('snare', 2.25), ('kick', 2.5), ('snare', 3.0),
            ('kick', 3.25), ('snare', 3.5),
        ]
        
        # Chop and rearrange based on chaos level
        num_slices = int(4 + chaos * 12)  # 4-16 slices per bar
        slice_positions = sorted(random.sample(range(16), min(num_slices, 16)))
        
        for pos in slice_positions:
            t = current_time + pos * 0.25
            hit = random.choice(['kick', 'snare', 'kick', 'snare', 'tom_high', 'tom_mid'])
            
            # Glitch: sometimes reverse or stutter
            if random.random() < chaos * 0.3:
                # Stutter: rapid repeats
                for s in range(random.randint(2, 4)):
                    stutter_t = t + s * 0.0625
                    vel = comp.humanize_velocity(90 - s * 15, 10)
                    drums.hit(hit, stutter_t, 0.05, vel)
            else:
                vel = comp.humanize_velocity(100, 20)
                drums.hit(hit, t, 0.1, vel)
        
        # Hi-hat chaos: rapid 16ths or 32nds
        if random.random() < chaos:
            for i in range(16):
                if random.random() < 0.7:
                    t = current_time + i * 0.25
                    vel = comp.humanize_velocity(70, 25)
                    drums.hit('hihat_closed', t, 0.05, vel)
        
        # Occasional crash
        if bar_idx % 4 == 0:
            drums.hit('crash', current_time, 0.5, 100)
        
        # === BASS: AGGRESSIVE ===
        root = get_scale_note(0, key, scale, 2)
        
        # Distorted bass: root + octave stabs
        bass_pattern = random.choice([
            [0, 0.5, 1, 2, 2.5, 3],      # Driving
            [0, 1, 2, 3],                  # Minimal
            [0, 0.25, 0.5, 1, 1.5, 2, 3], # Busy
        ])
        
        for t in bass_pattern:
            if t < beats:
                vel = comp.humanize_velocity(100, 15)
                bass_track.note(root, current_time + t, 0.3, vel)
                # Occasional octave jump
                if random.random() < 0.2:
                    bass_track.note(root + 12, current_time + t + 0.125, 0.15, vel - 10)
        
        # === LEAD: GLITCHY MELODY ===
        melody_notes = []
        for i in range(random.randint(4, 8)):
            deg = random.randint(-2, 7)
            n = get_scale_note(deg, key, scale, 5)
            melody_notes.append(n)
        
        note_dur = beats / len(melody_notes) if melody_notes else 0.5
        for i, n in enumerate(melody_notes):
            t = current_time + i * note_dur
            vel = comp.humanize_velocity(80, 20)
            
            # Glitch: pitch bend effect (jump to nearby note)
            if random.random() < chaos * 0.2:
                lead.note(n + random.choice([-1, 1]), t, note_dur * 0.3, vel)
            lead.note(n, t, note_dur * 0.7, vel)
        
        # === PAD: DRONE LAYER (occasional) ===
        if bar_idx % 4 == 0:
            root_pad = get_scale_note(0, key, scale, 3)
            pad.note(root_pad, current_time, beats * 2, comp.humanize_velocity(45, 8))
            pad.note(root_pad + 7, current_time, beats * 2, comp.humanize_velocity(40, 8))
        
        # === TEMPO CHANGE (breakcore signature) ===
        # Note: MIDI tempo changes are global, so we simulate with note density changes
        # Actual tempo changes would need tempo events added to the MIDI
        
        current_time += beats
    
    comp.save(output)
    return {
        'file': output,
        'bars': bars,
        'tempo': tempo,
        'key': f"{key} {scale}",
        'chaos': chaos,
        'duration_sec': round(bars * (4 / tempo) * 60, 1),
        'seed': seed,
        'instruments': ['Distorted Bass', 'Glitch Lead', 'Halo Pad', 'Chopped Breaks']
    }

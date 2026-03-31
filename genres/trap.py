#!/usr/bin/env python3
"""
WÆver — Trap Genre Generator
808 bass, hi-hat rolls, minor scales, dark vibes.
"""

import random
from core import SonicComposition, DrumTrack
from theory import (
    PROGRESSIONS, DRUM_PATTERNS, get_scale_note, build_chord,
    GM_DRUMS
)

def generate(config: dict) -> str:
    tempo = config.get('tempo', 145)
    key = config.get('key', 'C')
    scale = config.get('scale', 'minor')
    bars = config.get('bars', 16)
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'trap.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    # === INSTRUMENTS ===
    bass_track = comp.add_track('808 Bass', 0, 36)  # Synth Bass
    melody = comp.add_track('Melody', 1, 81)  # Lead Synth
    pad = comp.add_track('Pad', 2, 88)  # Synth Pad
    drums = DrumTrack(comp.midi)
    
    # === PROGRESSION ===
    progression = PROGRESSIONS.get('trap_2', [1, 4, 1, 4])
    
    current_time = 0.0
    
    for bar_idx in range(bars):
        prog_idx = (bar_idx // 2) % len(progression)  # Change every 2 bars
        degree = progression[prog_idx]
        beats = comp.beats_per_bar
        
        # === 808 BASS ===
        root = get_scale_note(0, key, scale, 2)  # Low octave
        
        # 808 pattern: hit on 1, slide or sustain
        bass_vel = comp.humanize_velocity(110, 10)
        bass_track.note(root, current_time, 1.5, bass_vel)
        
        # Secondary 808 hit
        if bar_idx % 2 == 0:
            bass_track.note(root - 5, current_time + 2.5, 1.0, bass_vel - 10)
        else:
            bass_track.note(root, current_time + 2, 1.5, bass_vel - 5)
        
        # 808 slide on last bar of phrase
        if bar_idx % 4 == 3:
            bass_track.note(root, current_time + 3, 0.5, bass_vel)
            bass_track.note(root + 5, current_time + 3.5, 0.5, bass_vel - 15)
        
        # === DRUMS: TRAP PATTERN ===
        # Kick: beat 1 and "and of 2" (10 in 16th grid)
        drums.hit('kick', current_time, 0.3, comp.humanize_velocity(110, 8))
        drums.hit('kick', current_time + 2.5, 0.3, comp.humanize_velocity(100, 8))
        
        # Snare: beat 3 (position 8 in 16th grid)
        drums.hit('snare', current_time + 2, 0.3, comp.humanize_velocity(115, 5))
        
        # Hi-hats: 8ths normally, rolls on certain bars
        if bar_idx % 4 == 3:
            # Hi-hat roll: 16ths then 32nds
            for i in range(16):
                t = current_time + i * 0.25
                vel = comp.humanize_velocity(90 - (i * 2), 10)
                drums.hit('hihat_closed', t, 0.1, vel)
        else:
            # Standard 8th note hats with occasional open hat
            for i in range(8):
                t = current_time + i * 0.5
                hat = 'hihat_open' if (i == 3 and random.random() < 0.3) else 'hihat_closed'
                vel = comp.humanize_velocity(85, 12)
                drums.hit(hat, t, 0.2, vel)
        
        # === PAD: SUSTAINED CHORDS ===
        chord_notes = comp.get_chord(degree, octave=3)
        for n in chord_notes:
            pad.note(n, current_time, beats, comp.humanize_velocity(55, 8))
        
        # === MELODY ===
        # Trap melodies: minor scale, lots of repetition, sparse
        melody_pattern = random.choice([
            [0, 0, 3, 2, 0, 0, -1, 0],  # Descending
            [4, 3, 2, 0, 0, 2, 3, 4],   # Ascending-then-back
            [0, 0, 0, 5, 4, 3, 2, 0],   # Jump then descend
            [7, 5, 3, 2, 0, 0, 2, 3],   # High start descending
        ])
        
        note_dur = beats / len(melody_pattern)
        for i, deg in enumerate(melody_pattern):
            n = get_scale_note(deg, key, scale, 5)
            # Sparse: skip some notes (rests)
            if random.random() < 0.15:
                continue
            vel = comp.humanize_velocity(70, 15)
            # Triplet feel on some notes
            dur = note_dur * 0.75 if random.random() < 0.2 else note_dur * 0.8
            melody.note(n, current_time + i * note_dur, dur, vel)
        
        current_time += beats
    
    comp.save(output)
    return {
        'file': output,
        'bars': bars,
        'tempo': tempo,
        'key': f"{key} {scale}",
        'duration_sec': round(bars * (4 / tempo) * 60, 1),
        'seed': seed,
        'instruments': ['808 Bass', 'Lead Synth', 'Synth Pad', 'Drums']
    }

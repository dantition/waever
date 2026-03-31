#!/usr/bin/env python3
"""
SonicForge — Lo-fi Genre Generator
Jazzy chords, swing drums, mellow vibes.
"""

import random
from core import SonicComposition, DrumTrack
from theory import PROGRESSIONS, get_scale_note

def generate(config: dict) -> str:
    tempo = config.get('tempo', 82)
    key = config.get('key', 'C')
    scale = config.get('scale', 'major')
    bars = config.get('bars', 16)
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'lofi.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    # === INSTRUMENTS ===
    piano = comp.add_track('Rhodes', 0, 4)  # Electric Piano
    bass_track = comp.add_track('Bass', 1, 33)
    pad = comp.add_track('Pad', 2, 89)  # New Age Pad
    drums = DrumTrack(comp.midi)
    
    # === PROGRESSION ===
    progression = PROGRESSIONS.get('lofi_2', [1, 6, 2, 5])
    
    current_time = 0.0
    prev_voicing = []
    
    for bar_idx in range(bars):
        prog_idx = bar_idx % len(progression)
        degree = progression[prog_idx]
        beats = comp.beats_per_bar
        
        # === PIANO: JAZZY VOICINGS ===
        chord_notes = comp.get_chord(degree, octave=4, seventh=True)
        
        # Lo-fi voicing: add 9ths, use spread voicings
        if len(chord_notes) >= 4:
            voicing = [chord_notes[0], chord_notes[2], chord_notes[3]]  # Root, 5th, 7th
            if len(chord_notes) > 4:
                voicing.append(chord_notes[4])  # 9th
        else:
            voicing = chord_notes
        
        # Comping: laid-back rhythm
        comp_times = [0, 1.5, 2.5, 3.5] if bar_idx % 2 == 0 else [0.5, 2, 3]
        for t in comp_times:
            vel = comp.humanize_velocity(60, 15)  # Soft
            # Swing timing
            if int(t) % 2 == 1:
                t += 0.05
            piano.chord(voicing, current_time + t, 1.0, vel)
        
        # === WALKING BASS (simplified) ===
        root = chord_notes[0] - 12
        bass_notes = [root, root + 5, root + 3, root + 7]
        for i, note in enumerate(bass_notes):
            t = current_time + i
            if i % 2 == 1:
                t += 0.06  # Swing
            bass_track.note(note, t, 0.8, comp.humanize_velocity(70, 10))
        
        # === DRUMS: LO-FI SWING ===
        # Kick
        drums.hit('kick', current_time, 0.3, comp.humanize_velocity(85, 10))
        if bar_idx % 2 == 1:
            drums.hit('kick', current_time + 2.67, 0.3, comp.humanize_velocity(75, 10))
        
        # Snare on 2 and 4
        drums.hit('snare', current_time + 1, 0.3, comp.humanize_velocity(90, 8))
        drums.hit('snare', current_time + 3, 0.3, comp.humanize_velocity(90, 8))
        
        # Hi-hats: swing 8ths
        for i in range(8):
            t = current_time + i * 0.5
            if i % 2 == 1:
                t += 0.08  # Swing
            vel = comp.humanize_velocity(70, 15)
            drums.hit('hihat_closed', t, 0.2, vel)
        
        # Ghost snare
        if random.random() < 0.5:
            drums.hit('snare', current_time + 0.67, 0.1, 40)
        
        # === PAD: AMBIENT LAYER ===
        pad_note = get_scale_note(0, key, scale, 3)
        pad.note(pad_note, current_time, beats * 2, comp.humanize_velocity(40, 5))
        pad.note(pad_note + 7, current_time, beats * 2, comp.humanize_velocity(35, 5))
        
        current_time += beats
    
    comp.save(output)
    return {
        'file': output,
        'bars': bars,
        'tempo': tempo,
        'key': f"{key} {scale}",
        'duration_sec': round(bars * (4 / tempo) * 60, 1),
        'seed': seed,
        'instruments': ['Rhodes Piano', 'Bass', 'Ambient Pad', 'Drums (Swing)']
    }

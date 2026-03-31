#!/usr/bin/env python3
"""
SonicForge — Jazz Genre Generator
Swing feel, 7th chords, walking bass, ride patterns.
"""

import random
from core import SonicComposition, DrumTrack
from theory import (
    PROGRESSIONS, DRUM_PATTERNS, get_scale_note, build_chord,
    chord_from_scale_degree, SCALES, CHORD_TYPES
)

def generate(config: dict) -> str:
    tempo = config.get('tempo', 130)
    key = config.get('key', 'Bb')
    scale = config.get('scale', 'major')
    bars = config.get('bars', 32)
    style = config.get('style', 'standard')  # standard, blues, bossa
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'jazz.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    # === INSTRUMENTS ===
    piano = comp.add_track('Piano', 0, 0)
    bass_track = comp.add_track('Bass', 1, 33)
    drums = DrumTrack(comp.midi)
    sax = comp.add_track('Sax', 2, 65)  # Alto Sax
    
    # === PROGRESSION ===
    if style == 'blues':
        progression = PROGRESSIONS['jazz_blues']
    else:
        progression = PROGRESSIONS['jazz_251'] * (bars // 3 + 1)
    
    # === JAZZ SCALES ===
    jazz_scale = 'mixolydian'  # Default for dominant chords
    
    current_time = 0.0
    
    for bar_idx in range(bars):
        prog_idx = bar_idx % len(progression)
        degree = progression[prog_idx]
        beats = comp.beats_per_bar
        
        # === PIANO: COMPING (chord stabs) ===
        chord_notes = comp.get_chord(degree, octave=4, seventh=True)
        
        # Jazz voicing: rootless voicing for more sophisticated sound
        if len(chord_notes) >= 4:
            voicing = [chord_notes[1], chord_notes[2], chord_notes[3]]  # 3rd, 5th, 7th
            if len(chord_notes) > 4:
                voicing.append(chord_notes[4])  # 9th
        else:
            voicing = chord_notes
        
        # Comping rhythm: syncopated
        comp_times = [0, 1.5, 3] if bar_idx % 2 == 0 else [0.5, 2, 3.5]
        for t in comp_times:
            vel = comp.humanize_velocity(70, 15)
            piano.chord(voicing, current_time + t, 0.75, vel)
        
        # === WALKING BASS ===
        root_midi = chord_notes[0] - 12
        fifth = root_midi + 7
        third = chord_notes[1] if len(chord_notes) > 1 else root_midi + 4
        seventh = chord_notes[3] if len(chord_notes) > 3 else root_midi + 10
        
        # Walking pattern: root-approach-chord tone-chord tone
        bass_notes = [root_midi, root_midi + 5, third - 12, fifth - 12]
        
        # Add chromatic approach notes
        if bar_idx < bars - 1:
            next_root = comp.get_chord(progression[(bar_idx + 1) % len(progression)], 3)[0] - 12
            bass_notes[-1] = next_root - 1  # Chromatic approach
        
        for i, note in enumerate(bass_notes):
            # Swing timing: off-beats are slightly delayed
            t = current_time + i
            if i % 2 == 1:
                t += 0.08  # Swing feel
            bass_track.note(note, t, 0.9, comp.humanize_velocity(85, 10))
        
        # === DRUMS: SWING RIDE ===
        drum_vel = 100
        # Ride cymbal swing pattern
        for beat in range(4):
            drums.hit('ride', current_time + beat, 0.3, drum_vel)
            if beat < 3:
                drums.hit('ride', current_time + beat + 0.67, 0.2, drum_vel - 20)  # Swing skip
        # Hi-hat on 2 and 4
        drums.hit('hihat_pedal', current_time + 1, 0.2, 80)
        drums.hit('hihat_pedal', current_time + 3, 0.2, 80)
        # Kick accents
        if bar_idx % 2 == 0:
            drums.hit('kick', current_time, 0.3, 90)
        # Ghost notes on snare
        if random.random() < 0.4:
            drums.hit('snare', current_time + 0.67, 0.1, 50)
        if random.random() < 0.3:
            drums.hit('snare', current_time + 2.67, 0.1, 45)
        
        # === SAX: MELODY ===
        # Use mixolydian over dominant, major over major chords
        chord_type = 'major' if degree in [1, 4] else 'dom7'
        melody_scale = 'mixolydian' if chord_type == 'dom7' else 'major'
        
        # Generate bebop-style melody
        phrase_length = random.choice([4, 6, 8])
        melody_degrees = []
        current_deg = random.randint(0, 6)
        
        for _ in range(phrase_length):
            # Chromatic approach notes (bebop style)
            if random.random() < 0.25:
                current_deg += random.choice([-1, 1])  # Chromatic
            else:
                current_deg += random.choice([-2, -1, 1, 2])  # Diatonic
            
            current_deg = max(-2, min(9, current_deg))  # Keep in range
            melody_degrees.append(current_deg)
        
        note_dur = beats / phrase_length
        for i, deg in enumerate(melody_degrees):
            n = get_scale_note(deg, key, melody_scale, 5)
            # Swing timing
            t = current_time + i * note_dur
            if i % 2 == 1:
                t += note_dur * 0.15  # Swing delay
            
            # Vary velocity for dynamics
            vel = comp.humanize_velocity(75, 20)
            sax.note(n, t, note_dur * 0.8, vel)
        
        current_time += beats
    
    comp.save(output)
    return {
        'file': output,
        'bars': bars,
        'tempo': tempo,
        'key': f"{key} {scale}",
        'style': style,
        'duration_sec': round(bars * (4 / tempo) * 60, 1),
        'seed': seed,
        'instruments': ['Piano', 'Bass', 'Drums (Swing)', 'Alto Sax']
    }

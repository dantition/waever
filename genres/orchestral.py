#!/usr/bin/env python3
"""
WÆver — Orchestral Genre Generator
Dramatic orchestral pieces with strings, brass, woodwinds.
"""

import random
from core import SonicComposition, DrumTrack
from theory import (
    PROGRESSIONS, DRUM_PATTERNS, get_scale_note, build_chord,
    chord_from_scale_degree, voice_lead
)

def generate(config: dict) -> str:
    """
    Generate an orchestral piece.
    
    Config:
        tempo (int): 60-90 (default 72)
        key (str): Root note (default 'A')
        scale (str): Scale name (default 'minor')
        bars (int): Number of bars (default 32)
        mood (str): 'dramatic', 'heroic', 'dark', 'triumphant' (default 'dramatic')
        seed (int): Random seed for reproducibility
    """
    tempo = config.get('tempo', 72)
    key = config.get('key', 'A')
    scale = config.get('scale', 'minor')
    bars = config.get('bars', 32)
    mood = config.get('mood', 'dramatic')
    seed = config.get('seed', random.randint(0, 99999))
    output = config.get('output', 'orchestral.mid')
    
    random.seed(seed)
    comp = SonicComposition(tempo=tempo, key=key, scale=scale, seed=seed)
    
    # === INSTRUMENTS ===
    violin1 = comp.add_track('Violin I', 0, 40)
    violin2 = comp.add_track('Violin II', 1, 40)
    viola = comp.add_track('Viola', 2, 41)
    cello = comp.add_track('Cello', 3, 42)
    bass = comp.add_track('Bass', 4, 43)
    trumpet = comp.add_track('Trumpet', 5, 56)
    horn = comp.add_track('Horn', 6, 60)
    trombone = comp.add_track('Trombone', 7, 57)
    flute = comp.add_track('Flute', 9, 73)
    oboe = comp.add_track('Oboe', 10, 68)
    drums = DrumTrack(comp.midi)
    
    # === PROGRESSION ===
    prog_name = 'minor_1' if 'minor' in scale else 'pop_1'
    if mood == 'dark':
        prog_name = 'andalusian'
    elif mood == 'heroic':
        prog_name = 'pop_1'
    elif mood == 'triumphant':
        prog_name = 'pop_1'
    
    progression = PROGRESSIONS[prog_name]
    
    # === MELODY THEMES (scale degrees) ===
    themes = {
        'dramatic': [[0, 2, 4, 7, 9, 7, 4, 2],
                     [7, 9, 11, 14, 11, 9, 7, 4]],
        'heroic':   [[0, 4, 7, 12, 9, 7, 4, 0],
                     [2, 4, 7, 9, 7, 4, 2, 0]],
        'dark':     [[0, 1, 3, 5, 3, 1, 0, -1],
                     [7, 5, 3, 1, 0, 1, 3, 5]],
        'triumphant':[[0, 2, 4, 7, 9, 12, 9, 7],
                      [4, 7, 9, 11, 9, 7, 4, 2]],
    }
    
    melody_themes = themes.get(mood, themes['dramatic'])
    
    # === GENERATE ===
    current_time = 0.0
    prev_chord = []
    
    for bar_idx in range(bars):
        prog_idx = bar_idx % len(progression)
        degree = progression[prog_idx]
        beats = comp.beats_per_bar
        
        # === CHORD PROGRESSION ===
        chord_notes = comp.get_chord(degree, octave=3, seventh=(mood == 'triumphant'))
        chord_high = comp.get_chord(degree, octave=4, seventh=(mood == 'triumphant'))
        
        # Voice lead
        if prev_chord:
            chord_notes = voice_lead(prev_chord, chord_notes)
        prev_chord = chord_notes
        
        # === STRINGS: SUSTAINED PADS ===
        # Cellos: root + fifth
        cello_notes = [chord_notes[0], chord_notes[2] if len(chord_notes) > 2 else chord_notes[0] + 7]
        for n in cello_notes:
            cello.note(n - 12, current_time, beats, comp.humanize_velocity(80, 10))
        
        # Bass: root two octaves down
        bass.note(chord_notes[0] - 24, current_time, beats, comp.humanize_velocity(85, 8))
        
        # Violas: full chord
        for n in chord_notes:
            viola.note(n, current_time, beats, comp.humanize_velocity(70, 12))
        
        # Violin II: chord an octave up
        for n in chord_high:
            violin2.note(n, current_time, beats, comp.humanize_velocity(65, 10))
        
        # === VIOLIN I: MELODY ===
        theme = melody_themes[bar_idx % len(melody_themes)]
        note_dur = beats / len(theme)
        
        # Melody dynamics based on position
        if bar_idx < bars * 0.25:
            base_vel = 65  # Soft opening
        elif bar_idx < bars * 0.75:
            base_vel = 80  # Building
        else:
            base_vel = 95  # Climax
        
        for i, degree in enumerate(theme):
            melody_note = get_scale_note(degree, key, scale, 5)
            # Crescendo within phrase
            vel = base_vel + (i * 3) if i < len(theme) // 2 else base_vel + ((len(theme) - i) * 3)
            violin1.note(melody_note, current_time + i * note_dur, note_dur * 0.85, 
                        comp.humanize_velocity(vel, 8))
        
        # === BRASS: ACCENTS ===
        if bar_idx % 2 == 0:
            for n in chord_notes[:2]:
                horn.note(n, current_time, 2, comp.humanize_velocity(85, 10))
                horn.note(n, current_time + 2, 2, comp.humanize_velocity(75, 10))
        
        # Trumpet: dramatic accents on strong beats
        if bar_idx % 4 == 0:
            trumpet.note(chord_high[0], current_time, 1, comp.humanize_velocity(95, 8))
        elif bar_idx % 4 == 2:
            if len(chord_high) > 2:
                trumpet.note(chord_high[2], current_time + 2, 1, comp.humanize_velocity(90, 8))
        
        # === WOODWINDS: FILLS ===
        if bar_idx % 4 >= 2:
            scale_notes = get_scale_note(0, key, scale, 5), get_scale_note(2, key, scale, 5), \
                         get_scale_note(4, key, scale, 5), get_scale_note(7, key, scale, 5)
            fill_notes = random.sample(range(7), min(4, 7))
            for i, deg in enumerate(sorted(fill_notes)):
                n = get_scale_note(deg, key, scale, 5)
                flute.note(n, current_time + 0.5 + i * 0.75, 0.5, comp.humanize_velocity(60, 10))
        
        # Oboe counter-melody
        if bar_idx % 3 == 0:
            counter = [theme[0], theme[-1], theme[len(theme)//2]]
            for i, deg in enumerate(counter):
                n = get_scale_note(deg, key, scale, 4)
                oboe.note(n, current_time + i * (beats/3), beats/3, comp.humanize_velocity(65, 8))
        
        # === TIMPANI ===
        if bar_idx % 2 == 0:
            drums.hit('kick', current_time, 1, comp.humanize_velocity(100, 10))
        if bar_idx % 4 == 3 and bar_idx < bars - 1:
            # Dramatic roll before transition
            for beat in range(4):
                drums.hit('kick', current_time + beat, 0.5, comp.humanize_velocity(80, 10))
        
        # === CRESCENDO IN FINAL BARS ===
        if bar_idx >= bars - 4:
            boost = (bar_idx - (bars - 4)) * 12
            for n in chord_notes:
                trombone.note(n - 12, current_time, beats, 
                            min(127, 80 + boost + random.randint(-5, 5)))
        
        # === FINAL CHORD ===
        if bar_idx == bars - 1:
            # Everyone plays
            for inst in [violin1, violin2, viola, cello, bass, trumpet, horn, trombone, flute, oboe]:
                for n in chord_notes:
                    inst.note(n, current_time, beats * 2, comp.humanize_velocity(90, 15))
        
        current_time += beats
    
    comp.save(output)
    return {
        'file': output,
        'bars': bars,
        'tempo': tempo,
        'key': f"{key} {scale}",
        'mood': mood,
        'duration_sec': round(bars * (4 / tempo) * 60, 1),
        'seed': seed,
        'progression': prog_name,
        'instruments': ['Violin I', 'Violin II', 'Viola', 'Cello', 'Bass', 
                       'Trumpet', 'Horn', 'Trombone', 'Flute', 'Oboe']
    }

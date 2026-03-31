#!/usr/bin/env python3
"""
WÆver — Music Theory Library
Core scales, chords, progressions, and utilities.
"""

# === NOTE UTILITIES ===
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
ENHARMONIC = {'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}

def note_to_midi(name: str, octave: int = 4) -> int:
    """Convert note name to MIDI number. 'C4' = 60, 'A3' = 57"""
    n = name.replace('b', '#')  # Handle flats
    if n in ENHARMONIC:
        n = ENHARMONIC[n]
    if n not in NOTE_NAMES:
        n = ENHARMONIC.get(name, name)
    return NOTE_NAMES.index(n) + (octave + 1) * 12

def midi_to_note(midi: int) -> str:
    """Convert MIDI number to note name with octave."""
    octave = (midi // 12) - 1
    note = NOTE_NAMES[midi % 12]
    return f"{note}{octave}"

def note_name_to_index(name: str) -> int:
    """Convert note name to chromatic index (0-11)."""
    name = ENHARMONIC.get(name, name)
    return NOTE_NAMES.index(name)

# === SCALES ===
SCALES = {
    'major':             [0, 2, 4, 5, 7, 9, 11],
    'minor':             [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor':    [0, 2, 3, 5, 7, 8, 11],
    'melodic_minor':     [0, 2, 3, 5, 7, 9, 11],
    'dorian':            [0, 2, 3, 5, 7, 9, 10],
    'phrygian':          [0, 1, 3, 5, 7, 8, 10],
    'lydian':            [0, 2, 4, 6, 7, 9, 11],
    'mixolydian':        [0, 2, 4, 5, 7, 9, 10],
    'locrian':           [0, 1, 3, 5, 6, 8, 10],
    'pentatonic_major':  [0, 2, 4, 7, 9],
    'pentatonic_minor':  [0, 3, 5, 7, 10],
    'blues':             [0, 3, 5, 6, 7, 10],
    'chromatic':         list(range(12)),
    'whole_tone':        [0, 2, 4, 6, 8, 10],
    'diminished':        [0, 2, 3, 5, 6, 8, 9, 11],
}

def get_scale(root: str, scale_name: str, octave: int = 4) -> list:
    """Get all notes in a scale as MIDI numbers."""
    root_idx = note_name_to_index(root)
    intervals = SCALES.get(scale_name, SCALES['major'])
    base = (octave + 1) * 12 + root_idx
    return [base + i for i in intervals]

def get_scale_note(degree: int, root: str, scale_name: str, octave: int = 4) -> int:
    """Get a specific scale degree as MIDI number. Supports negative and overflow."""
    scale = get_scale(root, scale_name, octave)
    octaves_up = degree // len(scale)
    idx = degree % len(scale)
    return scale[idx] + octaves_up * 12

# === CHORD TYPES ===
CHORD_TYPES = {
    'major':     [0, 4, 7],
    'minor':     [0, 3, 7],
    'dim':       [0, 3, 6],
    'aug':       [0, 4, 8],
    'sus2':      [0, 2, 7],
    'sus4':      [0, 5, 7],
    'major7':    [0, 4, 7, 11],
    'minor7':    [0, 3, 7, 10],
    'dom7':      [0, 4, 7, 10],
    'dim7':      [0, 3, 6, 9],
    'half_dim7': [0, 3, 6, 10],
    'min7b5':    [0, 3, 6, 10],
    'major9':    [0, 4, 7, 11, 14],
    'minor9':    [0, 3, 7, 10, 14],
    'dom9':      [0, 4, 7, 10, 14],
    'add9':      [0, 4, 7, 14],
    '6':         [0, 4, 7, 9],
    'min6':      [0, 3, 7, 9],
    'power':     [0, 7],
    'octave':    [0, 12],
}

def build_chord(root: str, chord_type: str, octave: int = 4) -> list:
    """Build a chord from root note and type. Returns list of MIDI notes."""
    root_midi = note_to_midi(root, octave)
    intervals = CHORD_TYPES.get(chord_type, CHORD_TYPES['major'])
    return [root_midi + i for i in intervals]

def chord_from_scale_degree(degree: int, root: str, scale_name: str = 'major', 
                             octave: int = 4, seventh: bool = False) -> list:
    """Build a diatonic chord from a scale degree. E.g., degree=1 in C major = Cmaj7"""
    scale = get_scale(root, scale_name, octave)
    notes = []
    for i in range(4 if seventh else 3):
        idx = (degree - 1 + i * 2) % len(scale)
        octaves = (degree - 1 + i * 2) // len(scale)
        notes.append(scale[idx] + octaves * 12)
    return notes

# === PROGRESSIONS (as scale degrees, 1-indexed) ===
PROGRESSIONS = {
    # Pop/Rock
    'pop_1':      [1, 5, 6, 4],      # I-V-vi-IV
    'pop_2':      [6, 4, 1, 5],      # vi-IV-I-V
    'pop_3':      [1, 4, 5, 5],      # I-IV-V-V
    '50s':        [1, 6, 4, 5],      # I-vi-IV-V
    # Jazz
    'jazz_251':   [2, 5, 1],         # ii-V-I
    'jazz_1625':  [1, 6, 2, 5],      # I-vi-ii-V
    'jazz_rhythm':[1, 6, 2, 5, 1, 6, 2, 5],  # Rhythm changes A section
    'jazz_blues': [1, 1, 1, 1, 4, 4, 1, 1, 5, 4, 1, 5],  # 12-bar jazz blues
    # Minor
    'minor_1':    [1, 6, 7, 1],      # i-VI-VII-i
    'minor_2':    [1, 4, 7, 1],      # i-iv-VII-i
    'minor_3':    [1, 5, 6, 4],      # i-v-VI-iv
    'andalusian': [6, 5, 4, 1],      # VI-V-IV-i (Andalusian cadence)
    # Trap/Hip-Hop
    'trap_1':     [1, 1, 1, 1],      # i-i-i-i (loop-based)
    'trap_2':     [1, 4, 1, 4],      # i-iv-i-iv
    'trap_3':     [1, 6, 4, 5],      # i-VI-iv-v
    # Lo-fi
    'lofi_1':     [2, 5, 1, 6],      # ii7-V7-Imaj7-vi7
    'lofi_2':     [1, 6, 2, 5],      # Imaj7-vi7-ii7-V7
    'lofi_3':     [4, 5, 3, 6],      # IVmaj7-V7-iii7-vi7
    # Metal
    'metal_1':    [1, 7, 6, 5],      # i-VII-VI-v
    'metal_2':    [1, 1, 4, 5],      # i-i-iv-v
    'metal_chug': [1, 1, 1, 1],      # Single riff based
}

# === RHYTHM PATTERNS (beat positions, 0-15 for 16th note grid in 4/4) ===
DRUM_PATTERNS = {
    'basic_rock': {
        'kick':  [0, 8, 10],
        'snare': [4, 12],
        'hihat': [0, 2, 4, 6, 8, 10, 12, 14],
    },
    'basic_jazz': {
        'kick':  [0, 6, 10],
        'snare': [4, 12],
        'ride':  [0, 4, 6, 8, 12, 14],  # Swing ride pattern
        'hh_ped':[4, 12],
    },
    'trap_basic': {
        'kick':  [0, 10],
        'snare': [8],
        'hihat': [0, 2, 4, 6, 8, 10, 12, 14],
    },
    'trap_roll': {
        'kick':  [0, 10],
        'snare': [8],
        'hihat': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],  # 16th note roll
    },
    'breakcore': {
        'kick':  [0, 3, 6, 10, 14],
        'snare': [4, 8, 12],
        'hihat': [0, 2, 4, 5, 6, 8, 10, 12, 13, 14],
    },
    'lofi': {
        'kick':  [0, 8, 11],
        'snare': [4, 12],
        'hihat': [0, 3, 4, 6, 8, 10, 12, 14],  # Swing 8ths
    },
    'metal_double': {
        'kick':  [0, 2, 4, 6, 8, 10, 12, 14],  # Double bass
        'snare': [4, 12],
        'hihat': [0, 4, 8, 12],
    },
    'funk': {
        'kick':  [0, 6, 8, 14],
        'snare': [4, 12],
        'hihat': [0, 2, 4, 5, 6, 8, 10, 12, 14, 15],
    },
    'ambient': {
        'kick':  [0],
        'snare': [],
        'hihat': [0, 8],
    },
}

# === INSTRUMENT RANGES (MIDI program numbers) ===
INSTRUMENTS = {
    # Strings
    'violin':      {'program': 40, 'channel': 0, 'range': (55, 105)},
    'violin2':     {'program': 40, 'channel': 1, 'range': (55, 100)},
    'viola':       {'program': 41, 'channel': 2, 'range': (48, 93)},
    'cello':       {'program': 42, 'channel': 3, 'range': (36, 76)},
    'bass':        {'program': 43, 'channel': 4, 'range': (28, 67)},
    # Brass
    'trumpet':     {'program': 56, 'channel': 5, 'range': (58, 94)},
    'french_horn': {'program': 60, 'channel': 6, 'range': (41, 77)},
    'trombone':    {'program': 57, 'channel': 7, 'range': (40, 72)},
    'tuba':        {'program': 58, 'channel': 8, 'range': (28, 58)},
    # Woodwinds
    'flute':       {'program': 73, 'channel': 9, 'range': (60, 96)},
    'oboe':        {'program': 68, 'channel': 10, 'range': (58, 91)},
    'clarinet':    {'program': 71, 'channel': 11, 'range': (50, 91)},
    # Keys
    'piano':       {'program': 0, 'channel': 0, 'range': (21, 108)},
    'electric_piano':{'program': 4, 'channel': 0, 'range': (21, 108)},
    'organ':       {'program': 16, 'channel': 0, 'range': (21, 108)},
    'synth_pad':   {'program': 88, 'channel': 0, 'range': (36, 96)},
    # Guitar
    'acoustic_guitar':{'program': 25, 'channel': 0, 'range': (40, 88)},
    'electric_guitar':{'program': 27, 'channel': 0, 'range': (40, 88)},
    'distortion_guitar':{'program': 30, 'channel': 0, 'range': (40, 88)},
    # Bass
    'electric_bass':{'program': 33, 'channel': 0, 'range': (28, 67)},
    'slap_bass':   {'program': 36, 'channel': 0, 'range': (28, 67)},
    'synth_bass':  {'program': 38, 'channel': 0, 'range': (28, 67)},
    '808_bass':    {'program': 36, 'channel': 0, 'range': (24, 60)},
    # Drums (channel 9 in GM)
    'drums':       {'program': 0, 'channel': 9, 'range': (35, 81)},
    # Pad
    'strings_pad': {'program': 49, 'channel': 0, 'range': (36, 84)},
    'choir_pad':   {'program': 52, 'channel': 0, 'range': (48, 84)},
}

# === GM DRUM MAP (channel 9) ===
GM_DRUMS = {
    'kick':      36,  # Bass Drum
    'snare':     38,  # Acoustic Snare
    'snare_rim': 37,  # Side Stick
    'hihat_closed': 42,  # Closed Hi-Hat
    'hihat_open': 46,   # Open Hi-Hat
    'hihat_pedal': 44,  # Pedal Hi-Hat
    'tom_high':  50,  # High Tom
    'tom_mid':   47,  # Mid Tom
    'tom_low':   45,  # Low Floor Tom
    'crash':     49,  # Crash Cymbal 1
    'ride':      51,  # Ride Cymbal 1
    'ride_bell': 53,  # Ride Bell
    'clap':      39,  # Hand Clap
    'tambourine':54,  # Tambourine
    'cowbell':   56,  # Cowbell
    'shaker':    82,  # Shaker
    'conga_low': 64,  # Low Conga
    'conga_high':62,  # Mute High Conga
}

# === TEMPO RANGES BY GENRE ===
TEMPO_RANGES = {
    'orchestral':  (60, 90),
    'jazz':        (100, 160),
    'trap':        (130, 170),
    'lofi':        (70, 95),
    'breakcore':   (160, 220),
    'metal':       (120, 180),
    'rock':        (110, 150),
    'ambient':     (40, 70),
    'funk':        (95, 120),
}

# === VOICE LEADING RULES ===
def voice_lead(prev_chord: list, next_chord: list) -> list:
    """Apply basic voice leading: move each voice to the nearest note in the next chord."""
    if not prev_chord:
        return next_chord
    
    result = []
    for i, prev_note in enumerate(prev_chord):
        if i >= len(next_chord):
            break
        target = next_chord[i]
        # Find nearest octave
        candidates = [target + o * 12 for o in range(-2, 3)]
        nearest = min(candidates, key=lambda x: abs(x - prev_note))
        result.append(nearest)
    
    # Add any remaining notes
    for i in range(len(prev_chord), len(next_chord)):
        result.append(next_chord[i])
    
    return sorted(result)

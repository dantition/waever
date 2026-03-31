#!/usr/bin/env python3
"""
SonicForge — Core MIDI Generation Engine
Handles MIDI creation, timing, velocity, and humanization.
"""

import random
import math
from midiutil import MIDIFile
from theory import (
    note_to_midi, build_chord, chord_from_scale_degree,
    get_scale, get_scale_note, SCALES, CHORD_TYPES, PROGRESSIONS,
    DRUM_PATTERNS, INSTRUMENTS, GM_DRUMS, TEMPO_RANGES, voice_lead
)

class SonicTrack:
    """A single track/instrument in the composition."""
    def __init__(self, midi: MIDIFile, channel: int, program: int, name: str = ""):
        self.midi = midi
        self.channel = channel
        self.program = program
        self.name = name
        midi.addProgramChange(0, channel, 0, program)

    def note(self, pitch: int, time: float, duration: float, velocity: int = 80):
        """Add a note with humanized velocity."""
        vel = max(1, min(127, velocity + random.randint(-5, 5)))
        self.midi.addNote(0, self.channel, pitch, time, duration, vel)

    def chord(self, pitches: list, time: float, duration: float, velocity: int = 75):
        """Add a chord (multiple notes)."""
        for p in pitches:
            self.note(p, time, duration, velocity + random.randint(-3, 3))

    def rest(self, duration: float):
        """Return time offset for a rest (used for timing calculations)."""
        return duration

class SonicComposition:
    """Main composition class. Orchestrates all tracks and sections."""
    def __init__(self, tempo: int = 120, time_sig: tuple = (4, 4), key: str = 'C', 
                 scale: str = 'major', seed: int = None):
        self.tempo = tempo
        self.time_sig = time_sig
        self.key = key
        self.scale = scale
        self.midi = MIDIFile(numTracks=16)
        self.midi.addTempo(0, 0, tempo)
        self.tracks = {}
        self.current_time = 0.0
        self.beats_per_bar = time_sig[0]
        
        if seed is not None:
            random.seed(seed)
    
    def add_track(self, name: str, channel: int, program: int) -> SonicTrack:
        """Add a new instrument track."""
        track = SonicTrack(self.midi, channel, program, name)
        self.tracks[name] = track
        return track
    
    def get_chord(self, degree: int, octave: int = 4, seventh: bool = False) -> list:
        """Get a diatonic chord from a scale degree."""
        return chord_from_scale_degree(degree, self.key, self.scale, octave, seventh)
    
    def bars_to_beats(self, bars: float) -> float:
        """Convert bars to beats."""
        return bars * self.beats_per_bar
    
    def humanize_timing(self, time: float, amount: float = 0.02) -> float:
        """Add subtle timing variation (in beats)."""
        return time + random.uniform(-amount, amount)
    
    def humanize_velocity(self, base: int = 80, range_val: int = 15) -> int:
        """Generate humanized velocity."""
        return max(30, min(127, base + random.randint(-range_val, range_val)))
    
    def crescendo(self, start_vel: int, end_vel: int, steps: int) -> list:
        """Generate velocity curve for crescendo/decrescendo."""
        if steps <= 1:
            return [end_vel]
        return [int(start_vel + (end_vel - start_vel) * i / (steps - 1)) for i in range(steps)]
    
    def save(self, filename: str):
        """Save the composition to a MIDI file."""
        with open(filename, 'wb') as f:
            self.midi.writeFile(f)

class DrumTrack:
    """Specialized track for drums (GM channel 9)."""
    def __init__(self, midi: MIDIFile, channel: int = 9):
        self.midi = midi
        self.channel = channel
    
    def hit(self, drum_name: str, time: float, duration: float = 0.25, velocity: int = 100):
        """Hit a drum."""
        pitch = GM_DRUMS.get(drum_name, 36)
        vel = max(1, min(127, velocity + random.randint(-8, 8)))
        self.midi.addNote(0, self.channel, pitch, time, duration, vel)
    
    def pattern(self, pattern_dict: dict, time: float, subdivisions: int = 16, 
                velocity: int = 100, swing: float = 0.0):
        """Play a drum pattern from a dict of {instrument: [positions]}."""
        beat_duration = 4.0 / subdivisions  # Duration of one subdivision in beats
        
        for inst, positions in pattern_dict.items():
            for pos in positions:
                t = time + pos * beat_duration
                # Apply swing to off-beat positions
                if pos % 2 == 1 and swing > 0:
                    t += beat_duration * swing
                # Ghost notes: lower velocity on some hits
                v = velocity
                if pos % 4 == 2 and random.random() < 0.3:
                    v = velocity - random.randint(20, 40)
                self.hit(inst, t, beat_duration * 0.8, v)
    
    def fill(self, time: float, fill_type: str = 'basic', velocity: int = 110):
        """Generate a drum fill."""
        if fill_type == 'basic':
            self.hit('tom_high', time, 0.25, velocity)
            self.hit('tom_mid', time + 0.25, 0.25, velocity - 5)
            self.hit('tom_low', time + 0.5, 0.25, velocity - 10)
            self.hit('snare', time + 0.75, 0.25, velocity)
        elif fill_type == 'roll':
            for i in range(8):
                self.hit('snare', time + i * 0.125, 0.1, velocity - i * 3)
        elif fill_type == 'breakcore':
            hits = random.sample(range(8), 6)
            drums = ['snare', 'kick', 'tom_high', 'tom_mid', 'tom_low', 'snare_rim']
            for i, h in enumerate(sorted(hits)):
                d = drums[i % len(drums)]
                self.hit(d, time + h * 0.125, 0.08, velocity - random.randint(0, 15))

def generate_midi(config: dict) -> str:
    """
    Main entry point. Generate a MIDI file from a config dict.
    
    Config structure:
    {
        'tempo': 120,
        'key': 'C',
        'scale': 'major',
        'bars': 16,
        'seed': 42,
        'tracks': [
            {'name': 'melody', 'channel': 0, 'program': 0, 'notes': [...]},
            {'name': 'bass', 'channel': 1, 'program': 33, 'notes': [...]},
        ],
        'drums': {
            'pattern': 'basic_rock',
            'swing': 0.0,
        },
        'output': 'output.mid'
    }
    """
    comp = SonicComposition(
        tempo=config.get('tempo', 120),
        key=config.get('key', 'C'),
        scale=config.get('scale', 'major'),
        seed=config.get('seed')
    )
    
    # Add melodic tracks
    for track_cfg in config.get('tracks', []):
        track = comp.add_track(
            track_cfg['name'],
            track_cfg['channel'],
            track_cfg['program']
        )
        for note_cfg in track_cfg.get('notes', []):
            pitch = note_cfg['pitch']
            time = note_cfg['time']
            duration = note_cfg['duration']
            velocity = note_cfg.get('velocity', 80)
            track.note(pitch, time, duration, velocity)
    
    # Add drums
    if 'drums' in config:
        drum_track = DrumTrack(comp.midi)
        pattern_name = config['drums'].get('pattern', 'basic_rock')
        pattern = DRUM_PATTERNS.get(pattern_name, DRUM_PATTERNS['basic_rock'])
        bars = config.get('bars', 16)
        swing = config['drums'].get('swing', 0.0)
        
        for bar in range(bars):
            bar_time = bar * comp.beats_per_bar
            # Add fills every 4 bars
            if bar % 4 == 3 and bar < bars - 1:
                drum_track.pattern(pattern, bar_time, 16, 100, swing)
                drum_track.fill(bar_time + 3.0, 'basic')
            else:
                drum_track.pattern(pattern, bar_time, 16, 100, swing)
    
    # Save
    output = config.get('output', 'sonicforge_output.mid')
    comp.save(output)
    return output

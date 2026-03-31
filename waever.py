#!/usr/bin/env python3
"""
WÆver — Open Source Music Toolkit
Generate, analyze, and create music from the command line.

Usage:
    python waever.py generate <genre> [options]
    python waever.py analyze <file>
    python waever.py chords --key <key> --progression <name>
    python waever.py info

Genres: orchestral, jazz, trap, lofi, breakcore, metal, rock, ambient

Examples:
    python waever.py generate orchestral --key A --scale minor --mood dramatic
    python waever.py generate trap --tempo 150 --key C# --bars 8
    python waever.py generate jazz --style blues --key Bb
    python waever.py generate breakcore --chaos 0.9 --tempo 200
    python waever.py analyze track.mid
    python waever.py chords --key Am --progression 251
"""

import sys
import os
import json
import argparse

# Add script directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theory import PROGRESSIONS, SCALES, CHORD_TYPES, TEMPO_RANGES, NOTE_NAMES, build_chord

# Genre imports
GENRES = {}
genre_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'genres')
if os.path.isdir(genre_dir):
    sys.path.insert(0, genre_dir)

def load_genres():
    """Dynamically load genre modules."""
    genre_names = ['orchestral', 'jazz', 'trap', 'lofi', 'breakcore', 'metal', 'rock', 'ambient']
    for name in genre_names:
        try:
            GENRES[name] = __import__(name)
        except ImportError:
            pass

def cmd_generate(args):
    """Generate a music piece."""
    load_genres()
    
    genre = args.genre.lower()
    if genre not in GENRES:
        print(f"Unknown genre: {genre}")
        print(f"Available: {', '.join(GENRES.keys())}")
        sys.exit(1)
    
    # Build config from args
    config = {
        'key': args.key,
        'scale': args.scale,
        'bars': args.bars,
        'output': args.output or f"{genre}.mid",
    }
    
    if args.tempo:
        config['tempo'] = args.tempo
    if args.seed:
        config['seed'] = args.seed
    if args.mood:
        config['mood'] = args.mood
    if args.style:
        config['style'] = args.style
    if args.chaos is not None:
        config['chaos'] = args.chaos
    
    print(f"\n🎵 WÆver — Generating {genre.upper()}")
    print(f"   Key: {config['key']} {config['scale']} | Tempo: {config.get('tempo', 'auto')}")
    print(f"   Bars: {config['bars']} | Output: {config['output']}")
    print()
    
    # Generate
    result = GENRES[genre].generate(config)
    
    print(f"✅ Generated: {result['file']}")
    print(f"   Duration: {result['duration_sec']}s | Key: {result['key']} | Tempo: {result['tempo']} BPM")
    print(f"   Instruments: {', '.join(result['instruments'])}")
    
    if args.analyze:
        print(f"\n🔍 Analyzing...")
        from analyze import full_pipeline
        analysis = full_pipeline(result['file'])
        print(f"   Detected tempo: {analysis['tempo_bpm']} BPM")
        print(f"   Detected key: {analysis['key']}")
        print(f"   Energy: {analysis['energy']['rms_mean']:.4f}")
    
    if args.wav:
        print(f"\n🔊 Rendering WAV...")
        from analyze import midi_to_wav
        wav_path = midi_to_wav(result['file'])
        print(f"   WAV: {wav_path}")
    
    print()

def cmd_analyze(args):
    """Analyze an audio or MIDI file."""
    from analyze import full_pipeline, analyze as analyze_file
    
    path = args.file
    if not os.path.exists(path):
        print(f"File not found: {path}")
        sys.exit(1)
    
    print(f"\n🔍 Analyzing: {path}\n")
    
    if path.endswith('.mid') or path.endswith('.midi'):
        result = full_pipeline(path)
    else:
        result = analyze_file(path)
    
    print(f"   Duration: {result['duration_sec']}s")
    print(f"   Tempo: {result['tempo_bpm']} BPM")
    print(f"   Key: {result['key']}")
    print(f"   Energy: {result['energy']['rms_mean']:.4f} (p95: {result['energy']['rms_p95']:.4f})")
    print(f"   Brightness: {result['timbre']['brightness']:.0f} Hz")
    print(f"   Beats: {result['beat_count']}")
    print()

def cmd_chords(args):
    """Show chord progression info."""
    key = args.key
    prog_name = args.progression
    
    print(f"\n🎹 Chord Progressions for {key}\n")
    
    if prog_name:
        if prog_name in PROGRESSIONS:
            prog = PROGRESSIONS[prog_name]
            print(f"  Progression: {prog_name}")
            print(f"  Degrees: {' → '.join(str(d) for d in prog)}")
            print()
            for degree in prog:
                chord = build_chord(key, 'major' if degree in [1, 4, 5] else 'minor', 4)
                chord_names = [f"{key}", f"{key}m", f"{key}m", f"{key}", f"{key}", f"{key}m", f"{key}m", f"{key}dim"]
                idx = degree - 1
                name = chord_names[idx] if idx < len(chord_names) else f"degree {degree}"
                print(f"    {degree}. {name}")
        else:
            print(f"  Unknown progression: {prog_name}")
            print(f"  Available: {', '.join(PROGRESSIONS.keys())}")
    else:
        print("  Available progressions:\n")
        for name, prog in PROGRESSIONS.items():
            print(f"    {name:15} {' → '.join(str(d) for d in prog)}")
    print()

def cmd_info(args):
    """Show available options."""
    load_genres()
    
    print("""
╔══════════════════════════════════════════════╗
║           🎵 WÆVER v1.0 🎵              ║
║        Open Source Music Toolkit             ║
╚══════════════════════════════════════════════╝

GENRES:
  orchestral — Strings, brass, woodwinds, dramatic pieces
  jazz       — Swing, 7th chords, walking bass, saxophone
  trap       — 808 bass, hi-hat rolls, minor scales
  lofi       — Jazzy chords, swing drums, mellow vibes
  breakcore  — Chopped breaks, tempo changes, chaos
  metal      — Power chords, double kick, palm mutes
  rock       — Overdriven guitar, driving drums
  ambient    — Slow pads, drones, minimal percussion

COMMANDS:
  generate <genre>  — Create a MIDI file
  analyze <file>    — Analyze MIDI or WAV
  chords            — Show chord progressions
  info              — This help message

OPTIONS:
  --key <note>      — Root note (C, D, E, F, G, A, B, with # or b)
  --scale <name>    — Scale (major, minor, dorian, blues, etc.)
  --tempo <bpm>     — Tempo override
  --bars <n>        — Number of bars
  --seed <n>        — Random seed for reproducibility
  --output <file>   — Output filename
  --analyze         — Also analyze after generating
  --wav             — Also render to WAV
  --mood <mood>     — Orchestral mood (dramatic, heroic, dark, triumphant)
  --style <style>   — Jazz style (standard, blues, bossa)
  --chaos <0-1>     — Breakcore chaos level

SCALES: """ + ', '.join(SCALES.keys()) + """

PROGRESSIONS: """ + ', '.join(PROGRESSIONS.keys()) + """
""")

def main():
    parser = argparse.ArgumentParser(
        prog='waever',
        description='🎵 WÆver — Open Source Music Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Example: python waever.py generate jazz --key Bb --style blues --bars 16'
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Generate
    gen_parser = subparsers.add_parser('generate', help='Generate a music piece')
    gen_parser.add_argument('genre', help='Genre to generate')
    gen_parser.add_argument('--key', default='C', help='Root note (default: C)')
    gen_parser.add_argument('--scale', default='minor', help='Scale (default: minor)')
    gen_parser.add_argument('--tempo', type=int, help='Tempo BPM')
    gen_parser.add_argument('--bars', type=int, default=16, help='Number of bars (default: 16)')
    gen_parser.add_argument('--seed', type=int, help='Random seed')
    gen_parser.add_argument('--output', '-o', help='Output filename')
    gen_parser.add_argument('--mood', help='Orchestral mood')
    gen_parser.add_argument('--style', help='Jazz style')
    gen_parser.add_argument('--chaos', type=float, help='Breakcore chaos (0-1)')
    gen_parser.add_argument('--analyze', action='store_true', help='Analyze after generating')
    gen_parser.add_argument('--wav', action='store_true', help='Render to WAV after generating')
    
    # Analyze
    an_parser = subparsers.add_parser('analyze', help='Analyze a MIDI or WAV file')
    an_parser.add_argument('file', help='File to analyze')
    
    # Chords
    ch_parser = subparsers.add_parser('chords', help='Show chord progressions')
    ch_parser.add_argument('--key', default='C', help='Root note')
    ch_parser.add_argument('--progression', '-p', help='Specific progression name')
    
    # Info
    subparsers.add_parser('info', help='Show all available options')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        cmd_generate(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'chords':
        cmd_chords(args)
    elif args.command == 'info':
        cmd_info(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

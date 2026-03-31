# 🎵 SonicForge v1.0

**Open Source Music Toolkit** — Generate, analyze, and create music from the command line.

## Features

- **8 Genre Generators:** Orchestral, Jazz, Trap, Lo-fi, Breakcore, Metal, Rock, Ambient
- **Full Pipeline:** Generate MIDI → Render WAV → Analyze audio
- **Music Theory Built-in:** Scales, chords, progressions, voice leading
- **Humanized Output:** Velocity variation, timing swing, groove control
- **Zero Dependencies:** Just Python + midiutil (+ fluidsynth for WAV rendering)

## Quick Start

```bash
pip install midiutil
python sonicforge.py info                    # See all options
python sonicforge.py generate jazz --key Bb  # Generate a jazz piece
python sonicforge.py generate trap --wav     # Generate trap + render WAV
```

## Commands

### Generate
```bash
python sonicforge.py generate <genre> [options]

# Examples:
python sonicforge.py generate orchestral --key A --scale minor --mood dramatic --wav
python sonicforge.py generate jazz --style blues --key Bb --bars 32
python sonicforge.py generate breakcore --chaos 0.9 --tempo 200
python sonicforge.py generate lofi --key C --bars 16
python sonicforge.py generate trap --key C# --bars 8
python sonicforge.py generate metal --key E --tempo 160
python sonicforge.py generate rock --key G --scale major
python sonicforge.py generate ambient --key D --bars 24
```

### Analyze
```bash
python sonicforge.py analyze track.mid   # MIDI → WAV → full analysis
python sonicforge.py analyze track.wav   # WAV → analysis only
```

### Chord Progressions
```bash
python sonicforge.py chords                          # List all progressions
python sonicforge.py chords --key Am --progression 251  # Show ii-V-I in Am
```

## Genres

| Genre | Tempo Range | Key Features |
|-------|-------------|--------------|
| Orchestral | 60-90 | Strings, brass, woodwinds, timpani, dramatic builds |
| Jazz | 100-160 | Swing, 7th chords, walking bass, saxophone, bebop |
| Trap | 130-170 | 808 bass, hi-hat rolls, minor scales, sparse melodies |
| Lo-fi | 70-95 | Jazzy Rhodes, swing drums, ambient pads, mellow vibes |
| Breakcore | 160-220 | Chopped breaks, glitch patterns, controlled chaos |
| Metal | 120-180 | Power chords, double kick, palm mutes, aggression |
| Rock | 110-150 | Overdriven guitar, driving drums, power chords |
| Ambient | 40-70 | Slow pads, drones, minimal percussion, evolving textures |

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--key` | Root note (C, D#, Bb, etc.) | C |
| `--scale` | Scale name | minor |
| `--tempo` | BPM override | Genre default |
| `--bars` | Number of bars | 16 |
| `--seed` | Random seed (for reproducibility) | random |
| `--output` | Output filename | `<genre>.mid` |
| `--wav` | Also render to WAV | off |
| `--analyze` | Also analyze after generating | off |
| `--mood` | Orchestral mood | dramatic |
| `--style` | Jazz style | standard |
| `--chaos` | Breakcore chaos (0-1) | 0.7 |

## Dependencies

**Required:**
- Python 3.8+
- `midiutil` (`pip install midiutil`)

**Optional (for WAV rendering):**
- `fluidsynth` + a soundfont (e.g., FluidR3_GM)

**Optional (for audio analysis):**
- `librosa`, `numpy`, `ffmpeg`

## Architecture

```
sonicforge/
├── sonicforge.py      # CLI entry point
├── core.py            # MIDI generation engine
├── theory.py          # Music theory (scales, chords, progressions)
├── analyze.py         # Audio analysis (librosa wrapper)
└── genres/
    ├── orchestral.py  # Strings, brass, woodwinds
    ├── jazz.py        # Swing, walking bass, sax
    ├── trap.py        # 808, hi-hat rolls, leads
    ├── lofi.py        # Rhodes, swing, ambient
    ├── breakcore.py   # Chopped breaks, glitch
    ├── metal.py       # Power chords, double kick
    ├── rock.py        # Guitar, driving drums
    └── ambient.py     # Pads, drones, minimal
```

## License

MIT — Free to use, modify, and distribute.

## Credits

Built with ❤️ by SonicForge. Powered by midiutil, fluidsynth, and librosa.

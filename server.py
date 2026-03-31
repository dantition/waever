#!/usr/bin/env python3
"""
WÆver — Web UI Server
Flask backend serving the WÆver music toolkit.
"""

import os
import sys
import json
import uuid
import time

# Add waever to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, jsonify, send_file, send_from_directory
from theory import PROGRESSIONS, SCALES, TEMPO_RANGES, CHORD_TYPES, NOTE_NAMES
from analyze import midi_to_wav, analyze as analyze_audio

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Genre modules
GENRES = {}
genre_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'genres')
if os.path.isdir(genre_dir):
    sys.path.insert(0, genre_dir)
    for name in ['orchestral', 'jazz', 'trap', 'lofi', 'breakcore', 'metal', 'rock', 'ambient']:
        try:
            GENRES[name] = __import__(name)
        except ImportError:
            pass

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/genres')
def api_genres():
    genre_info = {
        'orchestral': {'name': 'Orchestral', 'emoji': '🎻', 'desc': 'Strings, brass, woodwinds, dramatic builds',
                       'tempo': (60, 90), 'moods': ['dramatic', 'heroic', 'dark', 'triumphant']},
        'jazz':       {'name': 'Jazz', 'emoji': '🎷', 'desc': 'Swing, 7th chords, walking bass, saxophone',
                       'tempo': (100, 160), 'styles': ['standard', 'blues']},
        'trap':       {'name': 'Trap', 'emoji': '🔊', 'desc': '808 bass, hi-hat rolls, minor scales',
                       'tempo': (130, 170)},
        'lofi':       {'name': 'Lo-fi', 'emoji': '🌙', 'desc': 'Jazzy Rhodes, swing drums, mellow vibes',
                       'tempo': (70, 95)},
        'breakcore':  {'name': 'Breakcore', 'emoji': '💥', 'desc': 'Chopped breaks, glitch patterns, chaos',
                       'tempo': (160, 220), 'chaos': True},
        'metal':      {'name': 'Metal', 'emoji': '🤘', 'desc': 'Power chords, double kick, palm mutes',
                       'tempo': (120, 180)},
        'rock':       {'name': 'Rock', 'emoji': '🎸', 'desc': 'Overdriven guitar, driving drums',
                       'tempo': (110, 150)},
        'ambient':    {'name': 'Ambient', 'emoji': '🌊', 'desc': 'Slow pads, drones, minimal percussion',
                       'tempo': (40, 70)},
    }
    return jsonify(genre_info)

@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.json
    genre = data.get('genre', 'orchestral')
    
    if genre not in GENRES:
        return jsonify({'error': f'Unknown genre: {genre}'}), 400
    
    # Build config
    uid = str(uuid.uuid4())[:8]
    midi_path = os.path.join(OUTPUT_DIR, f'{genre}_{uid}.mid')
    
    config = {
        'key': data.get('key', 'C'),
        'scale': data.get('scale', 'minor'),
        'bars': int(data.get('bars', 16)),
        'output': midi_path,
    }
    
    if data.get('tempo'):
        config['tempo'] = int(data['tempo'])
    if data.get('seed'):
        config['seed'] = int(data['seed'])
    if data.get('mood'):
        config['mood'] = data['mood']
    if data.get('style'):
        config['style'] = data['style']
    if data.get('chaos') is not None:
        config['chaos'] = float(data['chaos'])
    
    try:
        start = time.time()
        result = GENRES[genre].generate(config)
        gen_time = round(time.time() - start, 2)
        
        # Render WAV
        wav_path = midi_to_wav(midi_path)
        
        # Analyze
        analysis = analyze_audio(wav_path)
        
        return jsonify({
            'success': True,
            'midi': f'/output/{os.path.basename(midi_path)}',
            'wav': f'/output/{os.path.basename(wav_path)}',
            'result': result,
            'analysis': analysis,
            'gen_time': gen_time,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chords')
def api_chords():
    key = request.args.get('key', 'C')
    prog = request.args.get('progression')
    
    if prog and prog in PROGRESSIONS:
        degrees = PROGRESSIONS[prog]
        chord_names = []
        for d in degrees:
            quality = 'minor' if d in [2, 3, 6] else 'major'
            if d == 7 and 'major' in key:
                quality = 'dim'
            root_idx = (NOTE_NAMES.index(key.replace('b', '#')) + 
                       SCALES['major' if quality == 'major' else 'minor'][(d-1) % 7]) % 12
            root = NOTE_NAMES[root_idx]
            suffix = 'm' if quality == 'minor' else ('dim' if quality == 'dim' else '')
            chord_names.append(f"{root}{suffix}")
        
        return jsonify({
            'progression': prog,
            'degrees': degrees,
            'chords': chord_names,
        })
    
    # Return all progressions
    return jsonify({'progressions': list(PROGRESSIONS.keys())})

@app.route('/api/scales')
def api_scales():
    return jsonify({'scales': list(SCALES.keys())})

@app.route('/output/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# ============ HTML TEMPLATE ============
HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>WÆver — Weave Your Sound</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg: #0a0a0f;
    --surface: #12121a;
    --surface2: #1a1a25;
    --border: #2a2a3a;
    --text: #e0e0e8;
    --text-dim: #888899;
    --accent: #00d4ff;
    --accent2: #ff6b9d;
    --accent3: #a855f7;
    --success: #22c55e;
    --gradient: linear-gradient(135deg, #00d4ff, #a855f7);
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.6;
}

/* Header */
.header {
    text-align: center;
    padding: 40px 20px 30px;
    background: linear-gradient(180deg, rgba(0,212,255,0.05) 0%, transparent 100%);
    border-bottom: 1px solid var(--border);
}
.header h1 {
    font-size: 2.5rem;
    background: var(--gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}
.header .tagline {
    color: var(--text-dim);
    font-size: 1.1rem;
    margin-top: 8px;
}

/* Container */
.container {
    max-width: 900px;
    margin: 0 auto;
    padding: 30px 20px;
}

/* Genre Grid */
.genre-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin-bottom: 30px;
}
.genre-card {
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}
.genre-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
}
.genre-card.selected {
    border-color: var(--accent);
    background: rgba(0,212,255,0.08);
    box-shadow: 0 0 20px rgba(0,212,255,0.15);
}
.genre-card .emoji { font-size: 2rem; margin-bottom: 8px; }
.genre-card .name { font-weight: 600; font-size: 1.1rem; }
.genre-card .desc { color: var(--text-dim); font-size: 0.8rem; margin-top: 4px; }

/* Controls */
.controls {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.controls h3 {
    color: var(--accent);
    margin-bottom: 16px;
    font-size: 1rem;
}
.control-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
    margin-bottom: 16px;
}
.control-group label {
    display: block;
    color: var(--text-dim);
    font-size: 0.8rem;
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.control-group select,
.control-group input {
    width: 100%;
    padding: 10px 12px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
}
.control-group select:focus,
.control-group input:focus {
    border-color: var(--accent);
}

/* Range slider */
.range-group {
    display: flex;
    align-items: center;
    gap: 12px;
}
.range-group input[type="range"] {
    flex: 1;
    -webkit-appearance: none;
    background: var(--border);
    height: 4px;
    border-radius: 2px;
    border: none;
    padding: 0;
}
.range-group input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 16px;
    height: 16px;
    background: var(--accent);
    border-radius: 50%;
    cursor: pointer;
}
.range-group .value {
    min-width: 40px;
    text-align: right;
    font-weight: 600;
    color: var(--accent);
}

/* Generate button */
.btn-generate {
    width: 100%;
    padding: 16px;
    background: var(--gradient);
    border: none;
    border-radius: 12px;
    color: #fff;
    font-size: 1.1rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.5px;
}
.btn-generate:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,212,255,0.3);
}
.btn-generate:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

/* Loading */
.loading {
    display: none;
    text-align: center;
    padding: 40px;
}
.loading.active { display: block; }
.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Results */
.results {
    display: none;
    margin-top: 20px;
}
.results.active { display: block; }

.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.result-card h3 {
    color: var(--accent);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Audio player */
.audio-player {
    background: var(--surface2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.audio-player audio {
    width: 100%;
    margin-top: 12px;
}

/* Analysis grid */
.analysis-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
}
.analysis-item {
    background: var(--surface2);
    border-radius: 8px;
    padding: 12px;
}
.analysis-item .label {
    color: var(--text-dim);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.analysis-item .value {
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--accent);
    margin-top: 4px;
}

/* Download buttons */
.downloads {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}
.btn-download {
    flex: 1;
    padding: 12px;
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    text-decoration: none;
    text-align: center;
    font-weight: 600;
    transition: all 0.2s;
}
.btn-download:hover {
    border-color: var(--accent);
    color: var(--accent);
}

/* Chord display */
.chord-display {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 12px;
}
.chord-badge {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 1.1rem;
}
.chord-badge .degree {
    color: var(--accent);
    font-size: 0.7rem;
    display: block;
}

/* Footer */
.footer {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-dim);
    font-size: 0.85rem;
    border-top: 1px solid var(--border);
    margin-top: 40px;
}
.footer a { color: var(--accent); text-decoration: none; }

/* Hidden */
.hidden { display: none !important; }

/* Responsive */
@media (max-width: 600px) {
    .header h1 { font-size: 1.8rem; }
    .control-row { grid-template-columns: 1fr 1fr; }
    .genre-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
</head>
<body>

<div class="header">
    <h1>WÆver</h1>
    <p class="tagline">Weave Your Sound — Open Source Music Toolkit</p>
</div>

<div class="container">
    <!-- Genre Selection -->
    <div class="controls">
        <h3>🎵 Choose Your Genre</h3>
        <div class="genre-grid" id="genreGrid"></div>
    </div>

    <!-- Controls -->
    <div class="controls" id="controlsPanel">
        <h3>⚙️ Customize</h3>
        <div class="control-row">
            <div class="control-group">
                <label>Key</label>
                <select id="key">
                    <option>C</option><option>C#</option><option>D</option><option>D#</option>
                    <option>E</option><option>F</option><option>F#</option><option>G</option>
                    <option>G#</option><option selected>A</option><option>A#</option><option>B</option>
                </select>
            </div>
            <div class="control-group">
                <label>Scale</label>
                <select id="scale">
                    <option value="minor" selected>Minor</option>
                    <option value="major">Major</option>
                    <option value="harmonic_minor">Harmonic Minor</option>
                    <option value="dorian">Dorian</option>
                    <option value="mixolydian">Mixolydian</option>
                    <option value="blues">Blues</option>
                    <option value="pentatonic_minor">Pentatonic Minor</option>
                </select>
            </div>
            <div class="control-group">
                <label>Bars</label>
                <div class="range-group">
                    <input type="range" id="bars" min="4" max="64" value="16">
                    <span class="value" id="barsVal">16</span>
                </div>
            </div>
        </div>
        <div class="control-row">
            <div class="control-group">
                <label>Tempo (BPM)</label>
                <div class="range-group">
                    <input type="range" id="tempo" min="40" max="220" value="0">
                    <span class="value" id="tempoVal">auto</span>
                </div>
            </div>
            <div class="control-group hidden" id="moodGroup">
                <label>Mood</label>
                <select id="mood">
                    <option value="dramatic">Dramatic</option>
                    <option value="heroic">Heroic</option>
                    <option value="dark">Dark</option>
                    <option value="triumphant">Triumphant</option>
                </select>
            </div>
            <div class="control-group hidden" id="styleGroup">
                <label>Style</label>
                <select id="style">
                    <option value="standard">Standard</option>
                    <option value="blues">Blues</option>
                </select>
            </div>
            <div class="control-group hidden" id="chaosGroup">
                <label>Chaos</label>
                <div class="range-group">
                    <input type="range" id="chaos" min="0" max="100" value="70">
                    <span class="value" id="chaosVal">0.7</span>
                </div>
            </div>
        </div>
        <div class="control-row">
            <div class="control-group">
                <label>Seed (optional)</label>
                <input type="number" id="seed" placeholder="Random">
            </div>
        </div>
    </div>

    <!-- Generate Button -->
    <button class="btn-generate" id="generateBtn" onclick="generate()">
        🎵 Generate Music
    </button>

    <!-- Loading -->
    <div class="loading" id="loading">
        <div class="spinner"></div>
        <p>Weaving your sound...</p>
    </div>

    <!-- Results -->
    <div class="results" id="results">
        <!-- Audio -->
        <div class="result-card">
            <h3>🎧 Listen</h3>
            <div class="audio-player">
                <audio id="audioPlayer" controls></audio>
            </div>
            <div class="downloads">
                <a class="btn-download" id="dlMidi" href="#">⬇️ MIDI</a>
                <a class="btn-download" id="dlWav" href="#">⬇️ WAV</a>
            </div>
        </div>

        <!-- Info -->
        <div class="result-card">
            <h3>📊 Details</h3>
            <div class="analysis-grid" id="detailsGrid"></div>
        </div>

        <!-- Analysis -->
        <div class="result-card">
            <h3>🔍 Audio Analysis</h3>
            <div class="analysis-grid" id="analysisGrid"></div>
        </div>
    </div>

    <!-- Chord Lookup -->
    <div class="controls" style="margin-top: 30px;">
        <h3>🎹 Chord Progressions</h3>
        <div class="control-row">
            <div class="control-group">
                <label>Key</label>
                <select id="chordKey">
                    <option>C</option><option>C#</option><option>D</option><option>D#</option>
                    <option>E</option><option>F</option><option>F#</option><option>G</option>
                    <option>G#</option><option>A</option><option>A#</option><option>B</option>
                </select>
            </div>
            <div class="control-group">
                <label>Progression</label>
                <select id="chordProg"></select>
            </div>
        </div>
        <button class="btn-generate" onclick="lookupChords()" style="background: var(--surface2); border: 1px solid var(--border);">
            Show Chords
        </button>
        <div class="chord-display" id="chordDisplay"></div>
    </div>
</div>

<div class="footer">
    <p>WÆver — Weave Your Sound</p>
    <p>Open source • <a href="https://github.com/dantition/waever">GitHub</a></p>
</div>

<script>
let selectedGenre = null;
let genres = {};

// Load genres on page load
fetch('/api/genres').then(r => r.json()).then(data => {
    genres = data;
    renderGenres(data);
    loadProgressions();
});

function renderGenres(data) {
    const grid = document.getElementById('genreGrid');
    grid.innerHTML = '';
    for (const [key, info] of Object.entries(data)) {
        const card = document.createElement('div');
        card.className = 'genre-card';
        card.dataset.genre = key;
        card.innerHTML = `
            <div class="emoji">${info.emoji}</div>
            <div class="name">${info.name}</div>
            <div class="desc">${info.desc}</div>
        `;
        card.onclick = () => selectGenre(key);
        grid.appendChild(card);
    }
}

function selectGenre(genre) {
    selectedGenre = genre;
    document.querySelectorAll('.genre-card').forEach(c => c.classList.remove('selected'));
    document.querySelector(`[data-genre="${genre}"]`).classList.add('selected');
    
    const info = genres[genre];
    
    // Show/hide genre-specific controls
    document.getElementById('moodGroup').classList.toggle('hidden', !info.moods);
    document.getElementById('styleGroup').classList.toggle('hidden', !info.styles);
    document.getElementById('chaosGroup').classList.toggle('hidden', !info.chaos);
    
    // Set tempo range
    const tempoSlider = document.getElementById('tempo');
    if (info.tempo) {
        tempoSlider.min = info.tempo[0];
        tempoSlider.max = info.tempo[1];
        tempoSlider.value = Math.round((info.tempo[0] + info.tempo[1]) / 2);
        document.getElementById('tempoVal').textContent = tempoSlider.value;
    }
}

// Range sliders
document.getElementById('bars').oninput = function() {
    document.getElementById('barsVal').textContent = this.value;
};
document.getElementById('tempo').oninput = function() {
    document.getElementById('tempoVal').textContent = this.value > 0 ? this.value : 'auto';
};
document.getElementById('chaos').oninput = function() {
    document.getElementById('chaosVal').textContent = (this.value / 100).toFixed(1);
};

async function generate() {
    if (!selectedGenre) {
        alert('Please select a genre first!');
        return;
    }
    
    const btn = document.getElementById('generateBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Generating...';
    
    document.getElementById('loading').classList.add('active');
    document.getElementById('results').classList.remove('active');
    
    const payload = {
        genre: selectedGenre,
        key: document.getElementById('key').value,
        scale: document.getElementById('scale').value,
        bars: parseInt(document.getElementById('bars').value),
    };
    
    const tempo = parseInt(document.getElementById('tempo').value);
    if (tempo > 0) payload.tempo = tempo;
    
    const seed = document.getElementById('seed').value;
    if (seed) payload.seed = parseInt(seed);
    
    const mood = document.getElementById('mood').value;
    if (!document.getElementById('moodGroup').classList.contains('hidden')) {
        payload.mood = mood;
    }
    
    const style = document.getElementById('style').value;
    if (!document.getElementById('styleGroup').classList.contains('hidden')) {
        payload.style = style;
    }
    
    if (!document.getElementById('chaosGroup').classList.contains('hidden')) {
        payload.chaos = parseFloat(document.getElementById('chaos').value) / 100;
    }
    
    try {
        const res = await fetch('/api/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Set audio
        document.getElementById('audioPlayer').src = data.wav;
        
        // Set downloads
        document.getElementById('dlMidi').href = data.midi;
        document.getElementById('dlWav').href = data.wav;
        
        // Show details
        const details = document.getElementById('detailsGrid');
        details.innerHTML = `
            <div class="analysis-item"><div class="label">Genre</div><div class="value">${genres[selectedGenre].emoji} ${genres[selectedGenre].name}</div></div>
            <div class="analysis-item"><div class="label">Key</div><div class="value">${data.result.key}</div></div>
            <div class="analysis-item"><div class="label">Tempo</div><div class="value">${data.result.tempo} BPM</div></div>
            <div class="analysis-item"><div class="label">Duration</div><div class="value">${data.result.duration_sec}s</div></div>
            <div class="analysis-item"><div class="label">Bars</div><div class="value">${data.result.bars}</div></div>
            <div class="analysis-item"><div class="label">Generated in</div><div class="value">${data.gen_time}s</div></div>
        `;
        
        // Show analysis
        const analysis = document.getElementById('analysisGrid');
        analysis.innerHTML = `
            <div class="analysis-item"><div class="label">Detected Tempo</div><div class="value">${data.analysis.tempo_bpm} BPM</div></div>
            <div class="analysis-item"><div class="label">Detected Key</div><div class="value">${data.analysis.key}</div></div>
            <div class="analysis-item"><div class="label">Energy</div><div class="value">${data.analysis.energy.rms_mean.toFixed(4)}</div></div>
            <div class="analysis-item"><div class="label">Brightness</div><div class="value">${Math.round(data.analysis.timbre.brightness)} Hz</div></div>
            <div class="analysis-item"><div class="label">Beats</div><div class="value">${data.analysis.beat_count}</div></div>
            <div class="analysis-item"><div class="label">Instruments</div><div class="value" style="font-size:0.8rem">${data.result.instruments.join(', ')}</div></div>
        `;
        
        document.getElementById('results').classList.add('active');
        
    } catch(e) {
        alert('Generation failed: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.textContent = '🎵 Generate Music';
        document.getElementById('loading').classList.remove('active');
    }
}

// Chord lookup
async function loadProgressions() {
    const res = await fetch('/api/chords');
    const data = await res.json();
    const select = document.getElementById('chordProg');
    data.progressions.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p;
        opt.textContent = p.replace(/_/g, ' ');
        select.appendChild(opt);
    });
}

async function lookupChords() {
    const key = document.getElementById('chordKey').value;
    const prog = document.getElementById('chordProg').value;
    
    const res = await fetch(`/api/chords?key=${key}&progression=${prog}`);
    const data = await res.json();
    
    const display = document.getElementById('chordDisplay');
    display.innerHTML = '';
    
    if (data.chords) {
        data.chords.forEach((chord, i) => {
            const badge = document.createElement('div');
            badge.className = 'chord-badge';
            badge.innerHTML = `<span class="degree">${data.degrees[i]}</span>${chord}`;
            display.appendChild(badge);
        });
    }
}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print("\n🎵 WÆver Web UI starting...")
    print("   Open: http://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)

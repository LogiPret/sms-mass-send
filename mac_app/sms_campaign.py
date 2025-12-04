#!/usr/bin/env python3
"""
SMS Campaign - Web-based GUI for mass SMS sending on Mac
Dark theme matching iOS app, with visual column mapper
"""

import http.server
import socketserver
import webbrowser
import json
import csv
import subprocess
import os
import sys
import threading
import urllib.request
import urllib.error
from pathlib import Path

# ============================================
# VERSION & AUTO-UPDATE CONFIGURATION
# ============================================
SCRIPT_VERSION = "1.0.2"
GIST_ID = "3e89759cac04be452c935c90b5733eea"  # Will be updated with real ID after creating gist
GIST_RAW_BASE = "https://gist.githubusercontent.com/HugoOtth"
VERSION_URL = f"{GIST_RAW_BASE}/{GIST_ID}/raw/version.json"
SCRIPT_URL = f"{GIST_RAW_BASE}/{GIST_ID}/raw/sms_campaign.py"

# Cache directory for updates
CACHE_DIR = Path.home() / ".sms_campaign"
CACHED_SCRIPT = CACHE_DIR / "sms_campaign.py"

PORT = 8765


def is_newer_version(latest: str, current: str) -> bool:
    """Compare version strings (e.g., '1.0.1' > '1.0.0')"""
    try:
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        while len(latest_parts) < 3:
            latest_parts.append(0)
        while len(current_parts) < 3:
            current_parts.append(0)
        
        for i in range(3):
            if latest_parts[i] > current_parts[i]:
                return True
            if latest_parts[i] < current_parts[i]:
                return False
        return False
    except:
        return False


def check_for_updates() -> dict | None:
    """Check if a newer version is available on the gist"""
    try:
        # Add cache buster
        import time
        cache_buster = int(time.time())
        url = f"{VERSION_URL}?cb={cache_buster}"
        
        req = urllib.request.Request(url, headers={
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        with urllib.request.urlopen(req, timeout=5) as response:
            version_info = json.loads(response.read().decode())
            
            if is_newer_version(version_info.get('version', '0.0.0'), SCRIPT_VERSION):
                return version_info
    except Exception as e:
        print(f"Update check failed: {e}")
    
    return None


def download_update() -> bool:
    """Download the latest script from gist"""
    try:
        import time
        cache_buster = int(time.time())
        url = f"{SCRIPT_URL}?cb={cache_buster}"
        
        req = urllib.request.Request(url, headers={
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        with urllib.request.urlopen(req, timeout=30) as response:
            new_script = response.read().decode()
            
            if len(new_script) < 100:
                print("Downloaded script too short")
                return False
            
            # Ensure cache directory exists
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            
            # Write the new script
            CACHED_SCRIPT.write_text(new_script, encoding='utf-8')
            print(f"Update downloaded to {CACHED_SCRIPT}")
            return True
            
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def run_cached_script():
    """Run the cached (updated) script instead of this one"""
    if CACHED_SCRIPT.exists():
        print(f"Launching updated script: {CACHED_SCRIPT}")
        os.execv(sys.executable, [sys.executable, str(CACHED_SCRIPT)] + sys.argv[1:])


def get_cached_version() -> str | None:
    """Get version from cached script if it exists"""
    if not CACHED_SCRIPT.exists():
        return None
    
    try:
        content = CACHED_SCRIPT.read_text(encoding='utf-8')
        for line in content.split('\n'):
            if line.startswith('SCRIPT_VERSION'):
                # Extract version from: SCRIPT_VERSION = "1.0.2"
                version = line.split('=')[1].strip().strip('"\'')
                return version
    except:
        pass
    return None

# ============================================
# FRENCH CHARACTER FIXES
# ============================================
# Fixes corrupted French accents from latin-1 encoding issues
# The � character appears when encoding is mismatched

KNOWN_REPLACEMENTS = {
    # É at start
    'emilie': 'Émilie',
    'eric': 'Éric',
    'etienne': 'Étienne',
    'eliane': 'Éliane',
    'elise': 'Élise',
    # é in middle
    'stephanie': 'Stéphanie',
    'stephane': 'Stéphane',
    'frederic': 'Frédéric',
    'frederique': 'Frédérique',
    'frederike': 'Frédérike',
    'valerie': 'Valérie',
    'amelie': 'Amélie',
    'melanie': 'Mélanie',
    'helene': 'Hélène',
    'mylene': 'Mylène',
    'veronique': 'Véronique',
    'sebastien': 'Sébastien',
    'cedric': 'Cédric',
    'gerard': 'Gérard',
    'remi': 'Rémi',
    'rene': 'René',
    'andre': 'André',
    'jerome': 'Jérôme',
    'therese': 'Thérèse',
    'genevieve': 'Geneviève',
    'beatrice': 'Béatrice',
    'benedicte': 'Bénédicte',
    # Last names
    'bedard': 'Bédard',
    'bechard': 'Béchard',
    'berube': 'Bérubé',
    'bezeau': 'Bézeau',
    'beaulieu': 'Beaulieu',
    'levesque': 'Lévesque',
    'leveille': 'Léveillé',
    'legare': 'Légaré',
    'leger': 'Léger',
    'lepine': 'Lépine',
    'lemelin': 'Lemelin',
    'menard': 'Ménard',
    'prevost': 'Prévost',
    'theoret': 'Théoret',
    'tetu': 'Têtu',
    'seguin': 'Séguin',
    'senecal': 'Sénécal',
    'gregoire': 'Grégoire',
    'cote': 'Côté',
    'crete': 'Crête',
    'pere': 'Père',
    'mere': 'Mère',
    'desrosiers': 'Desrosiers',
    'francois': 'François',
    'francoise': 'Françoise',
    # Common words in data
    'francais': 'Français',
    'prenom': 'Prénom',
    'adresse': 'Adresse',
    'electronique': 'Électronique',
    'preferee': 'Préférée',
}

import re

def fix_french_accents(text):
    """Fix corrupted French accents (� character) in names"""
    if not text or not isinstance(text, str):
        return text
    
    # Check if text contains the corruption character
    if '�' not in text:
        return text
    
    # Try to match against known names first
    clean_text = text.replace('�', '')
    lower_clean = clean_text.lower()
    
    for plain, accented in KNOWN_REPLACEMENTS.items():
        if lower_clean == plain:
            return accented
    
    # Specific pattern replacements for common corruptions
    replacements = [
        # Names starting with É
        (r'^�milie$', 'Émilie'),
        (r'^�ric$', 'Éric'),
        (r'^�tienne$', 'Étienne'),
        (r'^�liane$', 'Éliane'),
        (r'^�lise$', 'Élise'),
        
        # Stéphane/Stéphanie
        (r'St�phan', 'Stéphan'),
        (r'St�ph', 'Stéph'),
        
        # Common names with �
        (r'B�dard', 'Bédard'),
        (r'G�rard', 'Gérard'),
        (r'S�bastien', 'Sébastien'),
        (r'C�dric', 'Cédric'),
        (r'R�mi', 'Rémi'),
        (r'R�gis', 'Régis'),
        (r'D�nis', 'Dénis'),
        (r'B�atrice', 'Béatrice'),
        (r'Th�r�se', 'Thérèse'),
        (r'H�l�ne', 'Hélène'),
        (r'Genevi�ve', 'Geneviève'),
        (r'V�ronique', 'Véronique'),
        (r'Val�rie', 'Valérie'),
        (r'Am�lie', 'Amélie'),
        (r'M�lanie', 'Mélanie'),
        (r'Myl�ne', 'Mylène'),
        (r'Fr�d�ric', 'Frédéric'),
        (r'Fr�d�rique', 'Frédérique'),
        (r'Fran�ois', 'François'),
        (r'Fran�oise', 'Françoise'),
        (r'Fran�ais', 'Français'),
        
        # Header/column words
        (r'Pr�nom', 'Prénom'),
        (r'Pr�f�r�e', 'Préférée'),
        (r'�lectronique', 'Électronique'),
        (r'Adresse_�lec', 'Adresse_Élec'),
        (r'Langue_Pr�f', 'Langue_Préf'),
        
        # Last names
        (r'L�vesque', 'Lévesque'),
        (r'L�ger', 'Léger'),
        (r'L�pine', 'Lépine'),
        (r'M�nard', 'Ménard'),
        (r'S�guin', 'Séguin'),
        (r'S�n�cal', 'Sénécal'),
        (r'Pr�vost', 'Prévost'),
        (r'Th�oret', 'Théoret'),
        (r'Gr�goire', 'Grégoire'),
        (r'B�rub�', 'Bérubé'),
        (r'L�gar�', 'Légaré'),
        (r'C�t�', 'Côté'),
        (r'T�tu', 'Têtu'),
        (r'Cr�te', 'Crête'),
        
        # Patterns ending in -ière
        (r'li�re\b', 'lière'),
        (r'ti�re\b', 'tière'),
        (r'ni�re\b', 'nière'),
        (r'ri�re\b', 'rière'),
        (r'mi�re\b', 'mière'),
        (r'pi�re\b', 'pière'),
        (r'vi�re\b', 'vière'),
        (r'ci�re\b', 'cière'),
        (r'di�re\b', 'dière'),
        (r'si�re\b', 'sière'),
        (r'gi�re\b', 'gière'),
        
        # é at end after consonant (René, André, etc.)
        (r'n�\b', 'né'),
        (r'r�\b', 'ré'),
        (r'l�\b', 'lé'),
        (r't�\b', 'té'),
        (r'd�\b', 'dé'),
        (r's�\b', 'sé'),
        (r'm�\b', 'mé'),
        
        # è patterns (before re, ve, le, ne at end of word)
        (r'�ve\b', 'ève'),
        (r'�le\b', 'èle'),
        (r'�ne\b', 'ène'),
        (r'�me\b', 'ème'),
        (r'�te\b', 'ète'),
        (r'�se\b', 'èse'),
        (r'�ce\b', 'èce'),
        (r'�de\b', 'ède'),
        (r'�ge\b', 'ège'),
        (r'�pe\b', 'èpe'),
        (r'�re\b', 'ère'),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Default: remaining � is probably é
    text = text.replace('�', 'é')
    
    return text

HTML_PAGE = '''<!DOCTYPE html>
<html>
<head>
    <title>SMS Campaign</title>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro", sans-serif;
            background: #1c1c1e;
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            font-size: 22px;
            margin-bottom: 5px;
        }
        h2 {
            font-size: 16px;
            margin: 20px 0 10px 0;
            color: #fff;
        }
        .step-indicator {
            color: #0a84ff;
            font-size: 12px;
            margin-bottom: 15px;
            font-weight: 500;
        }
        .description {
            color: #8e8e93;
            margin-bottom: 20px;
            font-size: 14px;
            line-height: 1.5;
        }
        
        /* Info box */
        .info-box {
            background: #2c2c2e;
            padding: 12px 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            font-size: 13px;
            color: #8e8e93;
        }
        .info-box strong { color: #fff; }
        
        /* Stats */
        .stats {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat {
            padding: 15px 20px;
            border-radius: 12px;
            text-align: center;
            flex: 1;
        }
        .stat.valid {
            background: #1a3d1a;
            border: 1px solid #30d158;
        }
        .stat.skip {
            background: #3d1a1a;
            border: 1px solid #ff453a;
        }
        .stat .num {
            font-size: 28px;
            font-weight: bold;
        }
        .stat .label {
            font-size: 11px;
            color: #8e8e93;
            text-transform: uppercase;
            margin-top: 5px;
        }
        
        /* File drop */
        .file-drop {
            border: 2px dashed #3a3a3c;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
            background: #2c2c2e;
        }
        .file-drop:hover {
            border-color: #0a84ff;
            background: #1a1a1c;
        }
        .file-drop.has-file {
            border-color: #30d158;
            background: #1a3d1a;
        }
        .file-icon { font-size: 40px; margin-bottom: 10px; }
        .file-name { color: #30d158; font-weight: 600; margin-top: 10px; }
        
        /* Column Mapper */
        .column-mapper {
            background: #2c2c2e;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .mapper-header {
            display: flex;
            background: #3a3a3c;
            font-size: 11px;
            font-weight: 600;
            color: #8e8e93;
            text-transform: uppercase;
        }
        .mapper-header > div {
            padding: 12px 10px;
            flex: 1;
            border-right: 1px solid #4a4a4c;
            text-align: center;
        }
        .mapper-header > div:last-child { border-right: none; }
        .mapper-row {
            display: flex;
            border-bottom: 1px solid #3a3a3c;
        }
        .mapper-row:last-child { border-bottom: none; }
        .mapper-cell {
            flex: 1;
            padding: 10px;
            font-size: 13px;
            border-right: 1px solid #3a3a3c;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            text-align: center;
        }
        .mapper-cell:last-child { border-right: none; }
        .mapper-cell.header-cell {
            background: #1c1c1e;
            color: #0a84ff;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .mapper-cell.header-cell:hover {
            background: #0a84ff22;
        }
        .mapper-cell.header-cell.selected-name {
            background: #30d15833;
            color: #30d158;
        }
        .mapper-cell.header-cell.selected-phone {
            background: #ff9f0a33;
            color: #ff9f0a;
        }
        .mapper-cell.data-cell {
            color: #8e8e93;
        }
        
        /* Mapping instructions */
        .mapping-legend {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            font-size: 13px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        .legend-dot.name { background: #30d158; }
        .legend-dot.phone { background: #ff9f0a; }
        .mapping-mode {
            background: #0a84ff;
            color: #fff;
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 10px;
        }
        
        /* Textarea */
        textarea {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 12px;
            font-size: 15px;
            background: #2c2c2e;
            color: #fff;
            min-height: 140px;
            resize: vertical;
            font-family: inherit;
            line-height: 1.5;
        }
        textarea:focus {
            outline: 2px solid #0a84ff;
        }
        textarea::placeholder {
            color: #5a5a5e;
        }
        
        /* Buttons */
        .btn {
            padding: 12px 25px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #0a84ff;
            color: white;
        }
        .btn-primary:hover { background: #0070e0; }
        .btn-secondary {
            background: #3a3a3c;
            color: #fff;
        }
        .btn-secondary:hover { background: #4a4a4c; }
        .btn-success {
            background: #30d158;
            color: #fff;
        }
        .btn-success:hover { background: #28b84c; }
        .btn:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }
        
        .nav-buttons {
            display: flex;
            justify-content: space-between;
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #3a3a3c;
        }
        
        /* Preview table */
        .preview-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-bottom: 15px;
        }
        .preview-table th, .preview-table td {
            padding: 10px 8px;
            text-align: left;
            border-bottom: 1px solid #3a3a3c;
        }
        .preview-table th {
            background: #2c2c2e;
            color: #8e8e93;
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
        }
        .preview-table .phone {
            font-family: "SF Mono", Monaco, monospace;
            color: #0a84ff;
        }
        .preview-table .source {
            color: #30d158;
            font-size: 11px;
        }
        .preview-table .error {
            color: #ff453a;
        }
        .scroll-container {
            max-height: 220px;
            overflow-y: auto;
            border-radius: 10px;
            background: #2c2c2e;
        }
        
        /* Message preview */
        .message-preview {
            background: #2c2c2e;
            padding: 15px;
            border-radius: 10px;
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 14px;
        }
        .var {
            background: #0a84ff33;
            color: #0a84ff;
            padding: 2px 6px;
            border-radius: 4px;
        }
        
        /* Progress */
        .progress-container {
            background: #3a3a3c;
            border-radius: 10px;
            height: 8px;
            margin: 20px 0;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #0a84ff, #30d158);
            transition: width 0.3s;
            border-radius: 10px;
        }
        
        /* Log */
        .log {
            background: #1a1a1c;
            font-family: "SF Mono", Monaco, monospace;
            font-size: 12px;
            padding: 15px;
            border-radius: 10px;
            max-height: 300px;
            overflow-y: auto;
            line-height: 1.8;
        }
        .log-success { color: #30d158; }
        .log-error { color: #ff453a; }
        
        /* Insert button */
        .insert-btn {
            background: #3a3a3c;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            color: #fff;
            margin-bottom: 10px;
        }
        .insert-btn:hover { background: #4a4a4c; }
        
        .char-count {
            text-align: right;
            color: #5a5a5e;
            font-size: 12px;
            margin-top: 8px;
        }
        
        /* Language toggle */
        .lang-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            background: #2c2c2e;
            border-radius: 8px;
            overflow: hidden;
            font-size: 13px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .lang-btn {
            padding: 10px 18px;
            border: none;
            background: transparent;
            color: #8e8e93;
            cursor: pointer;
            transition: all 0.2s;
        }
        .lang-btn.active {
            background: #0a84ff;
            color: #fff;
        }
        .lang-btn:hover:not(.active) {
            background: #3a3a3c;
        }
        
        input[type="file"] { display: none; }
        
        /* Phone priority list */
        .priority-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 12px 15px;
            background: #2c2c2e;
            border-radius: 8px;
            margin-bottom: 8px;
            cursor: grab;
            transition: all 0.2s;
            border: 1px solid #3a3a3c;
        }
        .priority-item:hover {
            background: #3a3a3c;
        }
        .priority-item.dragging {
            opacity: 0.5;
            cursor: grabbing;
        }
        .priority-item .priority-num {
            background: #ff9f0a;
            color: #000;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
        }
        .priority-item .priority-name {
            flex: 1;
            font-weight: 500;
        }
        .priority-item .priority-handle {
            color: #5a5a5e;
            font-size: 16px;
        }
        
        .footer-debug {
            margin-top: 20px;
            padding: 15px;
            background: #2a2a2c;
            border-radius: 10px;
            text-align: center;
            color: #5a5a5e;
            font-size: 12px;
        }
        
        /* Quit button */
        .quit-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            background: #ff3b30;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(255,59,48,0.3);
            transition: all 0.2s;
            z-index: 1000;
        }
        .quit-btn:hover {
            background: #ff453a;
            transform: translateY(-1px);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Step 1: Select CSV -->
        <div id="step1">
            <div class="step-indicator" data-i18n="step1of4">Étape 1 sur 4</div>
            <h1><span data-i18n="selectFile">Sélectionner le fichier CSV</span></h1>
            <p class="description" data-i18n="selectFileDesc">Choisissez un fichier CSV contenant vos contacts avec noms et numéros de téléphone.</p>
            
            <div class="file-drop" id="fileDrop" onclick="document.getElementById('csvFile').click()">
                <div class="file-icon">📄</div>
                <div data-i18n="clickToSelect">Cliquez pour sélectionner un fichier CSV</div>
                <div class="file-name" id="fileName"></div>
            </div>
            <input type="file" id="csvFile" accept=".csv" onchange="handleFile(this)">
            
            <div class="nav-buttons">
                <div></div>
                <button class="btn btn-primary" id="next1" disabled onclick="goToStep(2)" data-i18n="next">Suivant →</button>
            </div>
        </div>
        
        <!-- Step 2: Map Columns -->
        <div id="step2" style="display:none">
            <div class="step-indicator" data-i18n="step2of4">Étape 2 sur 4</div>
            <h1><span data-i18n="mapColumns">Mapper les colonnes</span></h1>
            <p class="description" data-i18n="mapColumnsDesc">Cliquez sur les en-têtes de colonnes pour les assigner. Premier clic = Nom, Deuxième clic = Téléphone.</p>
            
            <div class="mapping-legend">
                <div class="legend-item">
                    <div class="legend-dot name"></div>
                    <span data-i18n="nameColumn">Colonne Nom</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot phone"></div>
                    <span data-i18n="phoneColumn">Colonne Téléphone</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div id="mappingMode" class="mapping-mode" data-i18n="clickName">Cliquez sur la colonne NOM</div>
                <button class="btn btn-secondary" style="padding: 8px 12px; font-size: 12px;" onclick="resetMapping()" data-i18n="resetMapping">Réinitialiser</button>
            </div>
            
            <div class="column-mapper" id="columnMapper"></div>
            
            <div class="info-box">
                <span data-i18n="foundContacts">Trouvé</span> <strong id="contactCount">0</strong> <span data-i18n="contacts">contacts</span>
            </div>
            
            <!-- Multi-phone priority section (hidden by default) -->
            <div id="phonePrioritySection" style="display:none; margin-top: 15px;">
                <div class="info-box" style="background: #2a4a2a; border: 1px solid #30d158;">
                    <strong><span data-i18n="multiPhoneDetected">Plusieurs colonnes téléphone détectées!</span></strong><br>
                    <span style="font-size: 12px;" data-i18n="multiPhoneHelp">Glissez pour réordonner la priorité. Le premier numéro disponible sera utilisé.</span>
                </div>
                <div id="phonePriorityList" style="margin-top: 10px;"></div>
            </div>
            
            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="goToStep(1)" data-i18n="back">← Retour</button>
                <button class="btn btn-primary" id="next2" disabled onclick="goToStep(3)" data-i18n="next">Suivant →</button>
            </div>
        </div>
        
        <!-- Step 3: Compose Message -->
        <div id="step3" style="display:none">
            <div class="step-indicator" data-i18n="step3of4">Étape 3 sur 4</div>
            <h1><span data-i18n="composeMessage">Composer le message</span></h1>
            <p class="description" data-i18n="composeDesc">Écrivez votre message. Utilisez {name} pour personnaliser avec le nom du destinataire.</p>
            
            <button class="insert-btn" onclick="insertName()" data-i18n="insertName">Insérer Prénom</button>
            <textarea id="message" data-placeholder-i18n="typemessage" placeholder="Tapez votre message ici..." oninput="updateCharCount()"></textarea>
            <div class="char-count"><span id="charCount">0</span> <span data-i18n="characters">caractères</span></div>
            
            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="goToStep(2)" data-i18n="back">← Retour</button>
                <button class="btn btn-primary" onclick="preparePreview()" data-i18n="next">Suivant →</button>
            </div>
        </div>
        
        <!-- Step 4: Preview (Debug-style) -->
        <div id="step4" style="display:none">
            <div class="step-indicator" data-i18n="step4of4">Étape 4 sur 4</div>
            <h1><span data-i18n="previewSend">Aperçu & Envoi</span></h1>
            
            <div class="stats">
                <div class="stat valid">
                    <div class="num" id="validCount">0</div>
                    <div class="label" data-i18n="valid">Valides</div>
                </div>
                <div class="stat skip">
                    <div class="num" id="skipCount">0</div>
                    <div class="label" data-i18n="skipped">Ignorés</div>
                </div>
            </div>
            
            <h2 data-i18n="validContacts">Contacts valides</h2>
            <div class="scroll-container">
                <table class="preview-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th data-i18n="name">Nom</th>
                            <th data-i18n="phone">Téléphone</th>
                            <th data-i18n="source">Source</th>
                        </tr>
                    </thead>
                    <tbody id="validList"></tbody>
                </table>
            </div>
            
            <div id="skippedSection" style="display:none">
                <h2 data-i18n="skippedContacts">Contacts ignorés</h2>
                <div class="scroll-container">
                    <table class="preview-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th data-i18n="reason">Raison</th>
                                <th data-i18n="rawData">Données brutes</th>
                            </tr>
                        </thead>
                        <tbody id="skipList"></tbody>
                    </table>
                </div>
            </div>
            
            <h2><span data-i18n="messagePreview">Aperçu du message</span></h2>
            <div class="message-preview" id="messagePreview"></div>
            
            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="goToStep(3)" data-i18n="back">← Retour</button>
                <button class="btn btn-success" onclick="startSending()" data-i18n="sendAll">Envoyer tous les SMS</button>
            </div>
        </div>
        
        <!-- Step 5: Sending -->
        <div id="step5" style="display:none">
            <h1><span data-i18n="sending">Envoi en cours...</span></h1>
            <p class="description" id="sendStatus" data-i18n="preparing">Préparation de l'envoi...</p>
            
            <div class="progress-container">
                <div class="progress-bar" id="progressBar" style="width:0%"></div>
            </div>
            
            <div class="log" id="sendLog"></div>
            
            <div class="nav-buttons" id="doneButtons" style="display:none">
                <div></div>
                <button class="btn btn-primary" onclick="window.close()" data-i18n="done">Terminé</button>
            </div>
        </div>
    </div>
    
    <!-- Quit Button -->
    <button class="quit-btn" onclick="quitApp()" data-i18n="stopCampaign">Arrêter la campagne</button>
    
    <!-- Language Toggle -->
    <div class="lang-toggle">
        <button class="lang-btn" id="btnEN" onclick="setLang('en')">EN</button>
        <button class="lang-btn active" id="btnFR" onclick="setLang('fr')">FR</button>
    </div>
    
    <script>
        // ============ TRANSLATIONS ============
        const translations = {
            en: {
                step1of4: "Step 1 of 4",
                step2of4: "Step 2 of 4",
                step3of4: "Step 3 of 4",
                step4of4: "Step 4 of 4",
                selectFile: "Select CSV File",
                selectFileDesc: "Choose a CSV file containing your contacts with names and phone numbers.",
                clickToSelect: "Click to select CSV file",
                next: "Next →",
                back: "← Back",
                mapColumns: "Map Columns",
                mapColumnsDesc: "Click on column headers to assign them. First click = Name, Second click = Phone.",
                nameColumn: "Name Column",
                phoneColumn: "Phone Column",
                clickName: "Click the NAME column",
                clickPhone: "Now click the PHONE column",
                clickPhoneMulti: "Click a PHONE column (or use priority below)",
                mappingDone: "Mapping complete!",
                resetMapping: "Reset",
                multiPhoneDetected: "Multiple phone columns detected!",
                multiPhoneHelp: "Drag to reorder priority. First available number will be used.",
                foundContacts: "Found",
                contacts: "contacts",
                composeMessage: "Compose Message",
                composeDesc: "Write your message. Use {name} to personalize with recipient's name.",
                insertName: "Insert First Name",
                typemessage: "Type your message here...",
                characters: "characters",
                previewSend: "Preview & Send",
                valid: "Valid",
                skipped: "Skipped",
                validContacts: "Valid Contacts",
                skippedContacts: "Skipped Contacts",
                name: "Name",
                phone: "Phone",
                source: "Source",
                reason: "Reason",
                rawData: "Raw Data",
                messagePreview: "Message Preview",
                sendAll: "Send All SMS",
                stopCampaign: "Stop Campaign",
                sending: "Sending Messages...",
                preparing: "Preparing to send...",
                done: "Done",
                noPhone: "No phone number",
                noName: "No name",
                confirmSend: "Send {count} SMS messages?",
                sendingProgress: "Sending {current} of {total}...",
                complete: "Complete! Sent: {sent}, Failed: {failed}",
                updateAvailable: "Update Available"
            },
            fr: {
                step1of4: "Étape 1 sur 4",
                step2of4: "Étape 2 sur 4",
                step3of4: "Étape 3 sur 4",
                step4of4: "Étape 4 sur 4",
                selectFile: "Sélectionner le fichier CSV",
                selectFileDesc: "Choisissez un fichier CSV contenant vos contacts avec noms et numéros de téléphone.",
                clickToSelect: "Cliquez pour sélectionner un fichier CSV",
                next: "Suivant →",
                back: "← Retour",
                mapColumns: "Mapper les colonnes",
                mapColumnsDesc: "Cliquez sur les en-têtes de colonnes pour les assigner. Premier clic = Nom, Deuxième clic = Téléphone.",
                nameColumn: "Colonne Nom",
                phoneColumn: "Colonne Téléphone",
                clickName: "Cliquez sur la colonne NOM",
                clickPhone: "Maintenant cliquez sur la colonne TÉLÉPHONE",
                clickPhoneMulti: "Cliquez sur une colonne TÉLÉPHONE (ou utilisez la priorité ci-dessous)",
                mappingDone: "Mapping terminé!",
                resetMapping: "Réinitialiser",
                multiPhoneDetected: "Plusieurs colonnes téléphone détectées!",
                multiPhoneHelp: "Glissez pour réordonner la priorité. Le premier numéro disponible sera utilisé.",
                foundContacts: "Trouvé",
                contacts: "contacts",
                composeMessage: "Composer le message",
                composeDesc: "Écrivez votre message. Utilisez {name} pour personnaliser avec le nom du destinataire.",
                insertName: "Insérer Prénom",
                typemessage: "Tapez votre message ici...",
                characters: "caractères",
                previewSend: "Aperçu & Envoi",
                valid: "Valides",
                skipped: "Ignorés",
                validContacts: "Contacts valides",
                skippedContacts: "Contacts ignorés",
                name: "Nom",
                phone: "Téléphone",
                source: "Source",
                reason: "Raison",
                rawData: "Données brutes",
                messagePreview: "Aperçu du message",
                sendAll: "Envoyer tous les SMS",
                stopCampaign: "Arrêter la campagne",
                sending: "Envoi en cours...",
                preparing: "Préparation de l'envoi...",
                done: "Terminé",
                noPhone: "Pas de numéro",
                noName: "Pas de nom",
                confirmSend: "Envoyer {count} messages SMS?",
                sendingProgress: "Envoi {current} sur {total}...",
                complete: "Terminé! Envoyés: {sent}, Échoués: {failed}",
                updateAvailable: "Mise à jour disponible"
            }
        };
        
        let currentLang = 'fr';
        
        function setLang(lang) {
            currentLang = lang;
            document.getElementById('btnEN').classList.toggle('active', lang === 'en');
            document.getElementById('btnFR').classList.toggle('active', lang === 'fr');
            
            // Update all elements with data-i18n
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (translations[lang][key]) {
                    el.textContent = translations[lang][key];
                }
            });
            
            // Update placeholders
            document.querySelectorAll('[data-placeholder-i18n]').forEach(el => {
                const key = el.getAttribute('data-placeholder-i18n');
                if (translations[lang][key]) {
                    el.placeholder = translations[lang][key];
                }
            });
        }
        
        function t(key, replacements = {}) {
            let text = translations[currentLang][key] || key;
            for (const [k, v] of Object.entries(replacements)) {
                text = text.replace('{' + k + '}', v);
            }
            return text;
        }
        
        // ============ FRENCH ACCENT FIXES ============
        const knownReplacements = {
            'emilie': 'Émilie', 'eric': 'Éric', 'etienne': 'Étienne', 'eliane': 'Éliane', 'elise': 'Élise',
            'stephanie': 'Stéphanie', 'stephane': 'Stéphane', 'frederic': 'Frédéric', 'frederique': 'Frédérique',
            'valerie': 'Valérie', 'amelie': 'Amélie', 'melanie': 'Mélanie', 'helene': 'Hélène', 'mylene': 'Mylène',
            'veronique': 'Véronique', 'sebastien': 'Sébastien', 'cedric': 'Cédric', 'gerard': 'Gérard',
            'remi': 'Rémi', 'rene': 'René', 'andre': 'André', 'jerome': 'Jérôme', 'therese': 'Thérèse',
            'genevieve': 'Geneviève', 'beatrice': 'Béatrice', 'benedicte': 'Bénédicte',
            'bedard': 'Bédard', 'bechard': 'Béchard', 'berube': 'Bérubé', 'bezeau': 'Bézeau',
            'levesque': 'Lévesque', 'leveille': 'Léveillé', 'legare': 'Légaré', 'leger': 'Léger',
            'lepine': 'Lépine', 'menard': 'Ménard', 'prevost': 'Prévost', 'theoret': 'Théoret',
            'tetu': 'Têtu', 'seguin': 'Séguin', 'senecal': 'Sénécal', 'gregoire': 'Grégoire',
            'cote': 'Côté', 'crete': 'Crête', 'pere': 'Père', 'mere': 'Mère',
            'francois': 'François', 'francoise': 'Françoise',
            'francais': 'Français', 'prenom': 'Prénom', 'adresse': 'Adresse',
            'electronique': 'Électronique', 'preferee': 'Préférée'
        };
        
        function fixFrenchAccents(text) {
            if (!text || typeof text !== 'string' || !text.includes('�')) return text;
            
            // Try known names first
            let cleanText = text.replace(/�/g, '').toLowerCase();
            if (knownReplacements[cleanText]) return knownReplacements[cleanText];
            
            // Pattern replacements
            const patterns = [
                [/^�milie$/i, 'Émilie'], [/^�ric$/i, 'Éric'], [/^�tienne$/i, 'Étienne'],
                [/St�phan/gi, 'Stéphan'], [/St�ph/gi, 'Stéph'], [/B�dard/gi, 'Bédard'],
                [/G�rard/gi, 'Gérard'], [/S�bastien/gi, 'Sébastien'], [/C�dric/gi, 'Cédric'],
                [/R�mi/gi, 'Rémi'], [/B�atrice/gi, 'Béatrice'], [/Th�r�se/gi, 'Thérèse'],
                [/H�l�ne/gi, 'Hélène'], [/Genevi�ve/gi, 'Geneviève'], [/V�ronique/gi, 'Véronique'],
                [/Val�rie/gi, 'Valérie'], [/Am�lie/gi, 'Amélie'], [/M�lanie/gi, 'Mélanie'],
                [/Myl�ne/gi, 'Mylène'], [/Fr�d�ric/gi, 'Frédéric'], [/Fr�d�rique/gi, 'Frédérique'],
                [/Fran�ois/gi, 'François'], [/Fran�oise/gi, 'Françoise'],
                [/Fran�ais/gi, 'Français'], [/Pr�nom/gi, 'Prénom'], [/Pr�f�r�e/gi, 'Préférée'],
                [/�lectronique/gi, 'Électronique'], [/Adresse_�lec/gi, 'Adresse_Élec'],
                [/L�vesque/gi, 'Lévesque'], [/L�ger/gi, 'Léger'], [/L�pine/gi, 'Lépine'],
                [/M�nard/gi, 'Ménard'], [/S�guin/gi, 'Séguin'], [/S�n�cal/gi, 'Sénécal'],
                [/Pr�vost/gi, 'Prévost'], [/Th�oret/gi, 'Théoret'], [/Gr�goire/gi, 'Grégoire'],
                [/B�rub�/gi, 'Bérubé'], [/L�gar�/gi, 'Légaré'], [/C�t�/gi, 'Côté'],
                [/T�tu/gi, 'Têtu'], [/Cr�te/gi, 'Crête'],
                // -ière endings
                [/li�re\\b/gi, 'lière'], [/ti�re\\b/gi, 'tière'], [/ni�re\\b/gi, 'nière'],
                [/ri�re\\b/gi, 'rière'], [/mi�re\\b/gi, 'mière'], [/vi�re\\b/gi, 'vière'],
                // é at end (René, André)
                [/n�\\b/g, 'né'], [/r�\\b/g, 'ré'], [/l�\\b/g, 'lé'], [/t�\\b/g, 'té'],
                [/d�\\b/g, 'dé'], [/s�\\b/g, 'sé'], [/m�\\b/g, 'mé'],
                // è patterns (before consonant+e at end)
                [/�ve\\b/gi, 'ève'], [/�le\\b/gi, 'èle'], [/�ne\\b/gi, 'ène'],
                [/�re\\b/gi, 'ère'], [/�me\\b/gi, 'ème'], [/�te\\b/gi, 'ète']
            ];
            
            for (const [pattern, replacement] of patterns) {
                text = text.replace(pattern, replacement);
            }
            
            // Default: remaining � is probably é
            return text.replace(/�/g, 'é');
        }
        
        // ============ DATA ============
        let csvData = [];
        let headers = [];
        let recipients = [];
        let skipped = [];
        let nameCol = -1;
        let phoneCol = -1;
        let phoneCols = []; // Array of {index, name} for multi-phone columns
        let phonePriorityOrder = []; // User-defined priority order
        let mappingStep = 0; // 0 = select name, 1 = select phone, 2 = done
        
        // Phone column keywords for auto-detection
        const phoneKeywords = ['phone', 'mobile', 'cell', 'telephone', 'tel', 'work', 'home', 'maison', 'travail', 'bureau', 'cellulaire', 'domicile'];
        
        // ============ FILE HANDLING ============
        function handleFile(input) {
            const file = input.files[0];
            if (!file) return;
            
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('fileDrop').classList.add('has-file');
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const text = e.target.result;
                const lines = text.split(/\\r?\\n/).filter(line => line.trim());
                
                // Detect separator
                const firstLine = lines[0];
                const semicolons = (firstLine.match(/;/g) || []).length;
                const commas = (firstLine.match(/,/g) || []).length;
                const separator = semicolons > commas ? ';' : ',';
                
                // Parse and fix French accents in headers
                headers = parseCSVLine(lines[0], separator).map(h => fixFrenchAccents(h));
                
                // Parse data rows and fix French accents in all values
                csvData = lines.slice(1).map((line, idx) => ({
                    lineNumber: idx + 2,
                    values: parseCSVLine(line, separator).map(v => fixFrenchAccents(v))
                }));
                
                document.getElementById('contactCount').textContent = csvData.length;
                document.getElementById('next1').disabled = false;
                
                // Reset mapping
                nameCol = -1;
                phoneCol = -1;
                mappingStep = 0;
                
                // Build column mapper
                buildColumnMapper();
            };
            reader.readAsText(file);
        }
        
        function parseCSVLine(line, separator = ',') {
            const result = [];
            let current = '';
            let inQuotes = false;
            for (let char of line) {
                if (char === '"') inQuotes = !inQuotes;
                else if (char === separator && !inQuotes) { result.push(current.trim()); current = ''; }
                else current += char;
            }
            result.push(current.trim());
            return result;
        }
        
        // ============ COLUMN MAPPER ============
        function detectPhoneColumns() {
            // Detect all columns that look like phone columns
            phoneCols = [];
            const mobileKeywords = ['mobile', 'cell', 'cellulaire', 'cellular', 'portable'];
            const workKeywords = ['work', 'travail', 'bureau', 'office', 'business', 'professionnel'];
            const homeKeywords = ['home', 'maison', 'domicile', 'residence', 'personnel'];
            const genericKeywords = ['phone', 'telephone', 'tel', 'numero', 'number'];
            
            headers.forEach((header, idx) => {
                const h = header.toLowerCase();
                let type = null;
                
                if (mobileKeywords.some(k => h.includes(k))) type = 'mobile';
                else if (workKeywords.some(k => h.includes(k))) type = 'work';
                else if (homeKeywords.some(k => h.includes(k))) type = 'home';
                else if (genericKeywords.some(k => h.includes(k))) type = 'phone';
                
                if (type) {
                    phoneCols.push({ index: idx, name: header, type: type });
                }
            });
            
            // Set default priority order (mobile first, then work, then home, then generic)
            const typePriority = ['mobile', 'work', 'home', 'phone'];
            phoneCols.sort((a, b) => typePriority.indexOf(a.type) - typePriority.indexOf(b.type));
            phonePriorityOrder = phoneCols.map(c => c.index);
            
            return phoneCols;
        }
        
        function buildPhonePriorityList() {
            const container = document.getElementById('phonePriorityList');
            let html = '';
            
            phonePriorityOrder.forEach((colIdx, priority) => {
                const col = phoneCols.find(c => c.index === colIdx);
                if (!col) return;
                
                const typeLabel = col.type === 'mobile' ? 'Mobile' : col.type === 'work' ? 'Work' : col.type === 'home' ? 'Home' : 'Phone';
                html += `<div class="priority-item" draggable="true" data-col="${colIdx}">
                    <div class="priority-num">${priority + 1}</div>
                    <div class="priority-name"><span style="color:#8e8e93;font-size:11px;">[${typeLabel}]</span> ${col.name}</div>
                    <div class="priority-handle">☰</div>
                </div>`;
            });
            
            container.innerHTML = html;
            
            // Add drag and drop handlers
            const items = container.querySelectorAll('.priority-item');
            items.forEach(item => {
                item.addEventListener('dragstart', handleDragStart);
                item.addEventListener('dragover', handleDragOver);
                item.addEventListener('drop', handleDrop);
                item.addEventListener('dragend', handleDragEnd);
            });
        }
        
        let draggedItem = null;
        
        function handleDragStart(e) {
            draggedItem = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        }
        
        function handleDragOver(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
        }
        
        function handleDrop(e) {
            e.preventDefault();
            if (draggedItem !== this) {
                // Get current positions
                const container = document.getElementById('phonePriorityList');
                const items = [...container.querySelectorAll('.priority-item')];
                const draggedIdx = items.indexOf(draggedItem);
                const targetIdx = items.indexOf(this);
                
                // Reorder in DOM
                if (draggedIdx < targetIdx) {
                    this.parentNode.insertBefore(draggedItem, this.nextSibling);
                } else {
                    this.parentNode.insertBefore(draggedItem, this);
                }
                
                // Update priority order array
                updatePriorityFromDOM();
            }
        }
        
        function handleDragEnd() {
            this.classList.remove('dragging');
            draggedItem = null;
        }
        
        function updatePriorityFromDOM() {
            const container = document.getElementById('phonePriorityList');
            const items = container.querySelectorAll('.priority-item');
            phonePriorityOrder = [];
            
            items.forEach((item, idx) => {
                const colIdx = parseInt(item.dataset.col);
                phonePriorityOrder.push(colIdx);
                // Update priority number display
                item.querySelector('.priority-num').textContent = idx + 1;
            });
        }
        
        function buildColumnMapper() {
            const mapper = document.getElementById('columnMapper');
            const maxCols = Math.min(headers.length, 6); // Show max 6 columns
            const previewRows = Math.min(csvData.length, 3); // Show 3 data rows
            
            let html = '<div class="mapper-header">';
            for (let i = 0; i < maxCols; i++) {
                html += `<div>${headers[i].substring(0, 15)}</div>`;
            }
            html += '</div>';
            
            // Header row (clickable)
            html += '<div class="mapper-row">';
            for (let i = 0; i < maxCols; i++) {
                html += `<div class="mapper-cell header-cell" data-col="${i}" onclick="selectColumn(${i})">${headers[i]}</div>`;
            }
            html += '</div>';
            
            // Data rows
            for (let r = 0; r < previewRows; r++) {
                html += '<div class="mapper-row">';
                for (let i = 0; i < maxCols; i++) {
                    const val = csvData[r].values[i] || '';
                    html += `<div class="mapper-cell data-cell">${val.substring(0, 20)}</div>`;
                }
                html += '</div>';
            }
            
            mapper.innerHTML = html;
            
            // Detect phone columns
            detectPhoneColumns();
            
            // Show priority section if multiple phone columns detected
            const prioritySection = document.getElementById('phonePrioritySection');
            if (phoneCols.length > 1) {
                prioritySection.style.display = 'block';
                buildPhonePriorityList();
            } else {
                prioritySection.style.display = 'none';
            }
            
            updateMappingMode();
        }
        
        function selectColumn(col) {
            if (mappingStep === 0) {
                // Selecting name column
                nameCol = col;
                mappingStep = 1;
                
                // If multiple phone columns detected, enable Next right away (user can use priority)
                if (phoneCols.length > 1) {
                    document.getElementById('next2').disabled = false;
                }
            } else if (mappingStep === 1 || (mappingStep === 2 && phoneCols.length > 1 && phoneCol === -1)) {
                // Selecting phone column (or overriding in multi-phone mode)
                if (col === nameCol) return; // Can't select same column
                phoneCol = col;
                mappingStep = 2;
                
                // If in multi-phone mode, move selected column to top of priority
                if (phoneCols.length > 1) {
                    const idx = phonePriorityOrder.indexOf(col);
                    if (idx > 0) {
                        phonePriorityOrder.splice(idx, 1);
                        phonePriorityOrder.unshift(col);
                        buildPhonePriorityList();
                    }
                }
                
                document.getElementById('next2').disabled = false;
            }
            
            // Update visual state
            document.querySelectorAll('.header-cell').forEach(cell => {
                cell.classList.remove('selected-name', 'selected-phone');
                const c = parseInt(cell.dataset.col);
                if (c === nameCol) cell.classList.add('selected-name');
                if (c === phoneCol) cell.classList.add('selected-phone');
            });
            
            updateMappingMode();
        }
        
        function resetMapping() {
            nameCol = -1;
            phoneCol = -1;
            mappingStep = 0;
            document.getElementById('next2').disabled = true;
            
            // Remove all selection classes
            document.querySelectorAll('.header-cell').forEach(cell => {
                cell.classList.remove('selected-name', 'selected-phone');
            });
            
            updateMappingMode();
        }
        
        function updateMappingMode() {
            const mode = document.getElementById('mappingMode');
            if (mappingStep === 0) {
                mode.textContent = t('clickName');
                mode.style.background = '#30d158';
            } else if (mappingStep === 1) {
                // If multiple phone columns, show different message
                if (phoneCols.length > 1) {
                    mode.textContent = t('clickPhoneMulti') || 'Click a PHONE column (or use priority below)';
                    mode.style.background = '#ff9f0a';
                } else {
                    mode.textContent = t('clickPhone');
                    mode.style.background = '#ff9f0a';
                }
            } else {
                mode.textContent = t('mappingDone');
                mode.style.background = '#0a84ff';
            }
        }
        
        // ============ NAVIGATION ============
        function goToStep(n) {
            for (let i = 1; i <= 5; i++) {
                document.getElementById('step' + i).style.display = i === n ? 'block' : 'none';
            }
            if (n === 2) {
                buildColumnMapper();
            }
        }
        
        // ============ MESSAGE ============
        function insertName() {
            const ta = document.getElementById('message');
            const pos = ta.selectionStart;
            const text = ta.value;
            ta.value = text.slice(0, pos) + '{name} ' + text.slice(pos);
            updateCharCount();
            ta.focus();
        }
        
        function updateCharCount() {
            const len = document.getElementById('message').value.length;
            document.getElementById('charCount').textContent = len;
        }
        
        // ============ PHONE PARSING ============
        // Priority: mobile > cell > work > home > unknown
        const phonePriority = ['mobile', 'cell', 'cellular', 'work', 'travail', 'home', 'maison', 'domicile'];
        
        function extractBestPhone(rawPhone) {
            if (!rawPhone || !rawPhone.trim()) {
                return { phone: '', source: 'empty' };
            }
            
            const raw = rawPhone.trim();
            
            // Check if it contains multiple phones (has | separator or : type indicator)
            if (raw.includes('|') || raw.includes(':')) {
                // Format: "4389266456 : work | 5798819696 : home | 4389266456 : mobile"
                const parts = raw.split('|').map(p => p.trim()).filter(p => p);
                const phones = [];
                
                for (const part of parts) {
                    // Parse "number : type" or "number ext: xxx : type"
                    let number = '';
                    let type = 'unknown';
                    
                    if (part.includes(':')) {
                        const segments = part.split(':').map(s => s.trim());
                        
                        if (segments.length >= 2) {
                            // Last segment is usually the type
                            const lastSeg = segments[segments.length - 1].toLowerCase();
                            
                            // Check if last segment is a phone type
                            if (phonePriority.some(p => lastSeg.includes(p)) || lastSeg === 'unknown') {
                                type = lastSeg;
                                // Number is everything before the type, excluding 'ext' parts
                                number = segments[0];
                            } else if (segments.length >= 3 && segments[1].toLowerCase().startsWith('ext')) {
                                // Format: "number ext: 123 : type"
                                type = lastSeg;
                                number = segments[0];
                            } else {
                                // Just take first segment as number
                                number = segments[0];
                            }
                        }
                    } else {
                        number = part;
                    }
                    
                    // Clean the number - only digits
                    const digits = number.replace(/\\D/g, '');
                    if (digits.length >= 10) {
                        phones.push({ number: digits, type: type });
                    }
                }
                
                if (phones.length === 0) {
                    return { phone: '', source: 'no valid phones' };
                }
                
                // Find best phone by priority
                for (const priority of phonePriority) {
                    for (const p of phones) {
                        if (p.type.includes(priority)) {
                            return { phone: formatPhone(p.number), source: p.type };
                        }
                    }
                }
                
                // No priority match, return first one
                return { phone: formatPhone(phones[0].number), source: phones[0].type + ' (first)' };
            }
            
            // Single phone number - just clean it
            const digits = raw.replace(/\\D/g, '');
            if (digits.length >= 10) {
                return { phone: formatPhone(digits), source: 'single' };
            }
            
            return { phone: '', source: 'invalid' };
        }
        
        function formatPhone(digits) {
            // Ensure proper format: +1XXXXXXXXXX
            if (digits.length === 10) {
                return '+1' + digits;
            } else if (digits.length === 11 && digits.startsWith('1')) {
                return '+' + digits;
            } else if (digits.length > 11) {
                // Take last 10 digits if too long
                return '+1' + digits.slice(-10);
            }
            return '+1' + digits;
        }
        
        // ============ PREVIEW ============
        function preparePreview() {
            const msg = document.getElementById('message').value.trim();
            if (!msg) { alert(currentLang === 'fr' ? 'Veuillez entrer un message' : 'Please enter a message'); return; }
            
            recipients = [];
            skipped = [];
            
            csvData.forEach(row => {
                const rawName = row.values[nameCol] || '';
                
                // Get phone based on whether we have multiple phone columns or single selection
                let phone = '';
                let source = '';
                
                if (phoneCols.length > 1 && phonePriorityOrder.length > 0) {
                    // Multi-phone column mode: use priority order
                    for (const colIdx of phonePriorityOrder) {
                        const rawPhone = row.values[colIdx] || '';
                        if (rawPhone.trim()) {
                            const result = extractBestPhone(rawPhone);
                            if (result.phone) {
                                phone = result.phone;
                                const col = phoneCols.find(c => c.index === colIdx);
                                source = col ? col.name : result.source;
                                break; // Found a valid phone, stop looking
                            }
                        }
                    }
                    if (!phone) {
                        source = 'no phone in priority cols';
                    }
                } else {
                    // Single phone column mode
                    const rawPhone = row.values[phoneCol] || '';
                    const result = extractBestPhone(rawPhone);
                    phone = result.phone;
                    source = result.source;
                }
                
                // Fix French accents in name
                const name = fixFrenchAccents(rawName.trim());
                
                if (!phone) {
                    skipped.push({
                        lineNumber: row.lineNumber,
                        reason: t('noPhone'),
                        raw: name + ' | ' + rawPhone.substring(0, 40)
                    });
                } else if (!name) {
                    skipped.push({
                        lineNumber: row.lineNumber,
                        reason: t('noName'),
                        raw: phone
                    });
                } else {
                    recipients.push({
                        lineNumber: row.lineNumber,
                        name: name,
                        phone: phone,
                        phoneSource: source,
                        message: msg.replace(/{name}/g, name)
                    });
                }
            });
            
            // Update stats
            document.getElementById('validCount').textContent = recipients.length;
            document.getElementById('skipCount').textContent = skipped.length;
            
            // Populate valid list - show ALL entries for quick verification
            const validList = document.getElementById('validList');
            validList.innerHTML = recipients.map(r => `
                <tr>
                    <td>${r.lineNumber}</td>
                    <td>${r.name}</td>
                    <td class="phone">${r.phone}</td>
                    <td class="source">${r.phoneSource || ''}</td>
                </tr>
            `).join('');
            
            // Populate skipped list
            if (skipped.length > 0) {
                document.getElementById('skippedSection').style.display = 'block';
                document.getElementById('skipList').innerHTML = skipped.map(s => `
                    <tr>
                        <td>${s.lineNumber}</td>
                        <td class="error">${s.reason}</td>
                        <td style="color:#5a5a5e">${s.raw.substring(0, 30)}</td>
                    </tr>
                `).join('');
            } else {
                document.getElementById('skippedSection').style.display = 'none';
            }
            
            // Message preview
            let preview = msg;
            if (recipients.length > 0) {
                preview = msg.replace(/{name}/g, `<span class="var">${recipients[0].name}</span>`);
            }
            document.getElementById('messagePreview').innerHTML = preview;
            
            goToStep(4);
        }
        
        // ============ SENDING ============
        async function startSending() {
            if (!confirm(t('confirmSend', {count: recipients.length}))) return;
            goToStep(5);
            
            const log = document.getElementById('sendLog');
            const progress = document.getElementById('progressBar');
            const status = document.getElementById('sendStatus');
            let sent = 0, failed = 0;
            
            for (let i = 0; i < recipients.length; i++) {
                const r = recipients[i];
                status.textContent = t('sendingProgress', {current: i + 1, total: recipients.length});
                progress.style.width = ((i + 1) / recipients.length * 100) + '%';
                
                try {
                    const resp = await fetch('/send', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({phone: r.phone, message: r.message, name: r.name})
                    });
                    const result = await resp.json();
                    
                    if (result.success) {
                        sent++;
                        log.innerHTML += `<div class="log-success">✓ ${r.name} (${r.phone})</div>`;
                    } else {
                        failed++;
                        log.innerHTML += `<div class="log-error">✗ ${r.name} (${r.phone})</div>`;
                    }
                } catch (e) {
                    failed++;
                    log.innerHTML += `<div class="log-error">✗ ${r.name} - Error</div>`;
                }
                log.scrollTop = log.scrollHeight;
            }
            
            status.textContent = t('complete', {sent: sent, failed: failed});
            document.getElementById('doneButtons').style.display = 'flex';
        }
        
        // ============ SHUTDOWN ON CLOSE ============
        function quitApp() {
            fetch('/shutdown').then(() => window.close());
        }
        
        window.addEventListener('beforeunload', function() {
            navigator.sendBeacon('/shutdown');
        });
        
        window.addEventListener('unload', function() {
            navigator.sendBeacon('/shutdown');
        });
        
        // ============ AUTO-UPDATE ============
        async function checkUpdate() {
            try {
                const resp = await fetch('/check-update');
                const data = await resp.json();
                if (data.hasUpdate) {
                    showUpdateModal(data);
                }
            } catch(e) {
                console.log('Update check failed:', e);
            }
        }
        
        function showUpdateModal(data) {
            const modal = document.createElement('div');
            modal.id = 'updateModal';
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.8); display: flex;
                align-items: center; justify-content: center; z-index: 9999;
            `;
            
            const content = document.createElement('div');
            content.style.cssText = `
                background: #2c2c2e; padding: 30px; border-radius: 16px;
                max-width: 400px; text-align: center; color: #fff;
            `;
            
            const title = translations[currentLang].updateAvailable || 'Mise à jour disponible';
            const updateBtn = currentLang === 'fr' ? 'Mettre à jour' : 'Update';
            const laterBtn = currentLang === 'fr' ? 'Plus tard' : 'Later';
            const current = currentLang === 'fr' ? 'Version actuelle' : 'Current version';
            const newVer = currentLang === 'fr' ? 'Nouvelle version' : 'New version';
            
            content.innerHTML = \`
                <h2 style="margin-bottom: 15px;">🔄 \${title}</h2>
                <p style="color: #888; margin-bottom: 10px;">\${current}: \${data.currentVersion}</p>
                <p style="color: #30d158; font-weight: bold; margin-bottom: 15px;">\${newVer}: \${data.latestVersion}</p>
                \${data.changelog ? \`<p style="color: #aaa; font-size: 14px; margin-bottom: 20px;">\${data.changelog}</p>\` : ''}
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button onclick="applyUpdate()" style="
                        background: #30d158; color: #000; border: none; padding: 12px 24px;
                        border-radius: 8px; font-weight: bold; cursor: pointer;
                    ">\${updateBtn}</button>
                    <button onclick="closeUpdateModal()" style="
                        background: #48484a; color: #fff; border: none; padding: 12px 24px;
                        border-radius: 8px; cursor: pointer;
                    ">\${laterBtn}</button>
                </div>
            \`;
            
            modal.appendChild(content);
            document.body.appendChild(modal);
        }
        
        function closeUpdateModal() {
            const modal = document.getElementById('updateModal');
            if (modal) modal.remove();
        }
        
        async function applyUpdate() {
            const modal = document.getElementById('updateModal');
            if (modal) {
                modal.querySelector('div').innerHTML = \`
                    <h2 style="margin-bottom: 15px;">⏳ \${currentLang === 'fr' ? 'Téléchargement...' : 'Downloading...'}</h2>
                    <p style="color: #888;">\${currentLang === 'fr' ? 'Veuillez patienter' : 'Please wait'}</p>
                \`;
            }
            
            try {
                const resp = await fetch('/apply-update', { method: 'POST' });
                const data = await resp.json();
                
                if (data.success) {
                    if (modal) {
                        modal.querySelector('div').innerHTML = \`
                            <h2 style="margin-bottom: 15px;">✅ \${currentLang === 'fr' ? 'Mise à jour installée!' : 'Update installed!'}</h2>
                            <p style="color: #888; margin-bottom: 20px;">\${currentLang === 'fr' ? 'Relancez l'"'"'application' : 'Please restart the application'}</p>
                            <button onclick="quitApp()" style="
                                background: #30d158; color: #000; border: none; padding: 12px 24px;
                                border-radius: 8px; font-weight: bold; cursor: pointer;
                            ">\${currentLang === 'fr' ? 'Quitter' : 'Quit'}</button>
                        \`;
                    }
                } else {
                    if (modal) {
                        modal.querySelector('div').innerHTML = \`
                            <h2 style="margin-bottom: 15px;">❌ \${currentLang === 'fr' ? 'Erreur' : 'Error'}</h2>
                            <p style="color: #ff453a;">\${data.error || 'Unknown error'}</p>
                            <button onclick="closeUpdateModal()" style="
                                background: #48484a; color: #fff; border: none; padding: 12px 24px;
                                border-radius: 8px; cursor: pointer; margin-top: 15px;
                            ">OK</button>
                        \`;
                    }
                }
            } catch(e) {
                console.error('Update failed:', e);
                closeUpdateModal();
            }
        }
        
        // Check for updates on page load
        setTimeout(checkUpdate, 1000);
    </script>
</body>
</html>'''


class SMSHandler(http.server.SimpleHTTPRequestHandler):
    pending_update = None
    current_version = SCRIPT_VERSION
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == '/shutdown':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            # Shutdown server in background thread
            threading.Thread(target=self.server.shutdown, daemon=True).start()
        elif self.path == '/check-update':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            if SMSHandler.pending_update:
                response = {
                    'hasUpdate': True,
                    'currentVersion': SMSHandler.current_version,
                    'latestVersion': SMSHandler.pending_update.get('version', '?'),
                    'changelog': SMSHandler.pending_update.get('changelog', '')
                }
            else:
                response = {'hasUpdate': False}
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/send':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            
            success = send_via_applescript(data['phone'], data['message'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success}).encode())
        
        elif self.path == '/apply-update':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            try:
                if download_update():
                    response = {'success': True}
                else:
                    response = {'success': False, 'error': 'Download failed'}
            except Exception as e:
                response = {'success': False, 'error': str(e)}
            
            self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        pass


def send_via_applescript(phone, message):
    """Send a single SMS using AppleScript and Messages app"""
    escaped_message = message.replace('\\', '\\\\').replace('"', '\\"')
    
    # Use SMS service instead of iMessage to ensure delivery to non-iMessage users
    applescript = f'''
    tell application "Messages"
        set targetService to 1st account whose service type = SMS
        set targetBuddy to participant "{phone}" of targetService
        send "{escaped_message}" to targetBuddy
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error sending to {phone}: {e}")
        return False


class ReusableTCPServer(socketserver.TCPServer):
    """TCP Server that allows port reuse immediately after shutdown"""
    allow_reuse_address = True


def check_and_apply_updates() -> bool:
    """
    Check for updates and handle them.
    Returns True if we should exit (update applied), False to continue.
    """
    # First, check if there's a newer cached version we should use
    cached_version = get_cached_version()
    if cached_version and is_newer_version(cached_version, SCRIPT_VERSION):
        # We're running an old version but a newer one is cached
        # If we're not already running FROM the cache, switch to it
        current_script = Path(sys.argv[0]).resolve() if sys.argv else None
        if current_script != CACHED_SCRIPT.resolve():
            print(f"Newer cached version found ({cached_version} > {SCRIPT_VERSION}), launching it...")
            run_cached_script()
            return True  # Won't reach here due to exec
    
    # Check online for updates
    update_info = check_for_updates()
    if update_info:
        latest_version = update_info.get('version', '?')
        changelog = update_info.get('changelog', '')
        print(f"Update available: {latest_version} (current: {SCRIPT_VERSION})")
        
        # Return update info to show in UI
        return update_info
    
    return None


def main():
    # Check for updates before starting
    update_info = check_and_apply_updates()
    
    # Kill any existing process on the port
    os.system(f"lsof -ti:{PORT} | xargs kill -9 2>/dev/null")
    
    # Small delay to ensure port is released
    import time
    time.sleep(0.5)
    
    # Store update info for the handler to access
    SMSHandler.pending_update = update_info
    SMSHandler.current_version = SCRIPT_VERSION
    
    with ReusableTCPServer(("", PORT), SMSHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"SMS Campaign v{SCRIPT_VERSION} running at {url}")
        print("Press Ctrl+C to stop")
        
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()


if __name__ == "__main__":
    main()

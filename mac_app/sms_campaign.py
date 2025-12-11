#!/usr/bin/env python3
"""
SMS Campaign - Mac App v2.1.0
Beautiful dark UI matching the iOS app design.
"""

import subprocess
import json
import csv
import re
import os
import sys
import uuid
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError
from io import StringIO
import time
import ssl
import webview  # Import at top level for PyInstaller

# Create SSL context that doesn't verify certificates (needed for PyInstaller bundled apps)
SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

# ============================================================================
# VERSION & CONFIG
# ============================================================================

VERSION = "2.4.10"
BUILD = 1

CONFIG = {
    "webhook_url": "https://n8n-wwfb.onrender.com/webhook/05313c1f-7d0c-47db-bd5c-4ec846fda513",
    "gist_id": "3e89759cac04be452c935c90b5733eea",
    "update_url": "https://gist.githubusercontent.com/hugootth/3e89759cac04be452c935c90b5733eea/raw/version.json",
    "download_url": "https://github.com/LogiPret/sms-mass-send/releases/latest/download/SMS.Campaign.zip",
    "keychain_service": "com.logipret.sms-campaign",
    "keychain_auth_key": "sms_auth_code",
    "keychain_device_key": "sms_device_id",
    "phone_columns": ["phone", "phones", "telephone", "tel", "mobile", "cell", "numero", "numéro", "phone_number", "phone_numbers"],
    "name_columns": ["name", "nom", "client", "customer", "contact"],
    "firstname_columns": ["first_name", "firstname", "first", "prenom", "prénom"],
    "lastname_columns": ["last_name", "lastname", "last", "nom", "nom_famille", "family_name", "surname"],
    "phone_separators": ["|", ";", ",", "/", " "],
    "message_delay": 3.0
}

# Known French accent replacements (using escape sequences to avoid encoding issues)
KNOWN_REPLACEMENTS = {
    "\xc3\xa9": "é", "\xc3\xa8": "è", "\xc3\xa0": "à", "\xc3\xa2": "â", "\xc3\xae": "î",
    "\xc3\xb4": "ô", "\xc3\xbb": "û", "\xc3\xa7": "ç", "\xc3\xb9": "ù", "\xc3\xaa": "ê",
    "\xc3\xab": "ë", "\xc3\xaf": "ï", "\xc3\xbc": "ü", "\xc5\x93": "œ", "\xc3\x89": "É",
    "\xc3\x88": "È", "\xc3\x80": "À", "\xc3\x82": "Â", "\xc3\x8e": "Î", "\xc3\x94": "Ô",
    "\xc3\x9b": "Û", "\xc3\x87": "Ç", "\xc3\x99": "Ù", "\xc3\x8a": "Ê", "\xc3\x8b": "Ë",
    "\xc3\x8f": "Ï", "\xc3\x9c": "Ü", "\xc5\x92": "Œ", "\xe2\x80\x99": "'", "\xe2\x80\x9c": '"',
    "\xe2\x80\x9d": '"', "\xe2\x80\x94": "—", "\xe2\x80\x93": "–", "\xe2\x80\xa6": "…", "\xc2": "",
}

# ============================================================================
# BEAUTIFUL DARK UI - HTML/CSS/JS (Multi-screen wizard with i18n)
# ============================================================================

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SMS Campaign</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #000000;
            --bg-secondary: #1c1c1e;
            --bg-tertiary: #2c2c2e;
            --bg-card: #1c1c1e;
            --text-primary: #ffffff;
            --text-secondary: #8e8e93;
            --accent: #0a84ff;
            --accent-hover: #409cff;
            --success: #30d158;
            --warning: #ff9f0a;
            --error: #ff453a;
            --border: #38383a;
            --input-bg: #1c1c1e;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            overflow: hidden;
        }
        
        .container { max-width: 1000px; margin: 0 auto; padding: 16px; }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
        }
        
        .header-left { display: flex; align-items: center; gap: 12px; }
        .logo { font-size: 36px; }
        .title {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), #5e5ce6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .version { color: var(--text-secondary); font-size: 11px; }
        
        .lang-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 4px;
            background: var(--bg-tertiary);
            border-radius: 8px;
            padding: 4px;
        }
        
        .lang-btn {
            padding: 6px 12px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }
        
        .lang-btn.active {
            background: var(--accent);
            color: white;
        }
        
        .card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
        }
        
        .card-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-title .step-num {
            background: var(--accent);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: 700;
        }
        
        .form-group { margin-bottom: 20px; }
        
        label {
            display: block;
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        input[type="text"], textarea, select {
            width: 100%;
            padding: 14px 16px;
            font-size: 16px;
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            transition: all 0.2s;
            font-family: inherit;
        }
        
        textarea::placeholder, input::placeholder {
            color: #4a4a4c;
            opacity: 1;
        }
        
        input:focus, textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.2); }
        textarea { min-height: 120px; resize: none; }
        
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 14px 28px;
            font-size: 16px;
            font-weight: 600;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            font-family: inherit;
        }
        
        .btn-full { width: 100%; }
        .btn-primary { background: var(--accent); color: white; }
        .btn-primary:hover { background: var(--accent-hover); }
        .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
        .btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); }
        .btn-success { background: var(--success); color: white; }
        .btn-danger { background: var(--error); color: white; }
        .btn-small { padding: 8px 14px; font-size: 13px; border-radius: 8px; }
        
        .file-input-wrapper {
            position: relative;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            border: 2px dashed var(--border);
            border-radius: 16px;
            background: var(--bg-tertiary);
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .file-input-wrapper:hover { border-color: var(--accent); background: rgba(10, 132, 255, 0.1); }
        .file-input-wrapper.has-file { border-color: var(--success); background: rgba(48, 209, 88, 0.1); }
        .file-input-wrapper input { position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer; }
        .file-icon { font-size: 48px; margin-bottom: 12px; }
        .file-text { color: var(--text-secondary); font-size: 14px; }
        .file-name { color: var(--success); font-weight: 600; margin-top: 8px; }
        
        .contacts-table-wrapper {
            max-height: 350px;
            overflow-y: auto;
            margin-top: 16px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }
        
        .contacts-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        
        .contacts-table th, .contacts-table td {
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        .contacts-table th {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
        }
        
        .contacts-table tr:last-child td { border-bottom: none; }
        
        .contacts-table .status-valid { color: var(--success); }
        .contacts-table .status-skipped { color: var(--error); }
        .contacts-table .reason { color: var(--error); font-size: 11px; }
        .contacts-table .phone-source { color: var(--success); font-size: 11px; }
        .contacts-table .raw-data { color: var(--text-secondary); font-size: 11px; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        
        .dashboard-stats {
            display: flex;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .dashboard-stat {
            flex: 1;
            padding: 16px;
            border-radius: 12px;
            text-align: center;
        }
        
        .dashboard-stat.valid {
            background: rgba(48, 209, 88, 0.15);
            border: 1px solid var(--success);
        }
        
        .dashboard-stat.skipped {
            background: rgba(255, 69, 58, 0.15);
            border: 1px solid var(--error);
        }
        
        .dashboard-stat .num {
            font-size: 28px;
            font-weight: 700;
        }
        
        .dashboard-stat .label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-top: 4px;
        }
        
        .section-title {
            font-size: 14px;
            font-weight: 600;
            margin: 16px 0 8px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .separator-info {
            background: var(--bg-tertiary);
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 16px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .separator-info strong { color: var(--text-primary); }
        
        .phone-tag {
            display: inline-block;
            padding: 3px 8px;
            background: var(--bg-tertiary);
            border-radius: 5px;
            font-size: 12px;
            margin: 2px;
            font-family: 'SF Mono', Monaco, monospace;
        }
        
        .var-buttons {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        
        .var-btn {
            padding: 8px 14px;
            background: linear-gradient(135deg, var(--accent), #5e5ce6);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .var-btn:hover { transform: translateY(-1px); opacity: 0.9; }
        
        .message-preview {
            background: var(--bg-tertiary);
            padding: 16px;
            border-radius: 12px;
            font-size: 15px;
            line-height: 1.6;
            white-space: pre-wrap;
            margin-top: 16px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
            padding: 16px;
            background: var(--bg-tertiary);
            border-radius: 12px;
        }
        
        .stat-value { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
        .stat-value.success { color: var(--success); }
        .stat-value.error { color: var(--error); }
        .stat-value.warning { color: var(--warning); }
        .stat-label { font-size: 12px; color: var(--text-secondary); text-transform: uppercase; }
        
        .btn-group { display: flex; gap: 12px; margin-top: 20px; }
        .btn-group .btn { flex: 1; }
        
        .progress-container { margin: 24px 0; }
        .progress-bar { height: 8px; background: var(--bg-tertiary); border-radius: 4px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent), #5e5ce6); border-radius: 4px; transition: width 0.3s; }
        .progress-text { display: flex; justify-content: space-between; margin-top: 8px; font-size: 14px; color: var(--text-secondary); }
        
        .log-container {
            max-height: 360px;
            overflow-y: auto;
            background: var(--bg-tertiary);
            border-radius: 12px;
            padding: 12px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 12px;
        }
        
        .log-entry { padding: 6px 0; border-bottom: 1px solid var(--border); display: flex; align-items: flex-start; gap: 8px; }
        .log-entry:last-child { border-bottom: none; }
        .log-time { color: var(--text-secondary); font-size: 10px; white-space: nowrap; }
        .log-message { flex: 1; }
        
        /* Confirmation Modal */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(4px);
        }
        
        .modal {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
            max-width: 400px;
            width: 90%;
            animation: modalIn 0.2s ease-out;
        }
        
        @keyframes modalIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        
        .modal-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .modal-message {
            color: var(--text-secondary);
            font-size: 14px;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .modal-buttons {
            display: flex;
            gap: 12px;
        }
        
        .modal-buttons .btn { flex: 1; }
        
        .btn-warning { background: var(--warning); color: #000; }
        .btn-warning:hover { opacity: 0.9; }
        
        .alert { padding: 14px; border-radius: 12px; margin-bottom: 16px; display: flex; align-items: flex-start; gap: 10px; }
        .alert-error { background: rgba(255, 69, 58, 0.15); border: 1px solid rgba(255, 69, 58, 0.3); }
        .alert-success { background: rgba(48, 209, 88, 0.15); border: 1px solid rgba(48, 209, 88, 0.3); }
        .alert-icon { font-size: 18px; }
        .alert-content { flex: 1; }
        .alert-title { font-weight: 600; margin-bottom: 2px; }
        .alert-message { font-size: 13px; color: var(--text-secondary); }
        
        .hidden { display: none !important; }
        .fade-in { animation: fadeIn 0.3s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: scale(0.98) translateY(8px); } to { opacity: 1; transform: scale(1) translateY(0); } }
        
        .card { transition: all 0.25s ease-out; }
        
        .spinner { width: 20px; height: 20px; border: 2px solid transparent; border-top-color: currentColor; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        .update-banner {
            background: linear-gradient(135deg, var(--accent), #5e5ce6);
            padding: 10px 14px;
            border-radius: 10px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
            font-size: 14px;
        }
        
        .update-banner .btn-update {
            background: white;
            color: var(--accent);
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            border: none;
            cursor: pointer;
        }
        
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg-secondary); border-radius: 3px; }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
        
        .code-input { font-family: 'SF Mono', Monaco, monospace; font-size: 18px; text-align: center; letter-spacing: 2px; }
        
        .contact-count { color: var(--accent); font-weight: 600; }
    </style>
</head>
<body>
    <div class="lang-toggle">
        <button class="lang-btn active" id="lang-fr" onclick="setLang('fr')">FR</button>
        <button class="lang-btn" id="lang-en" onclick="setLang('en')">EN</button>
    </div>
    
    <div class="container">
        <!-- Update Banner -->
        <div id="update-banner" class="update-banner hidden">
            <span><span data-i18n="update_available">Version</span> <strong id="update-version"></strong> <span data-i18n="available">disponible!</span></span>
            <button class="btn-update" id="btn-update" data-i18n="update_now">Mettre à jour</button>
        </div>
        
        <!-- Header -->
        <div class="header">
            <div>
                <div class="title" id="app-title">Campagne SMS</div>
                <div class="version">v{{VERSION}}</div>
            </div>
        </div>
        
        <!-- Loading Screen -->
        <div id="screen-loading" class="card" style="text-align: center; padding: 50px;">
            <div class="spinner" style="margin: 0 auto 16px;"></div>
            <p style="color: var(--text-secondary);" data-i18n="checking_auth">Vérification...</p>
        </div>
        
        <!-- Activation Screen -->
        <div id="screen-activation" class="card fade-in hidden">
            <div class="card-title">
                <span data-i18n="activate_title">Activer votre licence</span>
            </div>
            <p style="color: var(--text-secondary); margin-bottom: 20px;" data-i18n="activate_desc">
                Entrez votre code d'activation pour débloquer SMS Campaign.
            </p>
            <div class="form-group">
                <label data-i18n="activation_code">Code d'activation</label>
                <input type="text" id="activation-code" class="code-input" placeholder="Entrez votre code" autocomplete="off">
            </div>
            <button class="btn btn-primary btn-full" id="btn-activate">
                <span data-i18n="activate_btn">Activer</span>
            </button>
            <div id="activation-error" class="alert alert-error hidden" style="margin-top: 16px;">
                <span class="alert-icon"></span>
                <div class="alert-content">
                    <div class="alert-title" data-i18n="activation_failed">Échec de l'activation</div>
                    <div class="alert-message" id="activation-error-msg"></div>
                </div>
            </div>
        </div>
        
        <!-- Step 1: Select CSV -->
        <div id="screen-step1" class="card fade-in hidden">
            <div class="card-title">
                <span class="step-num">1</span>
                <span data-i18n="step1_title">Sélectionnez vos contacts</span>
            </div>
            <div class="file-input-wrapper" id="file-drop-zone">
                <div class="file-icon">📁</div>
                <div class="file-text" data-i18n="drop_csv">Glissez votre fichier CSV ici ou cliquez pour parcourir</div>
                <div class="file-name hidden" id="file-name"></div>
                <input type="file" id="file-input" accept=".csv,.txt,.tsv">
            </div>
            <div id="csv-preview" class="hidden">
                <div class="alert alert-success" style="margin-top: 16px;">
                    <span class="alert-icon"></span>
                    <div class="alert-content">
                        <div class="alert-title"><span class="contact-count" id="contact-count">0</span> <span data-i18n="contacts_loaded">contacts chargés</span></div>
                    </div>
                </div>
                <button class="btn btn-primary btn-full" id="btn-to-step2" style="margin-top: 12px;" data-i18n="next_step">
                    Continuer →
                </button>
            </div>
        </div>
        
        <!-- Step 2: Compose Message -->
        <div id="screen-step2" class="card fade-in hidden">
            <div class="card-title">
                <span class="step-num">2</span>
                <span data-i18n="step2_title">Rédigez votre message</span>
            </div>
            <div class="form-group">
                <label data-i18n="insert_var">Insérer une variable :</label>
                <div class="var-buttons">
                    <button class="var-btn" id="btn-var-prenom">Prénom</button>
                    <button class="var-btn" id="btn-var-nom">Nom</button>
                </div>
            </div>
            <div class="form-group">
                <label data-i18n="message_label">Votre message</label>
                <textarea id="message-input" data-i18n-placeholder="message_placeholder" placeholder="Bonjour {{prenom}}, votre rendez-vous est confirmé!" style="color: var(--text-primary);"></textarea>
            </div>
            <div id="message-preview-box">
                <label data-i18n="preview_label">Aperçu (premier contact) :</label>
                <div class="message-preview" id="message-preview" style="min-height: 60px;"></div>
            </div>
            <div class="btn-group">
                <button class="btn btn-secondary" id="btn-back-to-step1" data-i18n="back">← Retour</button>
                <button class="btn btn-primary" id="btn-to-step3" disabled data-i18n="next_step">Continuer →</button>
            </div>
        </div>
        
        <!-- Step 3: Dashboard - Contact Validation (like mobile app) -->
        <div id="screen-step3" class="card fade-in hidden">
            <div class="card-title">
                <span class="step-num">3</span>
                <span data-i18n="step3_title">Vérification des contacts</span>
            </div>
            
            <div class="separator-info" id="separator-info">
                <strong data-i18n="separator_detected">Séparateur détecté:</strong> <span id="separator-type">virgule</span>
            </div>
            
            <div class="dashboard-stats">
                <div class="dashboard-stat valid">
                    <div class="num" id="valid-count">0</div>
                    <div class="label" data-i18n="valid_contacts">VALIDES</div>
                </div>
                <div class="dashboard-stat skipped">
                    <div class="num" id="skipped-count">0</div>
                    <div class="label" data-i18n="skipped_contacts">IGNORÉS</div>
                </div>
            </div>
            
            <!-- Side by side contact lists -->
            <div style="display: flex; gap: 20px; margin-bottom: 12px;">
                <!-- Valid contacts column -->
                <div style="flex: 1; min-width: 0;">
                    <div class="section-title" style="margin-top: 0; margin-bottom: 8px;"><span data-i18n="valid_contacts_title">Contacts valides</span></div>
                    <div class="contacts-table-wrapper" style="max-height: 220px; overflow-y: auto; overflow-x: hidden;">
                        <table class="contacts-table" style="table-layout: fixed; width: 100%;">
                            <thead>
                                <tr>
                                    <th style="width: 40px;">#</th>
                                    <th style="width: 30%;">Prénom</th>
                                    <th style="width: 30%;">Nom</th>
                                    <th style="width: 35%;">Téléphone</th>
                                </tr>
                            </thead>
                            <tbody id="valid-contacts-body"></tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Skipped contacts column -->
                <div id="skipped-section" style="flex: 1; min-width: 0;">
                    <div class="section-title" style="margin-top: 0; margin-bottom: 8px;"><span data-i18n="skipped_contacts_title">Contacts ignorés</span></div>
                    <div class="contacts-table-wrapper" style="max-height: 220px; overflow-y: auto; overflow-x: hidden;">
                        <table class="contacts-table" style="table-layout: fixed; width: 100%;">
                            <thead>
                                <tr>
                                    <th style="width: 40px;">#</th>
                                    <th style="width: 50%;">Raison</th>
                                    <th style="width: 40%;">Info</th>
                                </tr>
                            </thead>
                            <tbody id="skipped-contacts-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="section-title" style="margin-top: 8px; margin-bottom: 8px;"><span data-i18n="message_preview_title">Aperçu du message</span></div>
            <div class="message-preview" id="dashboard-preview" style="min-height: 40px; padding: 12px;"></div>
            
            <div class="btn-group" style="margin-top: 12px;">
                <button class="btn btn-secondary" id="btn-back-to-step2" data-i18n="back">← Retour</button>
                <button class="btn btn-success" id="btn-send">📤 <span data-i18n="send_all">Envoyer tout</span></button>
            </div>
        </div>
        
        <!-- Sending Screen -->
        <div id="screen-sending" class="card fade-in hidden">
            <div class="card-title">
                <span data-i18n="sending_title">Envoi en cours...</span>
            </div>
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                </div>
                <div class="progress-text">
                    <span id="progress-current">0 / 0</span>
                    <span id="progress-percent">0%</span>
                </div>
            </div>
            <div class="log-container" id="send-log"></div>
            <button class="btn btn-warning btn-full" id="btn-pause" style="margin-top: 16px;" data-i18n="pause_sending">Pause</button>
        </div>
        
        <!-- Pause Modal -->
        <div id="pause-modal" class="modal-overlay hidden">
            <div class="modal">
                <div class="modal-title"><span data-i18n="paused_title">Envoi en pause</span></div>
                <div class="modal-message">
                    <span data-i18n="paused_msg">L'envoi est en pause.</span>
                    <br><br>
                    <strong id="pause-progress"></strong>
                </div>
                <div class="modal-buttons">
                    <button class="btn btn-danger" id="btn-cancel-sending" data-i18n="cancel_all">Annuler</button>
                    <button class="btn btn-success" id="btn-resume"><span data-i18n="resume_btn">Reprendre</span></button>
                </div>
            </div>
        </div>
        
        <!-- Confirmation Modal -->
        <div id="confirm-modal" class="modal-overlay hidden">
            <div class="modal">
                <div class="modal-title"><span data-i18n="confirm_send_title">Confirmer l'envoi</span></div>
                <div class="modal-message">
                    <span data-i18n="confirm_send_msg">Vous êtes sur le point d'envoyer</span>
                    <strong id="confirm-count">0</strong>
                    <span data-i18n="confirm_send_msg2">messages. Cette action ne peut pas être annulée.</span>
                </div>
                <div class="modal-buttons">
                    <button class="btn btn-secondary" id="btn-cancel-send" data-i18n="cancel">Annuler</button>
                    <button class="btn btn-success" id="btn-confirm-send">📤 <span data-i18n="confirm_btn">Confirmer</span></button>
                </div>
            </div>
        </div>
        
        <!-- Complete Screen -->
        <div id="screen-complete" class="card fade-in hidden">
            <div class="card-title">
                <span data-i18n="complete_title">Campagne terminée!</span>
            </div>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value success" id="final-success">0</div>
                    <div class="stat-label" data-i18n="stat_sent">Envoyés</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value error" id="final-failed">0</div>
                    <div class="stat-label" data-i18n="stat_failed">Échoués</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value warning" id="final-skipped">0</div>
                    <div class="stat-label" data-i18n="stat_skipped">Ignorés</div>
                </div>
            </div>
            <button class="btn btn-primary btn-full" id="btn-close-app" style="margin-top: 20px;" data-i18n="close_app">✕ Fermer</button>
        </div>
    </div>
    
    <script>
        // ===== TRANSLATIONS =====
        const translations = {
            fr: {
                checking_auth: "Vérification...",
                activate_title: "Activer votre licence",
                activate_desc: "Entrez votre code d'activation pour débloquer SMS Campaign.",
                activation_code: "Code d'activation",
                activate_btn: "Activer",
                activation_failed: "Échec de l'activation",
                step1_title: "Sélectionnez vos contacts",
                drop_csv: "Glissez votre fichier CSV ici ou cliquez pour parcourir",
                contacts_found: "contacts trouvés",
                contacts_loaded: "contacts chargés",
                col_firstname: "Prénom",
                col_lastname: "Nom", 
                col_phones: "Téléphone(s)",
                col_phone: "Téléphone",
                col_source: "Source",
                col_reason: "Raison",
                col_raw_firstname: "Prénom brut",
                col_raw_phone: "Tél brut",
                next_step: "Continuer →",
                back: "← Retour",
                step2_title: "Rédigez votre message",
                insert_var: "Insérer une variable :",
                message_label: "Votre message",
                message_placeholder: "Bonjour {{prenom}}, votre rendez-vous est confirmé!",
                preview_label: "Aperçu (premier contact) :",
                step3_title: "Vérification des contacts",
                separator_detected: "Séparateur détecté:",
                valid_contacts: "VALIDES",
                skipped_contacts: "IGNORÉS",
                valid_contacts_title: "Contacts valides",
                skipped_contacts_title: "Contacts ignorés",
                message_preview_title: "Aperçu du message",
                no_valid_contacts: "Aucun contact valide",
                stat_contacts: "Contacts",
                stat_messages: "Messages",
                stat_time: "Temps est.",
                final_message: "Message final :",
                send_all: "Envoyer tout",
                sending_title: "Envoi en cours...",
                stop_sending: "⏹ Arrêter l'envoi",
                confirm_send_title: "Confirmer l'envoi",
                confirm_send_msg: "Vous êtes sur le point d'envoyer",
                confirm_send_msg2: "messages. Cette action ne peut pas être annulée.",
                cancel: "Annuler",
                confirm_btn: "Confirmer",
                pause_sending: "Pause",
                paused_title: "Envoi en pause",
                paused_msg: "L'envoi est en pause.",
                cancel_all: "Annuler",
                resume_btn: "Reprendre",
                paused_progress: "messages envoyés sur",
                complete_title: "Campagne terminée!",
                stat_sent: "Envoyés",
                stat_failed: "Échoués",
                stat_skipped: "Ignorés",
                close_app: "✕ Fermer",
                update_available: "Version",
                available: "disponible!",
                update_now: "Mettre à jour",
                no_phone: "Pas de téléphone",
                phone_invalid: "Téléphone invalide",
                phone_too_short: "chiffres, min 10",
                phone_too_long: "chiffres, trop long",
                phone_empty: "Téléphone vide",
                firstname_missing: "Prénom manquant",
                separator_comma: "virgule",
                separator_semicolon: "point-virgule",
                separator_tab: "tabulation"
            },
            en: {
                checking_auth: "Checking...",
                activate_title: "Activate your license",
                activate_desc: "Enter your activation code to unlock SMS Campaign.",
                activation_code: "Activation Code",
                activate_btn: "Activate",
                activation_failed: "Activation Failed",
                step1_title: "Select your contacts",
                drop_csv: "Drop your CSV file here or click to browse",
                contacts_found: "contacts found",
                contacts_loaded: "contacts loaded",
                col_firstname: "First Name",
                col_lastname: "Last Name",
                col_phones: "Phone(s)",
                col_phone: "Phone",
                col_source: "Source",
                col_reason: "Reason",
                col_raw_firstname: "Raw First Name",
                col_raw_phone: "Raw Phone",
                next_step: "Continue →",
                back: "← Back",
                step2_title: "Compose your message",
                insert_var: "Insert variable:",
                message_label: "Your message",
                message_placeholder: "Hello {{prenom}}, your appointment is confirmed!",
                preview_label: "Preview (first contact):",
                step3_title: "Contact Verification",
                separator_detected: "Separator detected:",
                valid_contacts: "VALID",
                skipped_contacts: "SKIPPED",
                valid_contacts_title: "Valid contacts",
                skipped_contacts_title: "Skipped contacts",
                message_preview_title: "Message preview",
                no_valid_contacts: "No valid contacts",
                stat_contacts: "Contacts",
                stat_messages: "Messages",
                stat_time: "Est. Time",
                final_message: "Final message:",
                send_all: "Send All",
                sending_title: "Sending...",
                stop_sending: "⏹ Stop Sending",
                confirm_send_title: "Confirm Send",
                confirm_send_msg: "You are about to send",
                confirm_send_msg2: "messages. This action cannot be undone.",
                cancel: "Cancel",
                confirm_btn: "Confirm",
                pause_sending: "Pause",
                paused_title: "Sending paused",
                paused_msg: "Sending is paused.",
                cancel_all: "Cancel",
                resume_btn: "Resume",
                paused_progress: "messages sent out of",
                complete_title: "Campaign Complete!",
                stat_sent: "Sent",
                stat_failed: "Failed",
                stat_skipped: "Skipped",
                close_app: "✕ Close",
                update_available: "Version",
                available: "available!",
                update_now: "Update Now",
                no_phone: "No phone",
                phone_invalid: "Invalid phone",
                phone_too_short: "digits, min 10",
                phone_too_long: "digits, too long",
                phone_empty: "Phone empty",
                firstname_missing: "First name missing",
                separator_comma: "comma",
                separator_semicolon: "semicolon",
                separator_tab: "tab"
            }
        };
        
        let currentLang = 'fr';
        
        function setLang(lang) {
            currentLang = lang;
            document.getElementById('lang-fr').classList.toggle('active', lang === 'fr');
            document.getElementById('lang-en').classList.toggle('active', lang === 'en');
            
            // Update title based on language
            document.getElementById('app-title').textContent = lang === 'fr' ? 'Campagne SMS' : 'SMS Campaign';
            
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (translations[lang][key]) {
                    el.textContent = translations[lang][key];
                }
            });
            
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                if (translations[lang][key]) {
                    el.placeholder = translations[lang][key];
                }
            });
        }
        
        // ===== STATE =====
        let contacts = [];
        let messageTemplate = '';
        let sending = false;
        let stopped = false;
        let paused = false;
        let currentSendIndex = 0;
        
        // ===== SCREENS =====
        const allScreens = ['screen-loading', 'screen-activation', 'screen-step1', 'screen-step2', 'screen-step3', 'screen-sending', 'screen-complete'];
        
        // Base widths for each screen (height is calculated from content)
        const screenWidths = {
            'screen-loading': 500,
            'screen-activation': 520,
            'screen-step1': 550,
            'screen-step2': 600,
            'screen-step3': 1000,
            'screen-sending': 600,
            'screen-complete': 500
        };
        
        // Calculate window height based on actual content
        function calculateContentHeight(screenId) {
            const screen = document.getElementById(screenId);
            if (!screen) return 500;
            
            // Temporarily show to measure (without animation)
            const wasHidden = screen.classList.contains('hidden');
            if (wasHidden) {
                screen.style.visibility = 'hidden';
                screen.style.position = 'absolute';
                screen.classList.remove('hidden');
            }
            
            // Get the container and header heights
            const container = document.querySelector('.container');
            const header = document.querySelector('.header');
            const updateBanner = document.getElementById('update-banner');
            const langToggle = document.querySelector('.lang-toggle');
            
            // Calculate total height: screen card + header + padding + chrome
            const screenHeight = screen.offsetHeight;
            const headerHeight = header ? header.offsetHeight : 0;
            const bannerHeight = (updateBanner && !updateBanner.classList.contains('hidden')) ? updateBanner.offsetHeight + 16 : 0;
            const containerPadding = 32; // 16px top + 16px bottom
            const headerMargin = 30; // margin-bottom on header
            const windowChrome = 40; // Title bar + some buffer
            
            // Restore hidden state
            if (wasHidden) {
                screen.classList.add('hidden');
                screen.style.visibility = '';
                screen.style.position = '';
            }
            
            const totalHeight = screenHeight + headerHeight + headerMargin + bannerHeight + containerPadding + windowChrome;
            
            // Add minimum heights and screen-specific max caps
            const minHeight = 400;
            const maxHeight = screenId === 'screen-step3' ? 1100 : 900;
            
            return Math.max(minHeight, Math.min(maxHeight, totalHeight));
        }
        
        // Resize window based on content
        function resizeToContent(screenId) {
            if (!window.pywebview || !window.pywebview.api) return;
            
            const width = screenWidths[screenId] || 550;
            const height = calculateContentHeight(screenId);
            
            try {
                window.pywebview.api.resize(width, height);
            } catch (e) {
                console.log('Resize error:', e);
            }
        }
        
        function showScreen(id) {
            allScreens.forEach(s => document.getElementById(s).classList.add('hidden'));
            document.getElementById(id).classList.remove('hidden');
            
            // Use requestAnimationFrame to ensure DOM is updated before measuring
            requestAnimationFrame(() => {
                resizeToContent(id);
            });
        }
        
        // Resize current screen (call after content changes)
        function resizeCurrentScreen() {
            const currentScreen = allScreens.find(s => !document.getElementById(s).classList.contains('hidden'));
            if (currentScreen) {
                resizeToContent(currentScreen);
            }
        }
        
        // ===== API =====
        async function api(action, data = {}) {
            const response = await fetch('/api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action, ...data })
            });
            return response.json();
        }
        
        // ===== INIT =====
        async function init() {
            showScreen('screen-loading');
            checkForUpdate();
            const result = await api('check_auth');
            showScreen(result.authorized ? 'screen-step1' : 'screen-activation');
        }
        
        // ===== UPDATE =====
        let updateDownloadUrl = null;
        
        async function checkForUpdate() {
            try {
                const result = await api('check_update');
                if (result.available) {
                    updateDownloadUrl = result.download_url;
                    document.getElementById('update-version').textContent = result.version;
                    document.getElementById('update-banner').classList.remove('hidden');
                }
            } catch (e) {}
        }
        
        document.getElementById('btn-update').addEventListener('click', async () => {
            const btn = document.getElementById('btn-update');
            btn.disabled = true;
            btn.textContent = '...';
            const result = await api('perform_update', { download_url: updateDownloadUrl });
            if (!result.success) {
                alert('Update failed: ' + (result.error || 'Unknown'));
                btn.disabled = false;
                btn.textContent = translations[currentLang].update_now;
            }
        });
        
        // ===== ACTIVATION =====
        document.getElementById('btn-activate').addEventListener('click', async () => {
            const code = document.getElementById('activation-code').value.trim();
            const errorEl = document.getElementById('activation-error');
            const errorMsg = document.getElementById('activation-error-msg');
            const btn = document.getElementById('btn-activate');
            
            if (!code) {
                errorEl.classList.remove('hidden');
                errorMsg.textContent = currentLang === 'fr' ? 'Veuillez entrer un code.' : 'Please enter a code.';
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<div class="spinner"></div>';
            errorEl.classList.add('hidden');
            
            const result = await api('activate', { code });
            btn.disabled = false;
            btn.innerHTML = `<span>${translations[currentLang].activate_btn}</span>`;
            
            if (result.success) {
                showScreen('screen-step1');
            } else {
                errorEl.classList.remove('hidden');
                errorMsg.textContent = result.error || 'Invalid code';
            }
        });
        
        // ===== STEP 1: CSV =====
        const fileInput = document.getElementById('file-input');
        const fileDropZone = document.getElementById('file-drop-zone');
        
        fileInput.addEventListener('change', e => { if (e.target.files[0]) handleFile(e.target.files[0]); });
        fileDropZone.addEventListener('click', e => { if (e.target !== fileInput) fileInput.click(); });
        fileDropZone.addEventListener('dragover', e => { e.preventDefault(); fileDropZone.style.borderColor = 'var(--accent)'; });
        fileDropZone.addEventListener('dragleave', () => { fileDropZone.style.borderColor = ''; });
        fileDropZone.addEventListener('drop', e => { e.preventDefault(); fileDropZone.style.borderColor = ''; if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); });
        
        async function handleFile(file) {
            const reader = new FileReader();
            reader.onload = async e => {
                const result = await api('parse_csv', { content: e.target.result, filename: file.name });
                if (result.success) {
                    contacts = result.contacts;
                    separatorType = result.separator || 'comma';
                    
                    fileDropZone.classList.add('has-file');
                    document.getElementById('file-name').textContent = file.name;
                    document.getElementById('file-name').classList.remove('hidden');
                    
                    document.getElementById('contact-count').textContent = contacts.length;
                    document.getElementById('csv-preview').classList.remove('hidden');
                    
                    // Resize window to fit the content that appeared
                    resizeCurrentScreen();
                } else {
                    alert('Error: ' + result.error);
                }
            };
            reader.readAsText(file);
        }
        
        document.getElementById('btn-to-step2').addEventListener('click', () => {
            if (contacts.length > 0) showScreen('screen-step2');
        });
        
        // ===== STEP 2: MESSAGE =====
        const messageInput = document.getElementById('message-input');
        
        document.getElementById('btn-var-prenom').addEventListener('click', () => {
            insertAtCursor(messageInput, '{{prenom}} ');
            messageInput.dispatchEvent(new Event('input'));
        });
        
        document.getElementById('btn-var-nom').addEventListener('click', () => {
            insertAtCursor(messageInput, '{{nom}} ');
            messageInput.dispatchEvent(new Event('input'));
        });
        
        function insertAtCursor(el, text) {
            const start = el.selectionStart;
            const end = el.selectionEnd;
            el.value = el.value.substring(0, start) + text + el.value.substring(end);
            el.selectionStart = el.selectionEnd = start + text.length;
            el.focus();
        }
        
        messageInput.addEventListener('input', () => {
            messageTemplate = messageInput.value;
            const btn = document.getElementById('btn-to-step3');
            
            if (messageTemplate.trim()) {
                btn.disabled = false;
            } else {
                btn.disabled = true;
            }
            
            // Always show preview, with highlighted variables
            const firstContact = contacts[0];
            const firstName = firstContact?.firstname || firstContact?.name || 'Client';
            const lastName = firstContact?.lastname || '';
            
            let preview = messageTemplate || '';
            preview = preview
                .replace(/\\{\\{prenom\\}\\}/gi, `<span style="background:linear-gradient(135deg,var(--accent),#5e5ce6);color:white;padding:2px 8px;border-radius:6px">${firstName}</span>`)
                .replace(/\\{\\{nom\\}\\}/gi, `<span style="background:linear-gradient(135deg,var(--accent),#5e5ce6);color:white;padding:2px 8px;border-radius:6px">${lastName}</span>`)
                .replace(/\\{\\{name\\}\\}/gi, `<span style="background:linear-gradient(135deg,var(--accent),#5e5ce6);color:white;padding:2px 8px;border-radius:6px">${firstName}</span>`);
            
            document.getElementById('message-preview').innerHTML = preview;
            
            // Dynamically resize window based on content
            resizeCurrentScreen();
        });
        
        document.getElementById('btn-back-to-step1').addEventListener('click', () => showScreen('screen-step1'));
        
        // Store validated contacts data
        let validatedContacts = [];
        let skippedContacts = [];
        let separatorType = 'virgule';
        
        document.getElementById('btn-to-step3').addEventListener('click', () => {
            if (!messageTemplate.trim()) return;
            
            // Validate contacts (like mobile app)
            validatedContacts = [];
            skippedContacts = [];
            
            contacts.forEach((c, i) => {
                // Get the best phone
                const rawPhone = c.phones.length > 0 ? c.phones[0] : '';
                const formattedPhone = formatPhoneNumber(rawPhone);
                
                // Validate contact (like mobile app - requires firstname and valid phone)
                const skipReason = validatePhone(formattedPhone, rawPhone, c.firstname);
                
                if (skipReason) {
                    skippedContacts.push({
                        lineNumber: i + 1,
                        reason: skipReason,
                        rawFirstName: c.firstname || '',
                        rawPhone: c.raw_phone || rawPhone || ''
                    });
                } else {
                    validatedContacts.push({
                        lineNumber: i + 1,
                        phone: formattedPhone,
                        firstname: c.firstname || '',
                        lastname: c.lastname || '',
                        phoneSource: c.phone_source || 'principal',
                        rawPhone: rawPhone
                    });
                }
            });
            
            // Populate dashboard
            document.getElementById('valid-count').textContent = validatedContacts.length;
            document.getElementById('skipped-count').textContent = skippedContacts.length;
            document.getElementById('separator-type').textContent = translations[currentLang][`separator_${separatorType}`] || separatorType;
            
            // Valid contacts table (simplified for side-by-side)
            const validBody = document.getElementById('valid-contacts-body');
            validBody.innerHTML = '';
            if (validatedContacts.length === 0) {
                validBody.innerHTML = `<tr><td colspan="4" style="color:var(--text-secondary)">${translations[currentLang].no_valid_contacts}</td></tr>`;
            } else {
                validatedContacts.forEach(c => {
                    validBody.innerHTML += `<tr>
                        <td>${c.lineNumber}</td>
                        <td>${c.firstname || '—'}</td>
                        <td>${c.lastname || '—'}</td>
                        <td style="font-size:11px">${c.phone}</td>
                    </tr>`;
                });
            }
            
            // Skipped contacts table (simplified for side-by-side)
            const skippedBody = document.getElementById('skipped-contacts-body');
            skippedBody.innerHTML = '';
            if (skippedContacts.length === 0) {
                document.getElementById('skipped-section').style.opacity = '0.4';
                skippedBody.innerHTML = `<tr><td colspan="3" style="color:var(--text-secondary)">—</td></tr>`;
            } else {
                document.getElementById('skipped-section').style.opacity = '1';
                skippedContacts.forEach(s => {
                    // Show phone if firstname is missing, show firstname if phone is missing
                    let infoDisplay = '';
                    if (!s.rawFirstName && s.rawPhone) {
                        infoDisplay = `${s.rawPhone}`;
                    } else if (s.rawFirstName && !s.rawPhone) {
                        infoDisplay = `${s.rawFirstName}`;
                    } else if (s.rawFirstName && s.rawPhone) {
                        infoDisplay = `${s.rawFirstName}`;
                    } else {
                        infoDisplay = '—';
                    }
                    skippedBody.innerHTML += `<tr>
                        <td>${s.lineNumber}</td>
                        <td class="reason" style="font-size:11px">${s.reason}</td>
                        <td style="font-size:11px">${infoDisplay}</td>
                    </tr>`;
                });
            }
            
            // Message preview (like mobile app) with highlighted variables
            const firstValid = validatedContacts[0];
            const preview = firstValid ? messageTemplate
                .replace(/\\{\\{prenom\\}\\}/gi, `<span style="background:linear-gradient(135deg,var(--accent),#5e5ce6);color:white;padding:2px 8px;border-radius:6px">${firstValid.firstname || 'Client'}</span>`)
                .replace(/\\{\\{nom\\}\\}/gi, `<span style="background:linear-gradient(135deg,var(--accent),#5e5ce6);color:white;padding:2px 8px;border-radius:6px">${firstValid.lastname || ''}</span>`)
                .replace(/\\{\\{name\\}\\}/gi, `<span style="background:linear-gradient(135deg,var(--accent),#5e5ce6);color:white;padding:2px 8px;border-radius:6px">${firstValid.firstname || 'Client'}</span>`)
                : messageTemplate;
            document.getElementById('dashboard-preview').innerHTML = preview;
            
            // Disable send if no valid contacts
            document.getElementById('btn-send').disabled = validatedContacts.length === 0;
            
            showScreen('screen-step3');
        });
        
        // Phone formatting (like mobile app)
        function formatPhoneNumber(phone) {
            if (!phone) return '';
            
            let cleaned = phone.replace(/[^\\d+]/g, '');
            
            // Already formatted with +1
            if (cleaned.startsWith('+1') && cleaned.length === 12) {
                return cleaned;
            }
            
            // Starts with 1 (North American)
            if (cleaned.startsWith('1') && cleaned.length === 11) {
                return '+' + cleaned;
            }
            
            // Get just digits
            let digits = cleaned.replace(/\\D/g, '');
            
            // 10 digits - add +1
            if (digits.length === 10) {
                return '+1' + digits;
            }
            
            // 11 digits starting with 1
            if (digits.length === 11 && digits.startsWith('1')) {
                return '+' + digits;
            }
            
            return cleaned;
        }
        
        // Phone validation (like mobile app - require firstname)
        function validatePhone(phone, rawPhone, firstname) {
            // Firstname is required (like mobile app)
            if (!firstname || firstname.trim().length === 0) {
                return translations[currentLang].firstname_missing || 'Prénom manquant';
            }
            
            const phoneDigits = phone.replace(/\\D/g, '');
            
            if (!phoneDigits || phoneDigits.length === 0) {
                return translations[currentLang].phone_empty;
            }
            
            if (phoneDigits.length < 10) {
                return `${translations[currentLang].phone_invalid}: "${rawPhone}" (${phoneDigits.length} ${translations[currentLang].phone_too_short})`;
            }
            
            if (phoneDigits.length > 15) {
                return `${translations[currentLang].phone_invalid}: "${rawPhone}" (${phoneDigits.length} ${translations[currentLang].phone_too_long})`;
            }
            
            return null; // Valid
        }
        
        // ===== STEP 3: SEND =====
        document.getElementById('btn-back-to-step2').addEventListener('click', () => showScreen('screen-step2'));
        
        // Show confirmation modal
        document.getElementById('btn-send').addEventListener('click', () => {
            if (validatedContacts.length === 0) return;
            document.getElementById('confirm-count').textContent = validatedContacts.length;
            document.getElementById('confirm-modal').classList.remove('hidden');
        });
        
        // Cancel send
        document.getElementById('btn-cancel-send').addEventListener('click', () => {
            document.getElementById('confirm-modal').classList.add('hidden');
        });
        
        // Close modal on overlay click
        document.getElementById('confirm-modal').addEventListener('click', (e) => {
            if (e.target.id === 'confirm-modal') {
                document.getElementById('confirm-modal').classList.add('hidden');
            }
        });
        
        // Sending state
        let sent = 0, failed = 0;
        const maxLogEntries = 15;
        let logEntries = [];
        
        // Confirm and send
        document.getElementById('btn-confirm-send').addEventListener('click', async () => {
            document.getElementById('confirm-modal').classList.add('hidden');
            startSending(0);
        });
        
        async function startSending(startIndex) {
            showScreen('screen-sending');
            sending = true;
            stopped = false;
            paused = false;
            
            const log = document.getElementById('send-log');
            if (startIndex === 0) {
                log.innerHTML = '';
                logEntries = [];
                sent = 0;
                failed = 0;
            }
            
            const total = validatedContacts.length;
            
            for (let i = startIndex; i < validatedContacts.length && !stopped && !paused; i++) {
                currentSendIndex = i;
                const contact = validatedContacts[i];
                const phone = contact.phone;
                const message = messageTemplate
                    .replace(/\\{\\{prenom\\}\\}/gi, contact.firstname || '')
                    .replace(/\\{\\{nom\\}\\}/gi, contact.lastname || '')
                    .replace(/\\{\\{name\\}\\}/gi, contact.firstname || '');
                
                const result = await api('send_sms', { phone, message });
                const time = new Date().toLocaleTimeString();
                
                let logEntry;
                if (result.success) {
                    sent++;
                    logEntry = `<div class="log-entry"><span class="log-time">${time}</span><span style="color:#30d158">Sent</span><span class="log-message">${contact.firstname || 'Contact'} → ${phone}</span></div>`;
                } else {
                    failed++;
                    logEntry = `<div class="log-entry"><span class="log-time">${time}</span><span style="color:#ff453a">Error</span><span class="log-message">${contact.firstname || 'Contact'}: ${result.error || 'Failed'}</span></div>`;
                }
                
                // Keep only last 15 entries
                logEntries.push(logEntry);
                if (logEntries.length > maxLogEntries) {
                    logEntries.shift();
                }
                log.innerHTML = logEntries.join('');
                log.scrollTop = log.scrollHeight;
                
                const progress = ((i + 1) / total * 100).toFixed(0);
                document.getElementById('progress-fill').style.width = progress + '%';
                document.getElementById('progress-current').textContent = `${i + 1} / ${total}`;
                document.getElementById('progress-percent').textContent = progress + '%';
                
                currentSendIndex = i + 1;
            }
            
            // Only show complete if not paused
            if (!paused) {
                document.getElementById('final-success').textContent = sent;
                document.getElementById('final-failed').textContent = failed;
                document.getElementById('final-skipped').textContent = skippedContacts.length;
                showScreen('screen-complete');
            }
        }
        
        // Pause button
        document.getElementById('btn-pause').addEventListener('click', () => {
            paused = true;
            const total = validatedContacts.length;
            document.getElementById('pause-progress').textContent = `${currentSendIndex} ${translations[currentLang].paused_progress} ${total}`;
            document.getElementById('pause-modal').classList.remove('hidden');
        });
        
        // Resume button
        document.getElementById('btn-resume').addEventListener('click', () => {
            document.getElementById('pause-modal').classList.add('hidden');
            startSending(currentSendIndex);
        });
        
        // Cancel all button
        document.getElementById('btn-cancel-sending').addEventListener('click', () => {
            document.getElementById('pause-modal').classList.add('hidden');
            stopped = true;
            const remaining = validatedContacts.length - sent - failed;
            document.getElementById('final-success').textContent = sent;
            document.getElementById('final-failed').textContent = failed + remaining;
            document.getElementById('final-skipped').textContent = skippedContacts.length;
            showScreen('screen-complete');
        });
        
        // Close app button
        document.getElementById('btn-close-app').addEventListener('click', () => {
            window.close();
        });
        
        // ===== START =====
        init();
    </script>
</body>
</html>
'''

# ============================================================================
# KEYCHAIN FUNCTIONS
# ============================================================================

def keychain_get(key):
    """Get a value from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", CONFIG["keychain_service"], "-a", key, "-w"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    return None

def keychain_set(key, value):
    """Set a value in macOS Keychain."""
    try:
        # Delete existing entry first
        subprocess.run(
            ["security", "delete-generic-password", "-s", CONFIG["keychain_service"], "-a", key],
            capture_output=True, text=True
        )
    except:
        pass
    
    try:
        result = subprocess.run(
            ["security", "add-generic-password", "-s", CONFIG["keychain_service"], "-a", key, "-w", value],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except:
        return False

def keychain_contains(key):
    """Check if a key exists in macOS Keychain."""
    return keychain_get(key) is not None

# ============================================================================
# AUTO-UPDATE SYSTEM
# ============================================================================

def get_app_path():
    """Get the path to the current .app bundle."""
    if getattr(sys, 'frozen', False):
        # Running as compiled app
        # The executable is inside .app/Contents/MacOS/
        exe_path = sys.executable
        # Go up to .app level: MacOS -> Contents -> .app
        app_path = os.path.dirname(os.path.dirname(os.path.dirname(exe_path)))
        if app_path.endswith('.app'):
            return app_path
    return None

def check_for_update():
    """Check if a new version is available."""
    try:
        req = Request(CONFIG["update_url"], headers={"Cache-Control": "no-cache"})
        with urlopen(req, timeout=10, context=SSL_CONTEXT) as response:
            data = json.loads(response.read().decode('utf-8'))
            remote_version = data.get("version", "0.0.0")
            download_url = data.get("download_url", CONFIG["download_url"])
            
            # Compare versions
            def parse_version(v):
                return tuple(map(int, v.split('.')))
            
            if parse_version(remote_version) > parse_version(VERSION):
                return {
                    "available": True,
                    "version": remote_version,
                    "download_url": download_url,
                    "notes": data.get("notes", "")
                }
            return {"available": False}
    except Exception as e:
        return {"available": False, "error": str(e)}

def perform_update(download_url):
    """Download and install the update, then relaunch."""
    import tempfile
    import zipfile
    import shutil
    
    app_path = get_app_path()
    if not app_path:
        return {"success": False, "error": "Cannot determine app location"}
    
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp(prefix="sms_campaign_update_")
        zip_path = os.path.join(temp_dir, "update.zip")
        
        # Use curl to download (handles GitHub redirects properly)
        result = subprocess.run(
            ["curl", "-L", "-o", zip_path, "-f", "--max-time", "120", download_url],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return {"success": False, "error": f"Download failed: {result.stderr}"}
        
        # Extract the zip
        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the .app in extracted content
        new_app_path = None
        for item in os.listdir(extract_dir):
            if item.endswith('.app'):
                new_app_path = os.path.join(extract_dir, item)
                break
        
        # Also check for __MACOSX folder issue
        if not new_app_path:
            for root, dirs, files in os.walk(extract_dir):
                for d in dirs:
                    if d.endswith('.app'):
                        new_app_path = os.path.join(root, d)
                        break
                if new_app_path:
                    break
        
        if not new_app_path:
            return {"success": False, "error": "No .app found in update"}
        
        # Create update script that runs after we quit
        app_name = os.path.basename(app_path)
        parent_dir = os.path.dirname(app_path)
        
        update_script = f'''#!/bin/bash
sleep 2
rm -rf "{app_path}"
cp -R "{new_app_path}" "{parent_dir}/"
xattr -cr "{os.path.join(parent_dir, os.path.basename(new_app_path))}"
open "{os.path.join(parent_dir, os.path.basename(new_app_path))}"
rm -rf "{temp_dir}"
'''
        
        script_path = os.path.join(temp_dir, "update.sh")
        with open(script_path, 'w') as f:
            f.write(update_script)
        os.chmod(script_path, 0o755)
        
        # Run the update script in background and quit
        subprocess.Popen([script_path], start_new_session=True)
        
        return {"success": True, "message": "Update starting, app will relaunch..."}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# DEVICE FINGERPRINT
# ============================================================================

def get_device_fingerprint():
    """Get or create a unique device fingerprint stored in Keychain."""
    device_id = keychain_get(CONFIG["keychain_device_key"])
    if device_id:
        return device_id
    
    # Generate new device ID
    device_id = str(uuid.uuid4())
    keychain_set(CONFIG["keychain_device_key"], device_id)
    return device_id

# ============================================================================
# AUTHORIZATION
# ============================================================================

def read_auth_code():
    """Read stored auth code from Keychain."""
    return keychain_get(CONFIG["keychain_auth_key"])

def write_auth_code(code):
    """Write auth code to Keychain."""
    return keychain_set(CONFIG["keychain_auth_key"], code)

def verify_code_with_webhook(code):
    """Verify activation code with the n8n webhook."""
    device_id = get_device_fingerprint()
    
    payload = {
        "code": code.strip(),
        "device_id": device_id,
        "device_type": "mac",  # Used to store in macbook_id column
        "platform": "mac",
        "version": VERSION
    }
    
    try:
        req = Request(
            CONFIG["webhook_url"],
            data=json.dumps(payload).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        
        with urlopen(req, timeout=30, context=SSL_CONTEXT) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("valid", False), result.get("message", "Unknown error")
    except URLError as e:
        return False, f"Network error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def check_authorization():
    """Check if the app is authorized."""
    stored_code = read_auth_code()
    if not stored_code:
        return False
    
    # Verify with webhook
    valid, message = verify_code_with_webhook(stored_code)
    return valid

def activate(code):
    """Activate with a new code."""
    valid, message = verify_code_with_webhook(code)
    if valid:
        write_auth_code(code.strip())
        return True, "Activation successful!"
    return False, message

# ============================================================================
# CSV PARSING
# ============================================================================

def fix_french_accents(text):
    """Fix common French accent encoding issues."""
    if not text:
        return text
    for bad, good in KNOWN_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text

def detect_separator(content):
    """Detect the CSV separator."""
    first_lines = content.split('\n')[:5]
    sample = '\n'.join(first_lines)
    
    separators = [(',', 0), (';', 0), ('\t', 0), ('|', 0)]
    
    for i, (sep, _) in enumerate(separators):
        count = sample.count(sep)
        separators[i] = (sep, count)
    
    separators.sort(key=lambda x: x[1], reverse=True)
    return separators[0][0] if separators[0][1] > 0 else ','

def normalize_phone(phone):
    """Normalize a phone number."""
    if not phone:
        return None
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', str(phone))
    
    # Handle various formats
    if cleaned.startswith('+'):
        return cleaned
    elif cleaned.startswith('00'):
        return '+' + cleaned[2:]
    elif cleaned.startswith('0') and len(cleaned) == 10:
        return '+33' + cleaned[1:]
    elif len(cleaned) == 9 and not cleaned.startswith('0'):
        return '+33' + cleaned
    elif len(cleaned) >= 10:
        return '+' + cleaned
    
    return None

def is_valid_phone(phone):
    """Check if a phone number is valid."""
    if not phone:
        return False
    normalized = normalize_phone(phone)
    if not normalized:
        return False
    # Must have at least 10 digits
    digits = re.sub(r'\D', '', normalized)
    return len(digits) >= 10

def get_phones_from_value(value):
    """Extract all phone numbers from a cell value."""
    if not value:
        return []
    
    phones = []
    value = str(value).strip()
    
    # Try splitting by common separators
    for sep in CONFIG["phone_separators"]:
        if sep in value:
            parts = value.split(sep)
            for part in parts:
                phone = normalize_phone(part.strip())
                if phone and is_valid_phone(phone):
                    phones.append(phone)
            if phones:
                return phones
    
    # Try as single phone
    phone = normalize_phone(value)
    if phone and is_valid_phone(phone):
        return [phone]
    
    return []

def parse_csv(content, filename=""):
    """Parse CSV content and extract contacts with firstname, lastname, and phones."""
    # Fix French accents
    content = fix_french_accents(content)
    
    # Detect separator
    sep = detect_separator(content)
    
    # Parse CSV
    try:
        reader = csv.DictReader(StringIO(content), delimiter=sep)
        headers = [h.lower().strip() for h in (reader.fieldnames or [])]
        
        # Find columns
        phone_col = None
        name_col = None
        firstname_col = None
        lastname_col = None
        
        for h in headers:
            original_header = reader.fieldnames[headers.index(h)]
            h_lower = h.lower()
            
            # Phone column
            if not phone_col:
                for pc in CONFIG["phone_columns"]:
                    if pc in h_lower:
                        phone_col = original_header
                        break
            
            # Firstname column (check first, before generic name)
            if not firstname_col:
                for fc in CONFIG["firstname_columns"]:
                    if fc in h_lower or h_lower == fc:
                        firstname_col = original_header
                        break
            
            # Lastname column
            if not lastname_col:
                for lc in CONFIG["lastname_columns"]:
                    # Be careful: "nom" could match both firstname and lastname
                    # Only match lastname if it's a dedicated lastname column
                    if lc in h_lower and h_lower not in ["prenom", "prénom", "firstname", "first_name"]:
                        # Check if it's specifically a lastname column
                        if any(x in h_lower for x in ["last", "famille", "family", "surname"]) or (h_lower == "nom" and firstname_col):
                            lastname_col = original_header
                            break
            
            # Generic name column (fallback)
            if not name_col:
                for nc in CONFIG["name_columns"]:
                    if nc in h_lower:
                        name_col = original_header
                        break
        
        # If we found "nom" and no firstname, it's probably first name
        if not firstname_col and name_col:
            firstname_col = name_col
            name_col = None
        
        if not phone_col:
            # Try to find any column with phone-like data
            reader = csv.DictReader(StringIO(content), delimiter=sep)
            for row in reader:
                for col, val in row.items():
                    if get_phones_from_value(val):
                        phone_col = col
                        break
                if phone_col:
                    break
        
        if not phone_col:
            return {"success": False, "error": "No phone column found"}
        
        # Parse contacts
        reader = csv.DictReader(StringIO(content), delimiter=sep)
        contacts = []
        
        for row in reader:
            phones = get_phones_from_value(row.get(phone_col, ""))
            
            # Get firstname
            if firstname_col:
                firstname = fix_french_accents(row.get(firstname_col, "")).strip()
            elif name_col:
                # Split full name if we only have a name column
                full_name = fix_french_accents(row.get(name_col, "")).strip()
                parts = full_name.split(None, 1)
                firstname = parts[0] if parts else ""
            else:
                firstname = ""
            
            # Get lastname
            if lastname_col:
                lastname = fix_french_accents(row.get(lastname_col, "")).strip()
            elif name_col and not firstname_col:
                # Split full name
                full_name = fix_french_accents(row.get(name_col, "")).strip()
                parts = full_name.split(None, 1)
                lastname = parts[1] if len(parts) > 1 else ""
            else:
                lastname = ""
            
            # Also include full name for backwards compatibility
            name = firstname
            if lastname:
                name = f"{firstname} {lastname}".strip()
            # Store raw phone for debugging
            raw_phone = row.get(phone_col, "")
            
            contacts.append({
                "name": name,
                "firstname": firstname,
                "lastname": lastname,
                "phones": phones,
                "raw_phone": raw_phone,
                "phone_source": "principal" if phones else "vide"
            })
        
        # Determine separator name
        sep_name = "comma"
        if sep == ';':
            sep_name = "semicolon"
        elif sep == '\t':
            sep_name = "tab"
        
        return {"success": True, "contacts": contacts, "separator": sep_name}
    
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# SMS SENDING
# ============================================================================

def send_sms(phone, message):
    """Send an SMS using AppleScript via Messages app.
    
    Uses SMS service type to ensure delivery to all phones (iPhone and Android).
    This requires an iPhone connected via Continuity/Text Message Forwarding.
    """
    # Escape for AppleScript
    message_escaped = message.replace('\\', '\\\\').replace('"', '\\"')
    phone_escaped = phone.replace('\\', '\\\\').replace('"', '\\"')
    
    # Use SMS service (not iMessage) to ensure delivery to all phones
    script = f'''
    tell application "Messages"
        set targetService to 1st account whose service type = SMS
        set targetBuddy to participant "{phone_escaped}" of targetService
        send "{message_escaped}" to targetBuddy
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return {"success": True}
        else:
            return {"success": False, "error": result.stderr.strip() or "Unknown error"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================================
# WEB SERVER
# ============================================================================

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            html = HTML_TEMPLATE.replace('{{VERSION}}', VERSION)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                action = data.get('action', '')
                
                if action == 'check_auth':
                    authorized = check_authorization()
                    result = {"authorized": authorized}
                
                elif action == 'activate':
                    code = data.get('code', '')
                    success, message = activate(code)
                    result = {"success": success, "error": message if not success else None}
                
                elif action == 'parse_csv':
                    content = data.get('content', '')
                    filename = data.get('filename', '')
                    result = parse_csv(content, filename)
                
                elif action == 'send_sms':
                    phone = data.get('phone', '')
                    message = data.get('message', '')
                    result = send_sms(phone, message)
                    if result["success"]:
                        # Add delay between messages
                        time.sleep(CONFIG["message_delay"])
                
                elif action == 'check_update':
                    result = check_for_update()
                
                elif action == 'perform_update':
                    download_url = data.get('download_url', CONFIG["download_url"])
                    result = perform_update(download_url)
                    if result.get("success"):
                        # Quit the app after a short delay to let response send
                        def quit_app():
                            time.sleep(0.5)
                            os._exit(0)
                        threading.Thread(target=quit_app, daemon=True).start()
                
                else:
                    result = {"error": "Unknown action"}
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404)

def find_free_port():
    """Find a free port to use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def signal_launcher_ready():
    """Signal to launcher that main app is ready."""
    import tempfile
    signal_file = os.path.join(tempfile.gettempdir(), "sms_campaign_ready.signal")
    try:
        with open(signal_file, 'w') as f:
            f.write(str(time.time()))
        print(f"Signaled ready to launcher")
    except Exception as e:
        print(f"Failed to signal: {e}")

# Global reference to window for API
_window = None

class Api:
    """API class exposed to JavaScript via pywebview."""
    
    def resize_and_center(self, width, height):
        """Resize and keep the window centered on itself (same center point)."""
        global _window
        if not _window:
            print("[DEBUG] resize_and_center: _window is None")
            return
        
        new_width = int(width)
        new_height = int(height)
        
        try:
            import AppKit
            import objc
            
            # Get the NSWindow from pywebview
            ns_window = None
            for window in AppKit.NSApplication.sharedApplication().windows():
                title = window.title()
                if title == 'Campagne SMS' or title == 'SMS Campaign':
                    ns_window = window
                    break
            
            if ns_window:
                # Get current window frame BEFORE any changes
                current_frame = ns_window.frame()
                old_width = current_frame.size.width
                old_height = current_frame.size.height
                old_x = current_frame.origin.x
                old_y = current_frame.origin.y
                
                # Calculate center point of old window
                center_x = old_x + old_width / 2
                center_y = old_y + old_height / 2
                
                # Calculate new position to keep same center point
                new_x = center_x - new_width / 2
                new_y = center_y - new_height / 2
                
                # Define a block to run on main thread
                def set_frame():
                    new_frame = AppKit.NSMakeRect(new_x, new_y, new_width, new_height)
                    ns_window.setFrame_display_animate_(new_frame, True, False)
                
                # Schedule on main thread
                AppKit.NSOperationQueue.mainQueue().addOperationWithBlock_(set_frame)
                
            else:
                _window.resize(new_width, new_height)
            
        except Exception as e:
            _window.resize(new_width, new_height)
    
    def resize(self, width, height):
        """Resize the window (calls resize_and_center)."""
        self.resize_and_center(width, height)
    
    def center(self):
        """Center the window on screen (no-op since resize_and_center does it)."""
        pass  # Already centered by resize_and_center

def main():
    """Main entry point using native window."""
    global _window
    
    port = find_free_port()
    server = HTTPServer(('127.0.0.1', port), RequestHandler)
    
    # Start server in background thread
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    url = f'http://127.0.0.1:{port}'
    print(f"Starting SMS Campaign v{VERSION}")
    
    api = Api()
    
    # Create native window (non-resizable, starts at loading size)
    _window = webview.create_window(
        'Campagne SMS',
        url,
        width=500,
        height=400,
        resizable=False,
        js_api=api
    )
    
    # Signal launcher when window is ready
    def on_loaded():
        signal_launcher_ready()
    
    _window.events.loaded += on_loaded
    
    webview.start()
    
    # Cleanup
    server.shutdown()

if __name__ == "__main__":
    main()

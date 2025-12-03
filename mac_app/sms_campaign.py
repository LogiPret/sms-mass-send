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
import threading
from pathlib import Path

PORT = 8765

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
        
        .footer-debug {
            margin-top: 20px;
            padding: 15px;
            background: #2a2a2c;
            border-radius: 10px;
            text-align: center;
            color: #5a5a5e;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Step 1: Select CSV -->
        <div id="step1">
            <div class="step-indicator" data-i18n="step1of4">Step 1 of 4</div>
            <h1>📁 <span data-i18n="selectFile">Select CSV File</span></h1>
            <p class="description" data-i18n="selectFileDesc">Choose a CSV file containing your contacts with names and phone numbers.</p>
            
            <div class="file-drop" id="fileDrop" onclick="document.getElementById('csvFile').click()">
                <div class="file-icon">📄</div>
                <div data-i18n="clickToSelect">Click to select CSV file</div>
                <div class="file-name" id="fileName"></div>
            </div>
            <input type="file" id="csvFile" accept=".csv" onchange="handleFile(this)">
            
            <div class="nav-buttons">
                <div></div>
                <button class="btn btn-primary" id="next1" disabled onclick="goToStep(2)" data-i18n="next">Next →</button>
            </div>
        </div>
        
        <!-- Step 2: Map Columns -->
        <div id="step2" style="display:none">
            <div class="step-indicator" data-i18n="step2of4">Step 2 of 4</div>
            <h1>📊 <span data-i18n="mapColumns">Map Columns</span></h1>
            <p class="description" data-i18n="mapColumnsDesc">Click on column headers to assign them. First click = Name, Second click = Phone.</p>
            
            <div class="mapping-legend">
                <div class="legend-item">
                    <div class="legend-dot name"></div>
                    <span data-i18n="nameColumn">Name Column</span>
                </div>
                <div class="legend-item">
                    <div class="legend-dot phone"></div>
                    <span data-i18n="phoneColumn">Phone Column</span>
                </div>
            </div>
            
            <div id="mappingMode" class="mapping-mode" data-i18n="clickName">👆 Click the NAME column</div>
            
            <div class="column-mapper" id="columnMapper"></div>
            
            <div class="info-box">
                <span data-i18n="foundContacts">Found</span> <strong id="contactCount">0</strong> <span data-i18n="contacts">contacts</span>
            </div>
            
            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="goToStep(1)" data-i18n="back">← Back</button>
                <button class="btn btn-primary" id="next2" disabled onclick="goToStep(3)" data-i18n="next">Next →</button>
            </div>
        </div>
        
        <!-- Step 3: Compose Message -->
        <div id="step3" style="display:none">
            <div class="step-indicator" data-i18n="step3of4">Step 3 of 4</div>
            <h1>💬 <span data-i18n="composeMessage">Compose Message</span></h1>
            <p class="description" data-i18n="composeDesc">Write your message. Use {name} to personalize with recipient's name.</p>
            
            <button class="insert-btn" onclick="insertName()" data-i18n="insertName">Insert {name}</button>
            <textarea id="message" data-placeholder-i18n="typemessage" placeholder="Type your message here..." oninput="updateCharCount()"></textarea>
            <div class="char-count"><span id="charCount">0</span> <span data-i18n="characters">characters</span></div>
            
            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="goToStep(2)" data-i18n="back">← Back</button>
                <button class="btn btn-primary" onclick="preparePreview()" data-i18n="next">Next →</button>
            </div>
        </div>
        
        <!-- Step 4: Preview (Debug-style) -->
        <div id="step4" style="display:none">
            <div class="step-indicator" data-i18n="step4of4">Step 4 of 4</div>
            <h1>📱 <span data-i18n="previewSend">Preview & Send</span></h1>
            
            <div class="stats">
                <div class="stat valid">
                    <div class="num" id="validCount">0</div>
                    <div class="label" data-i18n="valid">Valid</div>
                </div>
                <div class="stat skip">
                    <div class="num" id="skipCount">0</div>
                    <div class="label" data-i18n="skipped">Skipped</div>
                </div>
            </div>
            
            <h2 data-i18n="validContacts">Valid Contacts</h2>
            <div class="scroll-container">
                <table class="preview-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th data-i18n="name">Name</th>
                            <th data-i18n="phone">Phone</th>
                            <th data-i18n="source">Source</th>
                        </tr>
                    </thead>
                    <tbody id="validList"></tbody>
                </table>
            </div>
            
            <div id="skippedSection" style="display:none">
                <h2 data-i18n="skippedContacts">Skipped Contacts</h2>
                <div class="scroll-container">
                    <table class="preview-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th data-i18n="reason">Reason</th>
                                <th data-i18n="rawData">Raw Data</th>
                            </tr>
                        </thead>
                        <tbody id="skipList"></tbody>
                    </table>
                </div>
            </div>
            
            <h2>📝 <span data-i18n="messagePreview">Message Preview</span></h2>
            <div class="message-preview" id="messagePreview"></div>
            
            <div class="nav-buttons">
                <button class="btn btn-secondary" onclick="goToStep(3)" data-i18n="back">← Back</button>
                <button class="btn btn-success" onclick="startSending()" data-i18n="sendAll">📱 Send All SMS</button>
            </div>
        </div>
        
        <!-- Step 5: Sending -->
        <div id="step5" style="display:none">
            <h1>📤 <span data-i18n="sending">Sending Messages...</span></h1>
            <p class="description" id="sendStatus" data-i18n="preparing">Preparing to send...</p>
            
            <div class="progress-container">
                <div class="progress-bar" id="progressBar" style="width:0%"></div>
            </div>
            
            <div class="log" id="sendLog"></div>
            
            <div class="nav-buttons" id="doneButtons" style="display:none">
                <div></div>
                <button class="btn btn-primary" onclick="window.close()" data-i18n="done">Done</button>
            </div>
        </div>
    </div>
    
    <!-- Language Toggle -->
    <div class="lang-toggle">
        <button class="lang-btn active" id="btnEN" onclick="setLang('en')">EN</button>
        <button class="lang-btn" id="btnFR" onclick="setLang('fr')">FR</button>
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
                clickName: "👆 Click the NAME column",
                clickPhone: "👆 Now click the PHONE column",
                mappingDone: "✅ Mapping complete!",
                foundContacts: "Found",
                contacts: "contacts",
                composeMessage: "Compose Message",
                composeDesc: "Write your message. Use {name} to personalize with recipient's name.",
                insertName: "Insert {name}",
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
                sendAll: "📱 Send All SMS",
                sending: "Sending Messages...",
                preparing: "Preparing to send...",
                done: "Done",
                noPhone: "No phone number",
                noName: "No name",
                confirmSend: "Send {count} SMS messages?",
                sendingProgress: "Sending {current} of {total}...",
                complete: "✅ Complete! Sent: {sent}, Failed: {failed}"
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
                clickName: "👆 Cliquez sur la colonne NOM",
                clickPhone: "👆 Maintenant cliquez sur la colonne TÉLÉPHONE",
                mappingDone: "✅ Mapping terminé!",
                foundContacts: "Trouvé",
                contacts: "contacts",
                composeMessage: "Composer le message",
                composeDesc: "Écrivez votre message. Utilisez {name} pour personnaliser avec le nom du destinataire.",
                insertName: "Insérer {name}",
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
                sendAll: "📱 Envoyer tous les SMS",
                sending: "Envoi en cours...",
                preparing: "Préparation de l'envoi...",
                done: "Terminé",
                noPhone: "Pas de numéro",
                noName: "Pas de nom",
                confirmSend: "Envoyer {count} messages SMS?",
                sendingProgress: "Envoi {current} sur {total}...",
                complete: "✅ Terminé! Envoyés: {sent}, Échoués: {failed}"
            }
        };
        
        let currentLang = 'en';
        
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
        
        // ============ DATA ============
        let csvData = [];
        let headers = [];
        let recipients = [];
        let skipped = [];
        let nameCol = -1;
        let phoneCol = -1;
        let mappingStep = 0; // 0 = select name, 1 = select phone, 2 = done
        
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
                
                headers = parseCSVLine(lines[0], separator);
                csvData = lines.slice(1).map((line, idx) => ({
                    lineNumber: idx + 2,
                    values: parseCSVLine(line, separator)
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
            updateMappingMode();
        }
        
        function selectColumn(col) {
            if (mappingStep === 0) {
                // Selecting name column
                nameCol = col;
                mappingStep = 1;
            } else if (mappingStep === 1) {
                // Selecting phone column
                if (col === nameCol) return; // Can't select same column
                phoneCol = col;
                mappingStep = 2;
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
        
        function updateMappingMode() {
            const mode = document.getElementById('mappingMode');
            if (mappingStep === 0) {
                mode.textContent = t('clickName');
                mode.style.background = '#30d158';
            } else if (mappingStep === 1) {
                mode.textContent = t('clickPhone');
                mode.style.background = '#ff9f0a';
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
            ta.value = text.slice(0, pos) + '{name}' + text.slice(pos);
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
                const name = row.values[nameCol] || '';
                const rawPhone = row.values[phoneCol] || '';
                const { phone, source } = extractBestPhone(rawPhone);
                
                if (!phone) {
                    skipped.push({
                        lineNumber: row.lineNumber,
                        reason: t('noPhone'),
                        raw: name + ' | ' + rawPhone.substring(0, 40)
                    });
                } else if (!name.trim()) {
                    skipped.push({
                        lineNumber: row.lineNumber,
                        reason: t('noName'),
                        raw: phone
                    });
                } else {
                    recipients.push({
                        lineNumber: row.lineNumber,
                        name: name.trim(),
                        phone: phone,
                        phoneSource: source,
                        message: msg.replace(/{name}/g, name.trim())
                    });
                }
            });
            
            // Update stats
            document.getElementById('validCount').textContent = recipients.length;
            document.getElementById('skipCount').textContent = skipped.length;
            
            // Populate valid list
            const validList = document.getElementById('validList');
            validList.innerHTML = recipients.slice(0, 50).map(r => `
                <tr>
                    <td>${r.lineNumber}</td>
                    <td>${r.name}</td>
                    <td class="phone">${r.phone}</td>
                    <td class="source">${r.phoneSource || ''}</td>
                </tr>
            `).join('');
            
            if (recipients.length > 50) {
                validList.innerHTML += `<tr><td colspan="4" style="color:#5a5a5e;text-align:center">... ${recipients.length - 50} more</td></tr>`;
            }
            
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
    </script>
</body>
</html>'''


class SMSHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
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


def main():
    os.system(f"lsof -ti:{PORT} | xargs kill -9 2>/dev/null")
    
    with socketserver.TCPServer(("", PORT), SMSHandler) as httpd:
        url = f"http://localhost:{PORT}"
        print(f"SMS Campaign running at {url}")
        print("Press Ctrl+C to stop")
        
        webbrowser.open(url)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()

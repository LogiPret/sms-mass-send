// SMS Mass Send - Scriptable Script
// Version 1.0
// Pour iPhone - Envoi de SMS en masse depuis un CSV

// ============================================
// AUTO-UPDATE CONFIGURATION
// ============================================
const SCRIPT_VERSION = "1.1.13";
const SCRIPT_NAME = "script"; // Must match filename in Scriptable
const UPDATE_URL = "https://raw.githubusercontent.com/hugootth/sms-mass-send/main/script.js";
const VERSION_URL = "https://raw.githubusercontent.com/hugootth/sms-mass-send/main/version.json";

// ============================================
// AUTO-UPDATE FUNCTION
// ============================================

// Compare semantic versions (handles 1.1 vs 1.1.4 correctly)
function isNewerVersion(latest, current) {
    const latestParts = latest.split('.').map(n => parseInt(n) || 0);
    const currentParts = current.split('.').map(n => parseInt(n) || 0);
    
    while (latestParts.length < 3) latestParts.push(0);
    while (currentParts.length < 3) currentParts.push(0);
    
    for (let i = 0; i < 3; i++) {
        if (latestParts[i] > currentParts[i]) return true;
        if (latestParts[i] < currentParts[i]) return false;
    }
    return false; // Equal
}

async function checkForUpdates(silent = false) {
    try {
        // Add cache-busting parameter AND no-cache headers
        let cacheBuster = new Date().getTime();
        let req = new Request(VERSION_URL + "?cb=" + cacheBuster);
        req.timeoutInterval = 10;
        req.headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        };
        let versionInfo = await req.loadJSON();
        
        const currentVersion = SCRIPT_VERSION;
        const latestVersion = versionInfo.version;
        const shouldUpdate = isNewerVersion(latestVersion, currentVersion);
        
        // DEBUG: Always show what's happening
        let debugAlert = new Alert();
        debugAlert.title = "🔍 Debug Update Check";
        debugAlert.message = `Current: ${currentVersion}\nLatest: ${latestVersion}\nShould update: ${shouldUpdate}\nURL: ...?cb=${cacheBuster}`;
        debugAlert.addAction("OK");
        await debugAlert.present();
        
        // Compare versions properly
        if (shouldUpdate) {
            // New version available!
            let alert = new Alert();
            alert.title = "🔄 Mise à jour disponible!";
            alert.message = `Version ${latestVersion} disponible (vous avez ${currentVersion})\n\n${versionInfo.changelog || ""}`;
            alert.addAction("Mettre à jour");
            alert.addCancelAction("Plus tard");
            
            let choice = await alert.present();
            
            if (choice === 0) {
                // Download and install update
                await installUpdate();
                return true; // Script was updated, should restart
            }
        } else if (!silent) {
            let alert = new Alert();
            alert.title = "✅ À jour!";
            alert.message = `Vous avez la dernière version (${currentVersion})`;
            alert.addAction("OK");
            await alert.present();
        }
    } catch (error) {
        // DEBUG: Show the error
        let errAlert = new Alert();
        errAlert.title = "❌ Update Error";
        errAlert.message = String(error);
        errAlert.addAction("OK");
        await errAlert.present();
    }
    return false;
}

async function installUpdate() {
    try {
        // Download the new script with cache busting
        let cacheBuster = new Date().getTime();
        let req = new Request(UPDATE_URL + "?cb=" + cacheBuster);
        req.headers = {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        };
        let newScript = await req.loadString();
        
        if (!newScript || newScript.length < 100) {
            throw new Error("Downloaded script is empty or too short");
        }
        
        // Try to find and update the script file
        let fm;
        let scriptPath;
        let success = false;
        
        // Try iCloud first
        try {
            fm = FileManager.iCloud();
            scriptPath = fm.joinPath(fm.documentsDirectory(), SCRIPT_NAME + ".js");
            if (fm.fileExists(scriptPath)) {
                fm.writeString(scriptPath, newScript);
                success = true;
            }
        } catch (e) {
            // iCloud not available
        }
        
        // Try local storage if iCloud didn't work
        if (!success) {
            try {
                fm = FileManager.local();
                scriptPath = fm.joinPath(fm.documentsDirectory(), SCRIPT_NAME + ".js");
                if (fm.fileExists(scriptPath)) {
                    fm.writeString(scriptPath, newScript);
                    success = true;
                }
            } catch (e) {
                // Local also failed
            }
        }
        
        // If still no success, try to find by listing files
        if (!success) {
            fm = FileManager.local();
            let docs = fm.documentsDirectory();
            let files = fm.listContents(docs);
            let scriptFiles = files.filter(f => f.endsWith('.js'));
            
            let alert = new Alert();
            alert.title = "📁 Debug: Script Files";
            alert.message = `Looking for: "${SCRIPT_NAME}.js"\n\nFound:\n${scriptFiles.join('\n')}\n\nPath tried: ${scriptPath}`;
            alert.addAction("OK");
            await alert.present();
            return;
        }
        
        let alert = new Alert();
        alert.title = "✅ Mise à jour installée!";
        alert.message = `Script mis à jour!\nPath: ${scriptPath}\nTaille: ${newScript.length} chars\n\nVeuillez relancer le script.`;
        alert.addAction("OK");
        await alert.present();
        
        return;
        
    } catch (error) {
        let alert = new Alert();
        alert.title = "❌ Erreur";
        alert.message = "Impossible de télécharger la mise à jour: " + String(error);
        alert.addAction("OK");
        await alert.present();
    }
}

// ============================================
// CONFIGURATION
// ============================================
const DEBUG_MODE = true;

const CONFIG = {
    // Colonne téléphone générique (format multi ou simple)
    phoneColumns: ['phone', 'telephone', 'tel', 'numéro', 'numero', 'b2_telephone'],
    
    // Colonnes téléphone séparées par type (priorité: mobile > work > home)
    mobileColumns: ['mobile', 'cell', 'cellulaire', 'cellular', 'cell_phone', 'mobile_phone'],
    workColumns: ['work', 'travail', 'bureau', 'office', 'work_phone', 'business', 'professionnel'],
    homeColumns: ['home', 'maison', 'domicile', 'residence', 'home_phone', 'personnel'],
    
    firstNameColumns: ['prenom', 'prénom', 'firstname', 'first name', 'first', 'given name', 'b2_prenom', 'b2_prénom'],
    lastNameColumns: ['nom', 'lastname', 'last name', 'last', 'family name', 'surname', 'b2_nom', 'famille'],
    
    // Variables dans le message
    firstNameVar: '**PRENOM**',
    lastNameVar: '**NOM**',
    
    // Priorité des types de téléphone pour format multi (premier = priorité haute)
    phonePriority: ['mobile', 'cell', 'cellulaire', 'work', 'travail', 'bureau', 'home', 'maison', 'domicile']
};

// ============================================
// FRENCH CHARACTER FIXES
// ============================================
// Fixes corrupted French accents from latin-1 encoding issues
// The � character appears when encoding is mismatched

function fixFrenchAccents(text) {
    if (!text || typeof text !== 'string') return text;
    
    // Common French name patterns with é (most common)
    const patternsE = [
        // First names starting with É
        /\bEmilie\b/gi,
        /\bEric\b/gi,
        /\bEtienne\b/gi,
        /\bEliane\b/gi,
        /\bElise\b/gi,
        // Names with é in middle
        /Stephanie/gi,
        /Stephane/gi,
        /Genevieve/gi,  // has both é and è, we'll fix è separately
        /Frederic/gi,
        /Frederique/gi,
        /Frederike/gi,
        /Valerie/gi,
        /Amelie/gi,
        /Melanie/gi,
        /Helene/gi,
        /Rene\b/gi,
        /Andre\b/gi,
        /Jerome/gi,
        /Therese/gi,
        /Mylene/gi,
        /Benedicte/gi,
        /Beatrice/gi,
        /Veronique/gi,
        /Sebastien/gi,
        /Cedric/gi,
        /Gerard/gi,
        /Desire/gi,
        /Remi/gi,
        // Last names
        /Bedard/gi,
        /Bechard/gi,
        /Berube/gi,
        /Bezeau/gi,
        /Beaulieu/gi,
        /Desrosiers/gi,
        /Levesque/gi,
        /Leveille/gi,
        /Legare/gi,
        /Leger/gi,
        /Lepine/gi,
        /Lemelin/gi,
        /Pere\b/gi,
        /Mere\b/gi,
        /Menard/gi,
        /Prevost/gi,
        /Theoret/gi,
        /Tetu/gi,
        /Seguin/gi,
        /Senecal/gi,
        /Gregoire/gi,
        /Cote\b/gi,  // word boundary to avoid matching inside other words
        /Crete/gi,
    ];
    
    // Known full name replacements (case insensitive matching, preserve case in output)
    const knownReplacements = {
        // É at start
        'emilie': 'Émilie',
        'eric': 'Éric',
        'etienne': 'Étienne',
        'eliane': 'Éliane',
        'elise': 'Élise',
        // é in middle
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
        // Last names
        'bedard': 'Bédard',
        'bechard': 'Béchard',
        'berube': 'Bérubé',
        'bezeau': 'Bézeau',
        'beaulieu': 'Beaulieu',  // no accent
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
    };
    
    // First, try to fix the � character by detecting patterns
    // If text contains �, we need to figure out what it should be
    if (text.includes('�')) {
        // Try to match against known patterns
        let cleanText = text.replace(/�/g, '');  // Remove corrupted chars
        let lowerClean = cleanText.toLowerCase();
        
        // Check for known names
        for (let [plain, accented] of Object.entries(knownReplacements)) {
            // Check if the clean text matches the plain version
            if (lowerClean === plain || lowerClean.includes(plain)) {
                // Replace in the original text
                let regex = new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/�/g, '.'), 'i');
                return text.replace(/�./g, (match, offset) => {
                    // Find position in accented version
                    let pos = text.substring(0, offset).replace(/�/g, '').length;
                    return accented.charAt(pos) || match;
                });
            }
        }
        
        // Specific pattern replacements for common corruptions
        // St�phanie -> Stéphanie, St�phan -> Stéphan
        text = text.replace(/St�phan/gi, 'Stéphan');
        text = text.replace(/St�ph/gi, 'Stéph');
        
        // �milie, �ric, �tienne -> É...
        text = text.replace(/^�milie$/i, 'Émilie');
        text = text.replace(/^�ric$/i, 'Éric');
        text = text.replace(/^�tienne$/i, 'Étienne');
        text = text.replace(/^�liane$/i, 'Éliane');
        text = text.replace(/^�lise$/i, 'Élise');
        
        // B�dard -> Bédard
        text = text.replace(/B�dard/gi, 'Bédard');
        
        // Larosili�re -> Larosilière
        text = text.replace(/li�re\b/gi, 'lière');
        text = text.replace(/ti�re\b/gi, 'tière');
        text = text.replace(/ni�re\b/gi, 'nière');
        text = text.replace(/ri�re\b/gi, 'rière');
        text = text.replace(/mi�re\b/gi, 'mière');
        text = text.replace(/pi�re\b/gi, 'pière');
        text = text.replace(/vi�re\b/gi, 'vière');
        text = text.replace(/ci�re\b/gi, 'cière');
        text = text.replace(/di�re\b/gi, 'dière');
        text = text.replace(/si�re\b/gi, 'sière');
        text = text.replace(/gi�re\b/gi, 'gière');
        
        // Fran�ais -> Français, Fran�ois -> François
        text = text.replace(/Fran�ais/gi, 'Français');
        text = text.replace(/Fran�ois/gi, 'François');
        text = text.replace(/Fran�oise/gi, 'Françoise');
        
        // Ren�, Andr�, etc. (é at end after consonant)
        text = text.replace(/n�\b/g, 'né');
        text = text.replace(/r�\b/g, 'ré');
        text = text.replace(/l�\b/g, 'lé');
        text = text.replace(/t�\b/g, 'té');
        text = text.replace(/d�\b/g, 'dé');
        text = text.replace(/s�\b/g, 'sé');
        text = text.replace(/m�\b/g, 'mé');
        
        // G�rard, S�bastien, C�dric, R�mi, etc. (é after consonant before vowel)
        text = text.replace(/G�rard/gi, 'Gérard');
        text = text.replace(/S�bastien/gi, 'Sébastien');
        text = text.replace(/C�dric/gi, 'Cédric');
        text = text.replace(/R�mi/gi, 'Rémi');
        text = text.replace(/R�gis/gi, 'Régis');
        text = text.replace(/D�nis/gi, 'Dénis');
        text = text.replace(/B�atrice/gi, 'Béatrice');
        text = text.replace(/Th�r�se/gi, 'Thérèse');
        text = text.replace(/H�l�ne/gi, 'Hélène');
        text = text.replace(/Genevi�ve/gi, 'Geneviève');
        text = text.replace(/V�ronique/gi, 'Véronique');
        text = text.replace(/Val�rie/gi, 'Valérie');
        text = text.replace(/Am�lie/gi, 'Amélie');
        text = text.replace(/M�lanie/gi, 'Mélanie');
        text = text.replace(/Myl�ne/gi, 'Mylène');
        text = text.replace(/Fr�d�ric/gi, 'Frédéric');
        text = text.replace(/Fr�d�rique/gi, 'Frédérique');
        
        // L�vesque, L�ger, L�pine, M�nard, S�guin, etc.
        text = text.replace(/L�vesque/gi, 'Lévesque');
        text = text.replace(/L�ger/gi, 'Léger');
        text = text.replace(/L�pine/gi, 'Lépine');
        text = text.replace(/M�nard/gi, 'Ménard');
        text = text.replace(/S�guin/gi, 'Séguin');
        text = text.replace(/S�n�cal/gi, 'Sénécal');
        text = text.replace(/Pr�vost/gi, 'Prévost');
        text = text.replace(/Th�oret/gi, 'Théoret');
        text = text.replace(/Gr�goire/gi, 'Grégoire');
        text = text.replace(/B�rub�/gi, 'Bérubé');
        text = text.replace(/L�gar�/gi, 'Légaré');
        text = text.replace(/C�t�/gi, 'Côté');
        text = text.replace(/T�tu/gi, 'Têtu');
        text = text.replace(/Cr�te/gi, 'Crête');
        
        // If still has �, try generic replacements based on position
        // Most remaining cases: � before consonant = é, � before 're' = è
        if (text.includes('�')) {
            // è patterns (before re, ve, le, ne at end of word)
            text = text.replace(/�ve\b/gi, 'ève');
            text = text.replace(/�le\b/gi, 'èle');
            text = text.replace(/�ne\b/gi, 'ène');
            text = text.replace(/�me\b/gi, 'ème');
            text = text.replace(/�te\b/gi, 'ète');
            text = text.replace(/�se\b/gi, 'èse');
            text = text.replace(/�ce\b/gi, 'èce');
            text = text.replace(/�de\b/gi, 'ède');
            text = text.replace(/�ge\b/gi, 'ège');
            text = text.replace(/�pe\b/gi, 'èpe');
            text = text.replace(/�re\b/gi, 'ère');  // Père, Mère
            
            // Default: remaining � is probably é
            text = text.replace(/�/g, 'é');
        }
    }
    
    return text;
}

// ============================================
// MAIN
// ============================================
async function main() {
    try {
        // Check for updates silently at launch
        let updated = await checkForUpdates(true);
        if (updated) return; // Script was updated, exit
        
        // Étape 1: Sélection du fichier CSV (pas de welcome screen)
        let csvContent = await selectCSVFile();
        if (!csvContent) return;
        
        // Étape 2: Parser le CSV
        let { headers, rows, columnMap, separator } = parseCSV(csvContent);
        
        if (rows.length === 0) {
            await showError("Le fichier CSV est vide ou ne contient que l'en-tête.");
            return;
        }
        
        // Vérifier colonnes essentielles (silencieux si OK)
        // On accepte soit une colonne téléphone générique, soit des colonnes séparées mobile/work/home
        let hasPhoneColumn = columnMap.phone >= 0 || columnMap.phoneMobile >= 0 || columnMap.phoneWork >= 0 || columnMap.phoneHome >= 0;
        if (!hasPhoneColumn) {
            await showError("Colonne téléphone non trouvée.\nUtilise: phone, telephone, mobile, work, home, etc.");
            return;
        }
        
        // Étape 3: Saisie du message
        let messageTemplate = await getMessageTemplate();
        if (!messageTemplate) return;
        
        // Étape 4: Préparer les contacts
        let { validContacts, skippedContacts } = prepareContacts(rows, headers, columnMap);
        
        if (validContacts.length === 0) {
            // Afficher plus de détails pour debug
            let debugInfo = `Colonnes détectées:\n`;
            debugInfo += `• Prénom: ${columnMap.firstName >= 0 ? headers[columnMap.firstName] : 'NON TROUVÉ'}\n`;
            debugInfo += `• Nom: ${columnMap.lastName >= 0 ? headers[columnMap.lastName] : 'NON TROUVÉ'}\n`;
            debugInfo += `• Tél: ${columnMap.phone >= 0 ? headers[columnMap.phone] : 'NON TROUVÉ'}\n`;
            debugInfo += `• Mobile: ${columnMap.phoneMobile >= 0 ? headers[columnMap.phoneMobile] : 'NON TROUVÉ'}\n`;
            debugInfo += `• Work: ${columnMap.phoneWork >= 0 ? headers[columnMap.phoneWork] : 'NON TROUVÉ'}\n`;
            debugInfo += `• Home: ${columnMap.phoneHome >= 0 ? headers[columnMap.phoneHome] : 'NON TROUVÉ'}\n\n`;
            debugInfo += `Séparateur: ${separator}\n`;
            debugInfo += `Lignes: ${rows.length}\n`;
            debugInfo += `Headers: ${headers.length}\n\n`;
            // Afficher tous les headers
            debugInfo += `Tous les headers:\n`;
            for (let i = 0; i < Math.min(8, headers.length); i++) {
                debugInfo += `[${i}] ${headers[i]}\n`;
            }
            debugInfo += `\n`;
            if (rows.length > 0) {
                debugInfo += `1ère ligne valeurs:\n`;
                for (let i = 0; i < Math.min(8, rows[0].values.length); i++) {
                    debugInfo += `[${i}] ${rows[0].values[i]}\n`;
                }
            }
            await showError(`Aucun contact valide.\n\n${debugInfo}`);
            return;
        }
        
        // MODE DEBUG : Afficher le rapport sans envoyer
        if (DEBUG_MODE) {
            await showDebugReport(validContacts, skippedContacts, messageTemplate, separator);
            return;
        }
        
        // Étape 5: Toujours afficher le rapport de preview pour vérification
        let shouldContinue = await showPreviewReport(validContacts, skippedContacts, messageTemplate, separator);
        if (!shouldContinue) return;
        
        // Étape 6: Envoyer les messages (mode rapide)
        let result = await sendMessagesFast(validContacts, messageTemplate);
        
        // Étape 7: Rapport final
        if (result.stopped) {
            let alert = new Alert();
            alert.title = "🛑 Arrêté";
            alert.message = `Envoi arrêté à ${result.stoppedAt}.\n\n✅ ${result.sentCount} message(s) envoyé(s)\n❌ ${validContacts.length - result.sentCount} non envoyé(s)`;
            alert.addAction("OK");
            await alert.present();
        } else {
            await showReport(result.sentCount, validContacts.length, skippedContacts);
        }
        
    } catch (error) {
        await showError(`Erreur: ${error.message}`);
    }
}

// ============================================
// FONCTIONS DE SÉLECTION FICHIER
// ============================================
async function selectCSVFile() {
    try {
        let files = await DocumentPicker.open(["public.comma-separated-values-text", "public.plain-text"]);
        if (files.length === 0) return null;
        
        let filePath = files[0];
        let fm = FileManager.local();
        
        // Lire le contenu du fichier
        let content = fm.readString(filePath);
        
        if (!content || content.trim().length === 0) {
            await showError("Le fichier est vide.");
            return null;
        }
        
        return content;
    } catch (error) {
        if (error.message.includes("cancel")) {
            return null;
        }
        await showError(`Erreur lors de la lecture: ${error.message}`);
        return null;
    }
}

// ============================================
// FONCTIONS DE PARSING CSV
// ============================================
function detectSeparator(content) {
    // Prendre les premières lignes pour détecter le séparateur
    let firstLines = content.split(/\r?\n/).slice(0, 5).join('\n');
    
    // Compter les occurrences de chaque séparateur potentiel
    let separators = [
        { char: ',', name: 'virgule', count: (firstLines.match(/,/g) || []).length },
        { char: ';', name: 'point-virgule', count: (firstLines.match(/;/g) || []).length },
        { char: '\t', name: 'tabulation', count: (firstLines.match(/\t/g) || []).length }
    ];
    
    // Retourner celui avec le plus d'occurrences
    separators.sort((a, b) => b.count - a.count);
    return separators[0];
}

function parseCSV(content) {
    let sepInfo = detectSeparator(content);
    let separator = sepInfo.char;
    console.log(`Séparateur détecté: ${sepInfo.name} (${sepInfo.count} occurrences)`);
    
    let lines = content.split(/\r?\n/).filter(line => line.trim().length > 0);
    
    if (lines.length === 0) {
        return { headers: [], rows: [], columnMap: {}, separator: sepInfo.name };
    }
    
    // Parser l'en-tête
    let headers = parseCSVLine(lines[0], separator);
    
    // Parser les lignes de données
    let rows = [];
    for (let i = 1; i < lines.length; i++) {
        let values = parseCSVLine(lines[i], separator);
        rows.push({
            lineNumber: i + 1,
            originalLine: lines[i],
            values: values
        });
    }
    
    // Détecter les colonnes
    let columnMap = detectColumns(headers);
    
    return { headers, rows, columnMap, separator: sepInfo.name };
}

function parseCSVLine(line, separator = ',') {
    let result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        let char = line[i];
        let nextChar = line[i + 1];
        
        if (char === '"') {
            if (inQuotes && nextChar === '"') {
                // Guillemet échappé
                current += '"';
                i++;
            } else {
                // Toggle état guillemet
                inQuotes = !inQuotes;
            }
        } else if (char === separator && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current.trim());
    return result;
}

function normalizeText(text) {
    // Supprimer les accents et caractères spéciaux, normaliser
    if (!text) return '';
    return text
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')  // Remove accents
        .replace(/[�]/g, 'e')              // Handle broken encoding
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '_');
}

function detectColumns(headers) {
    let columnMap = {
        phone: -1,        // Colonne téléphone générique (format multi)
        phoneMobile: -1,  // Colonne mobile séparée
        phoneWork: -1,    // Colonne travail séparée
        phoneHome: -1,    // Colonne maison séparée
        firstName: -1,
        lastName: -1
    };
    
    for (let i = 0; i < headers.length; i++) {
        let header = headers[i].toLowerCase().trim();
        let headerNormalized = normalizeText(headers[i]);
        
        // Debug: afficher dans console
        console.log(`Header[${i}]: "${header}" -> normalized: "${headerNormalized}"`);
        
        // Détecter colonne mobile
        if (columnMap.phoneMobile === -1) {
            for (let name of CONFIG.mobileColumns) {
                let nameNorm = normalizeText(name);
                if (header === name || headerNormalized === nameNorm ||
                    header.includes(name) && !header.includes('work') && !header.includes('home')) {
                    columnMap.phoneMobile = i;
                    break;
                }
            }
        }
        
        // Détecter colonne travail
        if (columnMap.phoneWork === -1) {
            for (let name of CONFIG.workColumns) {
                let nameNorm = normalizeText(name);
                if (header === name || headerNormalized === nameNorm ||
                    header.includes(name)) {
                    columnMap.phoneWork = i;
                    break;
                }
            }
        }
        
        // Détecter colonne maison
        if (columnMap.phoneHome === -1) {
            for (let name of CONFIG.homeColumns) {
                let nameNorm = normalizeText(name);
                if (header === name || headerNormalized === nameNorm ||
                    header.includes(name)) {
                    columnMap.phoneHome = i;
                    break;
                }
            }
        }
        
        // Détecter téléphone générique (si pas déjà une colonne spécifique)
        if (columnMap.phone === -1 && columnMap.phoneMobile !== i && columnMap.phoneWork !== i && columnMap.phoneHome !== i) {
            for (let name of CONFIG.phoneColumns) {
                let nameNorm = normalizeText(name);
                if (header.includes(name) || headerNormalized.includes(nameNorm)) {
                    columnMap.phone = i;
                    break;
                }
            }
        }
        
        // Détecter prénom - DOIT être vérifié AVANT nom car "prénom" contient "nom"
        // Chercher spécifiquement "prenom" ou "first" mais PAS si c'est "nom_de_famille"
        if (columnMap.firstName === -1) {
            // Vérifier si c'est un prénom (et pas un nom de famille)
            let isFirstName = false;
            
            // Patterns spécifiques pour prénom
            if (headerNormalized.includes('prenom') || 
                headerNormalized.includes('first') ||
                headerNormalized.includes('given')) {
                isFirstName = true;
            }
            
            // Exclure si c'est clairement un nom de famille
            if (headerNormalized.includes('famille') || 
                headerNormalized.includes('family') ||
                headerNormalized.includes('nom_de_famille')) {
                isFirstName = false;
            }
            
            if (isFirstName) {
                columnMap.firstName = i;
            }
        }
        
        // Détecter nom de famille
        if (columnMap.lastName === -1) {
            let isLastName = false;
            
            // Patterns spécifiques pour nom de famille
            if (headerNormalized.includes('nom_de_famille') ||
                headerNormalized.includes('famille') ||
                headerNormalized.includes('family') ||
                headerNormalized.includes('lastname') ||
                headerNormalized.includes('last_name') ||
                headerNormalized.includes('surname')) {
                isLastName = true;
            }
            
            // Simple "nom" mais PAS si c'est "prenom"
            if (!isLastName && headerNormalized.includes('nom') && !headerNormalized.includes('prenom')) {
                isLastName = true;
            }
            
            if (isLastName) {
                columnMap.lastName = i;
            }
        }
    }
    
    return columnMap;
}

// ============================================
// FONCTIONS DE PRÉPARATION CONTACTS
// ============================================
function prepareContacts(rows, headers, columnMap) {
    let validContacts = [];
    let skippedContacts = [];
    
    // Vérifier si on a des colonnes séparées pour mobile/work/home
    let hasSeparateColumns = columnMap.phoneMobile >= 0 || columnMap.phoneWork >= 0 || columnMap.phoneHome >= 0;
    
    for (let row of rows) {
        let rawFirstName = columnMap.firstName >= 0 ? row.values[columnMap.firstName] || '' : '';
        let rawLastName = columnMap.lastName >= 0 ? row.values[columnMap.lastName] || '' : '';
        
        let phoneExtraction;
        let rawPhone;
        
        if (hasSeparateColumns) {
            // Mode colonnes séparées: priorité mobile > work > home
            let phoneMobile = columnMap.phoneMobile >= 0 ? row.values[columnMap.phoneMobile] || '' : '';
            let phoneWork = columnMap.phoneWork >= 0 ? row.values[columnMap.phoneWork] || '' : '';
            let phoneHome = columnMap.phoneHome >= 0 ? row.values[columnMap.phoneHome] || '' : '';
            
            // Nettoyer les numéros (enlever espaces, tirets, etc.)
            phoneMobile = phoneMobile.replace(/[^0-9+]/g, '');
            phoneWork = phoneWork.replace(/[^0-9+]/g, '');
            phoneHome = phoneHome.replace(/[^0-9+]/g, '');
            
            // Sélectionner selon priorité: mobile > work > home
            if (phoneMobile && phoneMobile.length >= 10) {
                phoneExtraction = { phone: phoneMobile, source: 'mobile (colonne)' };
                rawPhone = phoneMobile;
            } else if (phoneWork && phoneWork.length >= 10) {
                phoneExtraction = { phone: phoneWork, source: 'work (colonne)' };
                rawPhone = phoneWork;
            } else if (phoneHome && phoneHome.length >= 10) {
                phoneExtraction = { phone: phoneHome, source: 'home (colonne)' };
                rawPhone = phoneHome;
            } else {
                // Aucun numéro valide dans les colonnes séparées
                phoneExtraction = { phone: '', source: 'vide' };
                rawPhone = `mobile: ${phoneMobile}, work: ${phoneWork}, home: ${phoneHome}`;
            }
        } else {
            // Mode colonne unique (format multi possible)
            rawPhone = columnMap.phone >= 0 ? row.values[columnMap.phone] || '' : '';
            phoneExtraction = extractPhoneFromMulti(rawPhone);
        }
        
        // Nettoyer le prénom et nom
        let firstName = cleanName(rawFirstName);
        let lastName = cleanName(rawLastName);
        
        // Formater le numéro
        let formattedPhone = formatPhoneNumber(phoneExtraction.phone);
        
        // Valider
        let skipReason = validateContact(formattedPhone, firstName);
        
        if (skipReason) {
            skippedContacts.push({
                lineNumber: row.lineNumber,
                originalLine: row.originalLine,
                reason: skipReason,
                rawData: { rawPhone, rawFirstName, rawLastName }
            });
        } else {
            validContacts.push({
                phone: formattedPhone,
                firstName: firstName,
                lastName: lastName,
                lineNumber: row.lineNumber,
                phoneSource: phoneExtraction.source,
                rawPhone: rawPhone
            });
        }
    }
    
    return { validContacts, skippedContacts };
}

function cleanName(name) {
    if (!name) return '';
    
    // Supprimer les guillemets orphelins
    name = name.replace(/"/g, '');
    
    // Corriger les accents français corrompus
    name = fixFrenchAccents(name);
    
    // Supprimer les caractères spéciaux au début et fin (garder les tirets et apostrophes au milieu)
    name = name.replace(/^[^a-zA-ZÀ-ÿ]+|[^a-zA-ZÀ-ÿ]+$/g, '');
    
    // Si contient une virgule, prendre seulement la première partie
    if (name.includes(',')) {
        name = name.split(',')[0].trim();
    }
    
    // Fonction helper pour capitaliser un mot tout en préservant les accents
    function capitalizeWord(word) {
        if (word.length === 0) return word;
        return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    }
    
    // Gérer les noms avec tiret (Anne-Marie, Jean-Pierre)
    name = name.split('-').map(capitalizeWord).join('-');
    
    // Gérer les espaces (noms composés comme "Marie Eve")
    name = name.split(' ').map(capitalizeWord).join(' ');
    
    // Gérer O'Brien, etc.
    name = name.replace(/'(\w)/g, (match, letter) => "'" + letter.toUpperCase());
    
    return name.trim();
}

function extractPhoneFromMulti(phoneField) {
    if (!phoneField) return { phone: '', source: 'vide' };
    
    let raw = phoneField.trim();
    
    // Si c'est un format simple (pas de | ou :), retourner directement
    if (!raw.includes('|') && !raw.includes(':')) {
        return { phone: raw, source: 'direct' };
    }
    
    // Format Velocity CRM: "4389266456 : work | 5798819696 : home | 4389266456 : mobile"
    // Le format est: numéro : type | numéro : type
    // Séparateur entre paires est |
    let pairs = raw.split('|').map(p => p.trim()).filter(p => p.length > 0);
    
    let phones = [];
    for (let pair of pairs) {
        // Séparer par : pour obtenir numéro et type
        let parts = pair.split(':').map(p => p.trim());
        if (parts.length >= 2) {
            // Format: "4389266456 : work" ou "4389266456 ext: 123 : work"
            let number = parts[0];
            let type = parts[parts.length - 1].toLowerCase(); // Dernier élément est le type
            
            // Si le numéro contient "ext", reconstruire
            if (parts.length > 2) {
                // Format avec extension: "4389266456 ext: 123 : work"
                number = parts.slice(0, parts.length - 1).join(':').trim();
            }
            
            // Vérifier que c'est bien un numéro (au moins 7 chiffres)
            if (number.replace(/\D/g, '').length >= 7) {
                phones.push({ type, number });
            }
        } else if (parts.length === 1) {
            // Juste un numéro sans type
            let digits = parts[0].replace(/\D/g, '');
            if (digits.length >= 10) {
                phones.push({ type: 'unknown', number: parts[0] });
            }
        }
    }
    
    if (phones.length === 0) {
        // Essayer d'extraire n'importe quel numéro valide de la chaîne brute
        let digits = raw.replace(/\D/g, '');
        if (digits.length >= 10) {
            // Prendre les 10-11 premiers chiffres
            let extracted = digits.substring(0, 11);
            return { phone: extracted, source: 'extrait' };
        }
        return { phone: '', source: 'aucun trouvé' };
    }
    
    // Chercher par priorité: mobile > work > home
    for (let priority of CONFIG.phonePriority) {
        for (let p of phones) {
            if (p.type.includes(priority)) {
                return { phone: p.number, source: p.type };
            }
        }
    }
    
    // Si aucune priorité trouvée, prendre le premier
    return { phone: phones[0].number, source: phones[0].type + ' (1er)' };
}

function formatPhoneNumber(phone) {
    if (!phone) return '';
    
    // Garder seulement les chiffres et le +
    let cleaned = phone.replace(/[^\d+]/g, '');
    
    // Si commence par +1, garder tel quel
    if (cleaned.startsWith('+1') && cleaned.length === 12) {
        return cleaned;
    }
    
    // Si commence par 1 et a 11 chiffres
    if (cleaned.startsWith('1') && cleaned.length === 11) {
        return '+' + cleaned;
    }
    
    // Si 10 chiffres, ajouter +1
    let digits = cleaned.replace(/\D/g, '');
    if (digits.length === 10) {
        return '+1' + digits;
    }
    
    // Si 11 chiffres commençant par 1
    if (digits.length === 11 && digits.startsWith('1')) {
        return '+' + digits;
    }
    
    return cleaned;
}

function validateContact(phone, firstName) {
    // Vérifier prénom
    if (!firstName || firstName.trim().length === 0) {
        return `Prénom manquant`;
    }
    
    // Vérifier téléphone
    let phoneDigits = phone.replace(/\D/g, '');
    
    if (!phoneDigits || phoneDigits.length < 10) {
        return `Téléphone invalide: "${phone}" (${phoneDigits.length} chiffres, min 10)`;
    }
    
    if (phoneDigits.length > 15) {
        return `Téléphone trop long: "${phone}" (${phoneDigits.length} chiffres)`;
    }
    
    return null;
}

// ============================================
// FONCTIONS UI
// ============================================
async function showDebugReport(validContacts, skippedContacts, messageTemplate, separator = 'virgule') {
    // Construire le tableau HTML des contacts valides
    let validRows = validContacts.map(c => `
        <tr>
            <td>${c.lineNumber}</td>
            <td>${c.firstName}</td>
            <td>${c.lastName}</td>
            <td class="phone">${c.phone}</td>
            <td class="source">${c.phoneSource}</td>
        </tr>
    `).join('');
    
    // Construire le tableau HTML des contacts ignorés
    let skipRows = skippedContacts.map(s => `
        <tr>
            <td>${s.lineNumber}</td>
            <td class="error">${s.reason}</td>
            <td class="raw">${s.rawData ? s.rawData.rawFirstName : '-'}</td>
            <td class="raw">${s.rawData ? s.rawData.rawPhone.substring(0, 30) : '-'}</td>
        </tr>
    `).join('');
    
    // Aperçu du message
    let preview = '';
    if (validContacts.length > 0) {
        preview = messageTemplate
            .replace(/\*\*PRENOM\*\*/g, `<span class="var">${validContacts[0].firstName}</span>`)
            .replace(/\*\*NOM\*\*/g, `<span class="var">${validContacts[0].lastName}</span>`);
    }
    
    let wv = new WebView();
    await wv.loadHTML(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { box-sizing: border-box; }
                body { font-family: -apple-system; font-size: 13px; padding: 15px; background: #1c1c1e; color: #fff; }
                h2 { font-size: 16px; margin: 15px 0 10px 0; }
                h2:first-child { margin-top: 0; }
                .info { background: #2c2c2e; padding: 10px 12px; border-radius: 8px; margin-bottom: 15px; font-size: 12px; color: #888; }
                .info strong { color: #fff; }
                .stats { display: flex; gap: 15px; margin-bottom: 15px; }
                .stat { padding: 12px 15px; border-radius: 10px; text-align: center; flex: 1; }
                .stat.valid { background: #1a3d1a; border: 1px solid #30d158; }
                .stat.skip { background: #3d1a1a; border: 1px solid #ff453a; }
                .stat .num { font-size: 24px; font-weight: bold; }
                .stat .label { font-size: 11px; color: #888; }
                table { width: 100%; border-collapse: collapse; font-size: 12px; }
                th, td { padding: 8px 6px; text-align: left; border-bottom: 1px solid #333; }
                th { background: #2c2c2e; color: #888; font-weight: 600; }
                .phone { font-family: monospace; color: #0a84ff; }
                .source { color: #30d158; font-size: 11px; }
                .error { color: #ff453a; }
                .raw { color: #888; font-size: 11px; max-width: 100px; overflow: hidden; text-overflow: ellipsis; }
                .preview { background: #2c2c2e; padding: 15px; border-radius: 10px; margin-top: 15px; white-space: pre-wrap; line-height: 1.5; }
                .var { background: #0a84ff33; color: #0a84ff; padding: 2px 4px; border-radius: 4px; }
                .footer { margin-top: 20px; padding: 15px; background: #2a2a2c; border-radius: 10px; text-align: center; color: #888; font-size: 12px; }
                .scroll { max-height: 200px; overflow-y: auto; border-radius: 8px; }
            </style>
        </head>
        <body>
            <div class="info">
                <strong>Séparateur détecté:</strong> ${separator}
            </div>
            
            <div class="stats">
                <div class="stat valid">
                    <div class="num">${validContacts.length}</div>
                    <div class="label">VALIDES</div>
                </div>
                <div class="stat skip">
                    <div class="num">${skippedContacts.length}</div>
                    <div class="label">IGNORÉS</div>
                </div>
            </div>
            
            <h2>Contacts valides</h2>
            <div class="scroll">
                <table>
                    <tr><th>#</th><th>Prénom</th><th>Nom</th><th>Téléphone</th><th>Source</th></tr>
                    ${validRows || '<tr><td colspan="5" style="color:#888">Aucun</td></tr>'}
                </table>
            </div>
            
            ${skippedContacts.length > 0 ? `
            <h2>Contacts ignorés</h2>
            <div class="scroll">
                <table>
                    <tr><th>#</th><th>Raison</th><th>Prénom brut</th><th>Tél brut</th></tr>
                    ${skipRows}
                </table>
            </div>
            ` : ''}
            
            ${preview ? `
            <h2>📝 Aperçu du message</h2>
            <div class="preview">${preview}</div>
            ` : ''}
            
            <div class="footer">
                🔍 MODE DEBUG - Aucun message envoyé<br>
                <small>Mettre DEBUG_MODE = false pour envoyer</small>
            </div>
        </body>
        </html>
    `);
    await wv.present();
}

async function showPreviewReport(validContacts, skippedContacts, messageTemplate, separator = 'virgule') {
    // Construire le tableau HTML des contacts valides
    let validRows = validContacts.map(c => `
        <tr>
            <td>${c.lineNumber}</td>
            <td>${c.firstName}</td>
            <td>${c.lastName}</td>
            <td class="phone">${c.phone}</td>
            <td class="source">${c.phoneSource}</td>
        </tr>
    `).join('');
    
    // Construire le tableau HTML des contacts ignorés
    let skipRows = skippedContacts.map(s => `
        <tr>
            <td>${s.lineNumber}</td>
            <td class="error">${s.reason}</td>
            <td class="raw">${s.rawData ? s.rawData.rawFirstName : '-'}</td>
            <td class="raw">${s.rawData ? s.rawData.rawPhone.substring(0, 30) : '-'}</td>
        </tr>
    `).join('');
    
    // Aperçu du message
    let preview = '';
    if (validContacts.length > 0) {
        preview = messageTemplate
            .replace(/\*\*PRENOM\*\*/g, `<span class="var">${validContacts[0].firstName}</span>`)
            .replace(/\*\*NOM\*\*/g, `<span class="var">${validContacts[0].lastName}</span>`);
    }
    
    let wv = new WebView();
    await wv.loadHTML(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { box-sizing: border-box; }
                body { font-family: -apple-system; font-size: 13px; padding: 15px; padding-bottom: 100px; background: #1c1c1e; color: #fff; }
                h2 { font-size: 16px; margin: 15px 0 10px 0; }
                h2:first-child { margin-top: 0; }
                .info { background: #2c2c2e; padding: 10px 12px; border-radius: 8px; margin-bottom: 15px; font-size: 12px; color: #888; }
                .info strong { color: #fff; }
                .stats { display: flex; gap: 15px; margin-bottom: 15px; }
                .stat { padding: 12px 15px; border-radius: 10px; text-align: center; flex: 1; }
                .stat.valid { background: #1a3d1a; border: 1px solid #30d158; }
                .stat.skip { background: #3d1a1a; border: 1px solid #ff453a; }
                .stat .num { font-size: 24px; font-weight: bold; }
                .stat .label { font-size: 11px; color: #888; }
                table { width: 100%; border-collapse: collapse; font-size: 12px; }
                th, td { padding: 8px 6px; text-align: left; border-bottom: 1px solid #333; }
                th { background: #2c2c2e; color: #888; font-weight: 600; }
                .phone { font-family: monospace; color: #0a84ff; }
                .source { color: #30d158; font-size: 11px; }
                .error { color: #ff453a; }
                .raw { color: #888; font-size: 11px; max-width: 100px; overflow: hidden; text-overflow: ellipsis; }
                .preview { background: #2c2c2e; padding: 15px; border-radius: 10px; margin-top: 15px; white-space: pre-wrap; line-height: 1.5; }
                .var { background: #0a84ff33; color: #0a84ff; padding: 2px 4px; border-radius: 4px; }
                .scroll { max-height: 200px; overflow-y: auto; border-radius: 8px; }
                .buttons { position: fixed; bottom: 0; left: 0; right: 0; padding: 15px; background: #1c1c1e; border-top: 1px solid #333; display: flex; gap: 10px; }
                .btn { flex: 1; padding: 14px; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; }
                .btn.go { background: #30d158; color: #fff; }
                .btn.cancel { background: #3a3a3c; color: #fff; }
            </style>
        </head>
        <body>
            <div class="info">
                📄 <strong>Séparateur détecté:</strong> ${separator}
            </div>
            
            <div class="stats">
                <div class="stat valid">
                    <div class="num">${validContacts.length}</div>
                    <div class="label">VALIDES</div>
                </div>
                <div class="stat skip">
                    <div class="num">${skippedContacts.length}</div>
                    <div class="label">IGNORÉS</div>
                </div>
            </div>
            
            <h2>✅ Contacts valides</h2>
            <div class="scroll">
                <table>
                    <tr><th>#</th><th>Prénom</th><th>Nom</th><th>Téléphone</th><th>Source</th></tr>
                    ${validRows || '<tr><td colspan="5" style="color:#888">Aucun</td></tr>'}
                </table>
            </div>
            
            ${skippedContacts.length > 0 ? `
            <h2>❌ Contacts ignorés</h2>
            <div class="scroll">
                <table>
                    <tr><th>#</th><th>Raison</th><th>Prénom brut</th><th>Tél brut</th></tr>
                    ${skipRows}
                </table>
            </div>
            ` : ''}
            
            ${preview ? `
            <h2>📝 Aperçu du message</h2>
            <div class="preview">${preview}</div>
            ` : ''}
            
            <div class="buttons">
                <button class="btn cancel" onclick="window.cancel = true; completion(false);">Annuler</button>
                <button class="btn go" onclick="completion(true);">🚀 GO! Envoyer ${validContacts.length}</button>
            </div>
            
            <script>
                function completion(value) {
                    window.result = value;
                }
            </script>
        </body>
        </html>
    `);
    
    await wv.present();
    
    // Récupérer le résultat
    let result = await wv.evaluateJavaScript('window.result');
    return result === true;
}

async function getMessageTemplate() {
    let wv = new WebView();
    
    await wv.loadHTML(`
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
        <style>
            * { box-sizing: border-box; }
            body { font-family: -apple-system; background: #1c1c1e; color: #fff; padding: 20px; margin: 0; }
            h2 { margin-top: 0; font-size: 20px; }
            .help { font-size: 13px; color: #888; margin-bottom: 20px; line-height: 1.5; }
            .variables { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
            .var { 
                background: #0a84ff; 
                color: #fff;
                padding: 8px 14px; 
                border-radius: 8px; 
                font-family: monospace; 
                font-size: 14px;
                cursor: pointer;
                transition: transform 0.1s, background 0.1s;
            }
            .var:active { transform: scale(0.95); background: #0070e0; }
            textarea { width: 100%; height: 180px; background: #2c2c2e; color: #fff; border: 1px solid #444; border-radius: 10px; padding: 15px; font-size: 16px; font-family: -apple-system; resize: none; }
            textarea:focus { outline: none; border-color: #0a84ff; }
            .done { margin-top: 15px; padding: 12px; background: #30d158; color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; width: 100%; }
            .footer { margin-top: 12px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <h2>Ton message</h2>
        <div class="help">
            👇 <b>Clique sur une variable</b> pour l'insérer dans ton message.<br>
            Elle sera remplacée par le vrai nom de chaque contact.
        </div>
        <div class="variables">
            <span class="var" onclick="insert('**PRENOM** ')">Prénom</span>
            <span class="var" onclick="insert('**NOM** ')">NOM</span>
        </div>
        <textarea id="msg" placeholder="Écris ton message ici...">Bonjour </textarea>
        <div class="footer">↓ Swipe vers le bas pour fermer quand tu as fini</div>
        <script>
            function insert(text) {
                let ta = document.getElementById('msg');
                let start = ta.selectionStart;
                let end = ta.selectionEnd;
                let before = ta.value.substring(0, start);
                let after = ta.value.substring(end);
                ta.value = before + text + after;
                ta.selectionStart = ta.selectionEnd = start + text.length;
                ta.focus();
            }
        </script>
    </body>
    </html>
    `);
    
    await wv.present();
    
    let message = await wv.evaluateJavaScript('document.getElementById("msg").value');
    
    if (!message || message.trim().length === 0) return null;
    return message;
}

async function showReport(sentCount, totalCount, skippedContacts) {
    let report = `✅ ENVOYÉS: ${sentCount}/${totalCount}\n`;
    
    if (skippedContacts.length > 0) {
        report += `\n❌ IGNORÉS: ${skippedContacts.length}\n\n`;
        for (let skip of skippedContacts) {
            report += `L${skip.lineNumber}: ${skip.reason}\n`;
            report += `  → "${skip.originalLine.substring(0, 40)}..."\n\n`;
        }
    }
    
    if (skippedContacts.length > 3) {
        let wv = new WebView();
        await wv.loadHTML(`
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: -apple-system; font-size: 14px; padding: 20px; background: #1c1c1e; color: #fff; }
                    pre { white-space: pre-wrap; word-wrap: break-word; }
                </style>
            </head>
            <body>
                <h2>📊 Rapport</h2>
                <pre>${report}</pre>
            </body>
            </html>
        `);
        await wv.present();
    } else {
        let alert = new Alert();
        alert.title = "✅ Terminé";
        alert.message = report;
        alert.addAction("OK");
        await alert.present();
    }
}

async function showError(message) {
    let alert = new Alert();
    alert.title = "❌ Erreur";
    alert.message = message;
    alert.addAction("OK");
    await alert.present();
}

// ============================================
// FONCTIONS D'ENVOI
// ============================================
async function sendMessagesFast(contacts, messageTemplate) {
    let sentCount = 0;
    
    for (let i = 0; i < contacts.length; i++) {
        let contact = contacts[i];
        
        let personalMessage = messageTemplate
            .replace(new RegExp(escapeRegExp(CONFIG.firstNameVar), 'g'), contact.firstName)
            .replace(new RegExp(escapeRegExp(CONFIG.lastNameVar), 'g'), contact.lastName);
        
        let msg = new Message();
        msg.recipients = [contact.phone];
        msg.body = personalMessage;
        
        try {
            await msg.send();
            sentCount++;
        } catch (error) {
            // L'utilisateur a annulé - demander s'il veut arrêter
            let stopAlert = new Alert();
            stopAlert.title = "Message annulé";
            stopAlert.message = `Tu as annulé le message pour ${contact.firstName}.\n\nVeux-tu arrêter l'envoi?\n\n✅ ${sentCount} envoyé(s)\n⏳ ${contacts.length - i - 1} restant(s)`;
            stopAlert.addAction("🛑 Arrêter tout");
            stopAlert.addAction("⏭️ Continuer (sauter ce contact)");
            stopAlert.addCancelAction("Annuler");
            
            let choice = await stopAlert.present();
            
            if (choice === 0 || choice === -1) {
                // Arrêter tout
                return { sentCount, stopped: true, stoppedAt: contact.firstName };
            }
            // choice === 1: continuer avec le prochain contact
        }
    }
    
    return { sentCount, stopped: false };
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

await main();

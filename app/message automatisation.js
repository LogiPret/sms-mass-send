// SMS Mass Send - Scriptable Script
// Version 1.0
// Pour iPhone - Envoi de SMS en masse depuis un CSV

// ============================================
// CONFIGURATION
// ============================================
const DEBUG_MODE = true;  // ← Mettre à false pour envoyer vraiment

const CONFIG = {
    // Noms de colonnes à détecter (insensible à la casse)
    phoneColumns: ['phone', 'telephone', 'tel', 'mobile', 'cell', 'cellulaire', 'numéro', 'numero'],
    firstNameColumns: ['prenom', 'prénom', 'firstname', 'first name', 'first', 'given name'],
    lastNameColumns: ['nom', 'lastname', 'last name', 'last', 'family name', 'surname'],
    
    // Variables dans le message
    firstNameVar: '**PRENOM**',
    lastNameVar: '**NOM**'
};

// ============================================
// MAIN
// ============================================
async function main() {
    try {
        // Étape 1: Sélection du fichier CSV (pas de welcome screen)
        let csvContent = await selectCSVFile();
        if (!csvContent) return;
        
        // Étape 2: Parser le CSV
        let { headers, rows, columnMap } = parseCSV(csvContent);
        
        if (rows.length === 0) {
            await showError("Le fichier CSV est vide ou ne contient que l'en-tête.");
            return;
        }
        
        // Vérifier colonnes essentielles (silencieux si OK)
        if (columnMap.phone === -1) {
            await showError("Colonne téléphone non trouvée. Utilise: phone, telephone, tel, mobile");
            return;
        }
        
        // Étape 3: Saisie du message
        let messageTemplate = await getMessageTemplate();
        if (!messageTemplate) return;
        
        // Étape 4: Préparer les contacts
        let { validContacts, skippedContacts } = prepareContacts(rows, headers, columnMap);
        
        if (validContacts.length === 0) {
            await showError("Aucun contact valide trouvé dans le CSV.");
            return;
        }
        
        // MODE DEBUG : Afficher le rapport sans envoyer
        if (DEBUG_MODE) {
            await showDebugReport(validContacts, skippedContacts, messageTemplate);
            return;
        }
        
        // Étape 5: Confirmation rapide avec aperçu
        let previewMessage = messageTemplate
            .replace(new RegExp(escapeRegExp(CONFIG.firstNameVar), 'g'), validContacts[0].firstName)
            .replace(new RegExp(escapeRegExp(CONFIG.lastNameVar), 'g'), validContacts[0].lastName);
        
        let confirmAlert = new Alert();
        confirmAlert.title = `📨 ${validContacts.length} messages`;
        confirmAlert.message = `Aperçu:\n"${previewMessage.substring(0, 100)}${previewMessage.length > 100 ? '...' : ''}"`;
        confirmAlert.addAction("GO!");
        confirmAlert.addCancelAction("Annuler");
        if (await confirmAlert.present() === -1) return;
        
        // Étape 6: Envoyer les messages (mode rapide)
        let sentCount = await sendMessagesFast(validContacts, messageTemplate);
        
        // Étape 7: Rapport final (seulement si erreurs)
        if (skippedContacts.length > 0) {
            await showReport(sentCount, validContacts.length, skippedContacts);
        } else {
            // Notification simple
            let n = new Notification();
            n.title = "✅ Terminé";
            n.body = `${sentCount} messages traités`;
            n.schedule();
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
function parseCSV(content) {
    let lines = content.split(/\r?\n/).filter(line => line.trim().length > 0);
    
    if (lines.length === 0) {
        return { headers: [], rows: [], columnMap: {} };
    }
    
    // Parser l'en-tête
    let headers = parseCSVLine(lines[0]);
    
    // Parser les lignes de données
    let rows = [];
    for (let i = 1; i < lines.length; i++) {
        let values = parseCSVLine(lines[i]);
        rows.push({
            lineNumber: i + 1,
            originalLine: lines[i],
            values: values
        });
    }
    
    // Détecter les colonnes
    let columnMap = detectColumns(headers);
    
    return { headers, rows, columnMap };
}

function parseCSVLine(line) {
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
        } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    result.push(current.trim());
    return result;
}

function detectColumns(headers) {
    let columnMap = {
        phone: -1,
        firstName: -1,
        lastName: -1
    };
    
    for (let i = 0; i < headers.length; i++) {
        let header = headers[i].toLowerCase().trim();
        
        // Détecter téléphone
        if (columnMap.phone === -1) {
            for (let name of CONFIG.phoneColumns) {
                if (header.includes(name)) {
                    columnMap.phone = i;
                    break;
                }
            }
        }
        
        // Détecter prénom
        if (columnMap.firstName === -1) {
            for (let name of CONFIG.firstNameColumns) {
                if (header.includes(name)) {
                    columnMap.firstName = i;
                    break;
                }
            }
        }
        
        // Détecter nom
        if (columnMap.lastName === -1) {
            for (let name of CONFIG.lastNameColumns) {
                if (header.includes(name)) {
                    columnMap.lastName = i;
                    break;
                }
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
    
    for (let row of rows) {
        let phone = columnMap.phone >= 0 ? row.values[columnMap.phone] || '' : '';
        let firstName = columnMap.firstName >= 0 ? row.values[columnMap.firstName] || '' : '';
        let lastName = columnMap.lastName >= 0 ? row.values[columnMap.lastName] || '' : '';
        
        // Nettoyer le prénom et nom
        firstName = cleanName(firstName);
        lastName = cleanName(lastName);
        
        // Si prénom vide, utiliser "Client" (comme le script Mac)
        if (!firstName || firstName.length === 0) {
            firstName = "Client";
        }
        
        // Formater le numéro
        let formattedPhone = formatPhoneNumber(phone);
        
        // Valider
        let skipReason = validateContact(formattedPhone, firstName);
        
        if (skipReason) {
            skippedContacts.push({
                lineNumber: row.lineNumber,
                originalLine: row.originalLine,
                reason: skipReason
            });
        } else {
            validContacts.push({
                phone: formattedPhone,
                firstName: firstName,
                lastName: lastName,
                lineNumber: row.lineNumber
            });
        }
    }
    
    return { validContacts, skippedContacts };
}

function cleanName(name) {
    if (!name) return '';
    
    // Supprimer les guillemets orphelins
    name = name.replace(/"/g, '');
    
    // Supprimer les caractères spéciaux au début et fin (garder les tirets et apostrophes au milieu)
    name = name.replace(/^[^a-zA-ZÀ-ÿ]+|[^a-zA-ZÀ-ÿ]+$/g, '');
    
    // Si contient une virgule, prendre seulement la première partie
    if (name.includes(',')) {
        name = name.split(',')[0].trim();
    }
    
    // Capitaliser chaque partie d'un nom composé (Jean-Pierre, O'Brien)
    name = name.replace(/\b\w/g, c => c.toUpperCase());
    name = name.replace(/([-'])\w/g, match => match.toLowerCase());
    name = name.replace(/^\w/, c => c.toUpperCase());
    
    // Gérer les noms avec tiret (Anne-Marie → Anne-Marie)
    name = name.split('-').map(part => {
        if (part.length > 0) {
            return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
        }
        return part;
    }).join('-');
    
    // Gérer O'Brien, etc.
    name = name.replace(/'(\w)/g, (match, letter) => "'" + letter.toUpperCase());
    
    return name.trim();
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
    // Vérifier le téléphone (moins strict - comme le script Mac)
    let phoneDigits = phone.replace(/\D/g, '');
    
    if (!phoneDigits || phoneDigits.length < 10) {
        return `Téléphone invalide: "${phone}" (${phoneDigits.length} chiffres, min 10)`;
    }
    
    if (phoneDigits.length > 15) {
        return `Téléphone trop long: "${phone}" (${phoneDigits.length} chiffres)`;
    }
    
    // Prénom optionnel - utiliser "Client" si vide (comme le script Mac)
    // On ne refuse plus si prénom manquant!
    
    return null; // Valide
}

// ============================================
// FONCTIONS UI
// ============================================
async function showDebugReport(validContacts, skippedContacts, messageTemplate) {
    // Construire le rapport détaillé
    let report = `🔍 MODE DEBUG - Aucun message envoyé\n\n`;
    report += `✅ VALIDES: ${validContacts.length}\n`;
    report += `❌ IGNORÉS: ${skippedContacts.length}\n\n`;
    
    report += `--- CONTACTS VALIDES ---\n`;
    for (let c of validContacts.slice(0, 10)) {
        report += `L${c.lineNumber}: ${c.firstName} ${c.lastName} → ${c.phone}\n`;
    }
    if (validContacts.length > 10) {
        report += `... +${validContacts.length - 10} autres\n`;
    }
    
    report += `\n--- CONTACTS IGNORÉS ---\n`;
    for (let s of skippedContacts) {
        report += `L${s.lineNumber}: ${s.reason}\n  → "${s.originalLine.substring(0, 50)}..."\n`;
    }
    
    // Aperçu du premier message
    if (validContacts.length > 0) {
        let preview = messageTemplate
            .replace(/\*\*PRENOM\*\*/g, validContacts[0].firstName)
            .replace(/\*\*NOM\*\*/g, validContacts[0].lastName);
        report += `\n--- APERÇU MESSAGE ---\n"${preview}"`;
    }
    
    // Afficher dans une webview pour scroll
    let wv = new WebView();
    await wv.loadHTML(`
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: -apple-system; font-size: 14px; padding: 20px; background: #1c1c1e; color: #fff; }
                pre { white-space: pre-wrap; word-wrap: break-word; }
                .valid { color: #30d158; }
                .skip { color: #ff453a; }
            </style>
        </head>
        <body>
            <pre>${report}</pre>
            <br><br>
            <p style="color:#888">⬆️ Mettre DEBUG_MODE = false pour envoyer</p>
        </body>
        </html>
    `);
    await wv.present();
}

async function getMessageTemplate() {
    let alert = new Alert();
    alert.title = "✏️ Message";
    alert.message = `Variables: ${CONFIG.firstNameVar} et ${CONFIG.lastNameVar}`;
    
    alert.addTextField("Message", "Bonjour **PRENOM**,\n\n");
    alert.addAction("OK");
    alert.addCancelAction("Annuler");
    
    if (await alert.present() === -1) return null;
    
    let message = alert.textFieldValue(0);
    if (!message || message.trim().length === 0) return null;
    
    return message;
}

async function showReport(sentCount, totalCount, skippedContacts) {
    let alert = new Alert();
    alert.title = "✅ Terminé";
    
    let message = `${sentCount} traités`;
    
    if (skippedContacts.length > 0) {
        message += `\n\n⚠️ ${skippedContacts.length} ignorés:`;
        for (let skip of skippedContacts.slice(0, 3)) {
            message += `\nL${skip.lineNumber}: ${skip.reason}`;
        }
        if (skippedContacts.length > 3) {
            message += `\n+${skippedContacts.length - 3} autres`;
        }
    }
    
    alert.message = message;
    alert.addAction("OK");
    await alert.present();
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
        
        // Préparer le message personnalisé
        let personalMessage = messageTemplate
            .replace(new RegExp(escapeRegExp(CONFIG.firstNameVar), 'g'), contact.firstName)
            .replace(new RegExp(escapeRegExp(CONFIG.lastNameVar), 'g'), contact.lastName);
        
        // Créer le message avec l'API native Scriptable
        let msg = new Message();
        msg.recipients = [contact.phone];
        msg.body = personalMessage;
        
        try {
            // send() retourne une Promise - attend que l'utilisateur clique Envoyer
            await msg.send();
            sentCount++;
        } catch (error) {
            // L'utilisateur a annulé ce message, continuer avec le suivant
            console.log(`Message annulé pour ${contact.firstName}: ${error}`);
        }
    }
    
    return sentCount;
}

// ============================================
// UTILITAIRES
// ============================================
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ============================================
// EXÉCUTION
// ============================================
await main();

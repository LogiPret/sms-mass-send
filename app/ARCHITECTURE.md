# Architecture Technique

## Vue d'ensemble

L'application utilise **Scriptable**, une app iOS qui permet d'exécuter du JavaScript avec accès aux APIs natives d'iOS.

```
┌─────────────────────────────────────────────────────────────┐
│                        SCRIPTABLE APP                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   File API   │    │  Messages    │    │    Alert     │  │
│  │  (CSV Read)  │    │   Compose    │    │   (UI/UX)    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    script.js                          │   │
│  │  • parseCSV()      - Parser CSV robuste              │   │
│  │  • formatPhone()   - Normalisation téléphone         │   │
│  │  • cleanName()     - Nettoyage caractères spéciaux   │   │
│  │  • sendMessage()   - Ouverture Messages avec URL     │   │
│  │  • main()          - Orchestration du flow           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## APIs Scriptable utilisées

### 1. DocumentPicker
```javascript
let files = await DocumentPicker.openFile();
```
Permet à l'utilisateur de sélectionner un fichier CSV depuis l'app Fichiers.

### 2. FileManager
```javascript
let fm = FileManager.local();
let content = fm.readString(filePath);
```
Lit le contenu du fichier CSV sélectionné.

### 3. Alert
```javascript
let alert = new Alert();
alert.title = "Titre";
alert.message = "Message";
alert.addTextField("placeholder", "default");
await alert.present();
```
Affiche des dialogues pour :
- Saisie du message template
- Confirmation avant envoi
- Rapport de fin

### 4. Safari / URL Scheme
```javascript
Safari.open(`sms:${phoneNumber}&body=${encodedMessage}`);
```
Ouvre l'app Messages avec le numéro et le message pré-remplis.

**Note importante** : On utilise le scheme `sms:` qui :
- Ouvre Messages avec tout pré-rempli
- Requiert que l'utilisateur clique "Envoyer" (limitation Apple)
- Fonctionne pour iMessage ET SMS

## Modules du script

### Module 1 : CSV Parser

```javascript
function parseCSV(csvText) {
    // Gère :
    // - Virgules dans les guillemets
    // - Guillemets échappés ""
    // - Retours à la ligne dans les champs
    // - Encodage UTF-8
}
```

### Module 2 : Phone Formatter

```javascript
function formatPhoneNumber(rawPhone) {
    // Transforme :
    // "(438) 555-1234" → "+14385551234"
    // "438.555.1234"   → "+14385551234"
    // "15145551234"    → "+15145551234"
}
```

### Module 3 : Name Cleaner

```javascript
function cleanName(name) {
    // Supprime les caractères problématiques :
    // Virgules, guillemets, parenthèses, etc.
}
```

### Module 4 : Column Detector

```javascript
function findColumn(headers, possibleNames) {
    // Détecte automatiquement les colonnes :
    // "First Name", "firstname", "prénom" → colonne prénom
    // "Phone", "mobile", "téléphone" → colonne téléphone
}
```

### Module 5 : Message Sender

```javascript
async function sendMessage(phone, message) {
    // Encode le message pour URL
    // Ouvre sms:// avec le numéro et le body
    // Attend que l'utilisateur revienne
}
```

## Gestion des erreurs

| Erreur | Cause | Solution |
|--------|-------|----------|
| Fichier non trouvé | CSV non sélectionné | Redemander le fichier |
| Colonnes manquantes | Headers non reconnus | Afficher les colonnes trouvées |
| Téléphone invalide | Format non reconnu | Ignorer la ligne, logger |
| Prénom vide | Champ vide dans CSV | Ignorer la ligne, logger |

## Persistance

Scriptable permet de sauvegarder des données :
```javascript
Keychain.set("lastMessage", messageTemplate);
let saved = Keychain.get("lastMessage");
```

Utilisé pour :
- Sauvegarder le dernier message utilisé
- Rappeler les préférences utilisateur

## Sécurité

- ✅ Aucune donnée envoyée à un serveur externe
- ✅ Tout reste local sur l'iPhone
- ✅ Le CSV n'est jamais uploadé nulle part
- ✅ Conforme aux restrictions Apple sur les messages

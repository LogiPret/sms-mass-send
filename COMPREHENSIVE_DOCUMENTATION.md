# SMS Campaign - Comprehensive Technical Documentation

> **Purpose:** This document provides a complete technical overview of the SMS Campaign application ecosystem, including the Mac app, mobile web app, iOS Scriptable version, and their architectures, to facilitate technical discussions about future features and possibilities.

**Last Updated:** January 5, 2026  
**Current Versions:**
- Mac App: 2.4.17
- iOS Scriptable: 1.1.38
- Mobile Web App: 1.0

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Platform Implementations](#platform-implementations)
4. [Core Features & Functionality](#core-features--functionality)
5. [Authorization System](#authorization-system)
6. [CSV Processing Engine](#csv-processing-engine)
7. [Phone Number Handling](#phone-number-handling)
8. [French Name Processing](#french-name-processing)
9. [Message Composition & Variables](#message-composition--variables)
10. [Auto-Update System](#auto-update-system)
11. [Build & Distribution](#build--distribution)
12. [Technical Constraints & Limitations](#technical-constraints--limitations)
13. [Future Possibilities](#future-possibilities)

---

## Project Overview

### What is SMS Campaign?

SMS Campaign is a mass SMS sending application for **Canadian/North American markets** (primarily Quebec) that allows users to:
- Import contacts from CSV files
- Send personalized SMS messages via Apple's Messages app (iMessage/SMS)
- Handle French names with proper accent support
- Prioritize multiple phone numbers per contact

### Key Use Cases

1. **Real estate agents** sending appointment reminders to clients
2. **Small businesses** sending promotional messages
3. **Organizations** sending event notifications
4. **Any user** needing to send personalized bulk SMS without paying for SMS API services

### Why This Approach?

Instead of using paid SMS APIs (Twilio, etc.), the app leverages:
- **Apple Messages app** - Free SMS/iMessage on user's iPhone/Mac
- **Native integration** - Uses URL schemes to pre-fill messages
- **Manual sending** - User clicks "Send" for each message (Apple limitation)

### Multi-Platform Strategy

The app exists in **three implementations**:

| Platform | Technology | Distribution | Code Protection | Use Case |
|----------|-----------|--------------|-----------------|----------|
| **Mac App** | Python + PyInstaller + webview | Standalone .app | Bytecode compiled | Desktop power users |
| **Mobile Web** | HTML/CSS/JS (PWA-ready) | Web hosted | Server-side | Quick access, shareable |
| **iOS Scriptable** | JavaScript (Scriptable app) | Gist auto-update | Code visible | iOS-only users |

---

## Architecture & Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     SMS CAMPAIGN ECOSYSTEM                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Mac App    │    │  Mobile Web  │    │   iOS App    │ │
│  │   (Python)   │    │  (HTML/JS)   │    │ (Scriptable) │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘ │
│         │                   │                    │          │
│         └───────────────────┴────────────────────┘          │
│                             │                               │
│                    ┌────────▼────────┐                      │
│                    │  Shared Backend │                      │
│                    │   (n8n Webhook) │                      │
│                    │   + Supabase    │                      │
│                    └────────┬────────┘                      │
│                             │                               │
│                  ┌──────────┴──────────┐                    │
│                  │                     │                    │
│           ┌──────▼──────┐      ┌──────▼──────┐            │
│           │ Auth Codes  │      │  Updates    │            │
│           │  (Device    │      │  (GitHub    │            │
│           │   Binding)  │      │   Gist)     │            │
│           └─────────────┘      └─────────────┘            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Apple Messages │
                    │  (sms:// URL)   │
                    └─────────────────┘
```

### Core Design Principles

1. **Privacy-First**: All data processing is local, no CSV data sent to servers
2. **Apple Native**: Leverages native Messages app for sending
3. **Auto-Update**: All versions check for updates from Gist/GitHub
4. **License Protection**: One activation code per device (bound to device ID)
5. **Offline-Capable**: Works without internet (after activation)

---

## Platform Implementations

### 1. Mac App (Primary Desktop Version)

**Technology Stack:**
- **Language:** Python 3.8+
- **UI:** HTML/CSS/JavaScript rendered in `pywebview` (native webkit)
- **Packaging:** PyInstaller (creates standalone .app bundle)
- **Automation:** AppleScript (controls Messages.app)

**File Structure:**
```
mac_app/
├── sms_campaign.py          # Main application (2514 lines)
├── SMS Campaign.spec        # PyInstaller build config
├── build.sh                 # Automated build script
├── version.json             # Version info (uploaded to Gist)
├── INSTALLATION_GUIDE.md    # User installation instructions
└── build/                   # Build artifacts
```

**Key Components:**

1. **Webview UI** (lines 170-1200): Dark-themed, multi-screen wizard
   - Screen 1: Activation (if not activated)
   - Screen 2: CSV file selection
   - Screen 3: Message composition with variables
   - Screen 4: Contact validation dashboard
   - Screen 5: Sending progress with logs
   - Screen 6: Completion stats

2. **CSV Parser** (lines 1400-1700): Robust CSV parsing
   - Auto-detects separator (comma, semicolon, tab)
   - Handles quoted fields, escaped quotes
   - UTF-8 encoding with French accent fixes
   - Column auto-detection (fuzzy matching)

3. **AppleScript Integration** (lines 1800-2000):
   ```python
   def send_sms_applescript(phone, message):
       script = f'''
       tell application "Messages"
           set targetService to 1st account whose service type = iMessage
           set targetBuddy to participant "{phone}" of targetService
           send "{message}" to targetBuddy
       end tell
       '''
       subprocess.run(['osascript', '-e', script])
   ```

4. **Authorization System** (lines 300-500):
   - Stores device_id in macOS Keychain
   - Validates activation code via n8n webhook
   - Binds code to device (one code = one device)

5. **Auto-Update System** (lines 250-300):
   - Checks Gist for new version on launch
   - Downloads updated `sms_campaign.py`
   - Saves to `~/.sms_campaign/` and restarts

**Build Process:**
```bash
cd mac_app
./build.sh
# Output: SMS Campaign.app (unsigned, ~50MB)
```

**Distribution:**
```bash
zip -r 'SMS Campaign.zip' 'SMS Campaign.app'
# Users: Right-click → Open (first time only)
# OR: xattr -cr 'SMS Campaign.app'
```

---

### 2. Mobile Web App (PWA)

**Technology Stack:**
- **Pure HTML/CSS/JavaScript** (no frameworks)
- **Responsive Design** (mobile-first)
- **PWA-Ready** (can be added to home screen)

**File Structure:**
```
mobile_web_app/
├── index.html               # Single-page app (613 lines)
└── README.md                # Deployment instructions
```

**Key Features:**

1. **File API**: Browser's native file picker
2. **Local Processing**: All CSV parsing in browser (JavaScript)
3. **sms:// URL Scheme**: Opens Messages with pre-filled message
4. **localStorage**: Saves message templates (optional)

**Flow:**
```
User selects CSV → Parse in browser → Compose message
→ For each contact: Click "Send" → Opens Messages → User sends → Back to app
```

**Deployment Options:**
- GitHub Pages (free)
- Vercel/Netlify (free)
- Cloudflare Pages (free)
- Local server: `python3 -m http.server 8080`

**Limitations vs Mac App:**
- No AppleScript (can't auto-send)
- Requires internet to load (unless Service Worker added)
- Code visible to users (unless hosted with auth)

**Advantages:**
- No installation required
- Works on any device with browser
- Easy to update (change on server)
- Can add authentication easily

---

### 3. iOS Scriptable Version

**Technology Stack:**
- **Scriptable App** (free iOS app for running JavaScript)
- **JavaScript** with Scriptable APIs
- **Auto-Update** via Gist

**File Structure:**
```
app/
├── sms_automatisation.js    # Main script (1581 lines)
├── version.json             # Version tracking
├── ARCHITECTURE.md          # API documentation
├── FLOW.md                  # User flow diagrams
└── examples/                # Sample CSV files
```

**Scriptable APIs Used:**

1. **DocumentPicker**: File selection
   ```javascript
   let files = await DocumentPicker.openFile();
   let content = files.readString();
   ```

2. **Alert**: UI dialogs
   ```javascript
   let alert = new Alert();
   alert.title = "Title";
   alert.addTextField("placeholder", "default");
   let value = await alert.present();
   ```

3. **Safari**: Open Messages
   ```javascript
   Safari.open(`sms:${phone}&body=${encodedMessage}`);
   ```

4. **Keychain**: Secure storage
   ```javascript
   Keychain.set("auth_code", code);
   let code = Keychain.get("auth_code");
   ```

**Update Mechanism:**
```javascript
// Check Gist for new version
let versionInfo = await (new Request(VERSION_URL)).loadJSON();
if (isNewerVersion(versionInfo.version, SCRIPT_VERSION)) {
    // Download new script
    let newScript = await (new Request(UPDATE_URL)).loadString();
    // Overwrite current script in Scriptable's storage
    fm.writeString(scriptPath, newScript);
    // Prompt user to restart
}
```

**Advantages:**
- Native iOS app experience
- Access to iOS APIs (contacts, calendar, etc.)
- Free distribution via Gist
- Secure storage (Keychain)

**Limitations:**
- Code is visible (users can read/modify)
- Requires Scriptable app installation
- More manual update process vs Mac app

---

## Core Features & Functionality

### CSV Column Auto-Detection

**How it works:**

1. **Exact Match First**: Check if header exactly matches known patterns
2. **Partial Match**: Check if header contains pattern
3. **Negative Filters**: Exclude false positives
4. **Priority Order**: Mobile > Work > Home for phone numbers

**Configuration (from `mac_app/sms_campaign.py`):**

```python
CONFIG = {
    # Phone columns
    "phone_columns_exact": [
        "phone", "phones", "telephone", "tel", "mobile", 
        "cell", "numero", "phone_number", "cellulaire"
    ],
    "phone_columns_partial": [
        "phone", "telephone", "mobile", "cell", "numero"
    ],
    
    # First name columns
    "firstname_columns_exact": [
        "first_name", "firstname", "first", "prenom", 
        "prénom", "given_name"
    ],
    "firstname_columns_partial": [
        "first_name", "firstname", "prenom", "prénom"
    ],
    
    # Last name columns
    "lastname_columns_exact": [
        "last_name", "lastname", "last", "nom", 
        "nom_famille", "family_name", "surname"
    ],
    "lastname_columns_partial": [
        "last_name", "lastname", "nom_de_famille", "famille"
    ],
    "lastname_columns_negative": [
        "prenom", "first"  # Don't match if these present
    ],
    
    # Full name column (when first/last not separate)
    "name_columns_exact": [
        "name", "client", "customer", "contact", "fullname"
    ],
    "name_columns_negative": [
        "first", "last", "prenom", "_id", "id_", 
        "number", "phone", "file"  # Avoid client_id, filename, etc.
    ],
    
    # Phone separators (for multiple phones in one field)
    "phone_separators": ["|", ";", ",", "/", " "],
}
```

**Example CSV Handling:**

| CSV Header | Detected As | Reason |
|------------|-------------|--------|
| `phone` | Phone (primary) | Exact match |
| `Mobile_Number` | Phone (primary) | Contains "mobile" |
| `Work_Phone` | Phone (secondary) | Contains "work" |
| `client_id` | (ignored) | Negative filter (contains "_id") |
| `prénom` | First Name | Exact match with accent |
| `First Name` | First Name | Exact match |
| `Full Name` | Name (split) | Exact match, will split into first/last |
| `Nom de famille` | Last Name | Contains "nom" + "famille" |

---

## Phone Number Handling

### Multi-Phone Priority System

**Problem:** CRM exports often have multiple phone columns (mobile, work, home).

**Solution:** Priority-based selection

```python
PRIORITY = ['mobile', 'cell', 'work', 'home']

# For contact with:
# - mobile: 438-555-1234
# - work: 514-555-9999
# - home: (empty)

# → Selects: 438-555-1234 (mobile has highest priority)
```

### Multiple Phones in One Field

**Problem:** Some CRMs export multiple phones separated by special characters.

**Example:**
```
Phone column: "438-555-1234 | 514-555-9999 | 450-555-7777"
```

**Detection:**
```python
PHONE_SEPARATORS = ["|", ";", ",", "/", " "]

def detect_multi_phone(phone_str):
    for sep in PHONE_SEPARATORS:
        if sep in phone_str:
            phones = phone_str.split(sep)
            return [p.strip() for p in phones if p.strip()]
    return [phone_str]
```

**Result:**
```python
Input:  "438-555-1234 | 514-555-9999"
Output: ["438-555-1234", "514-555-9999"]
# → Creates 2 separate messages
```

### Phone Number Formatting

**Normalization Process:**

```python
def format_phone_number(raw_phone):
    """
    Converts any format to E.164: +1XXXXXXXXXX
    
    Examples:
    - "(438) 555-1234"    → "+14385551234"
    - "438.555.1234"      → "+14385551234"
    - "1-514-555-9999"    → "+15145559999"
    - "+1 450 555 7777"   → "+14505557777"
    """
    # 1. Remove all non-digits
    digits = re.sub(r'[^0-9]', '', raw_phone)
    
    # 2. Add country code if missing
    if len(digits) == 10:
        digits = "1" + digits  # Add +1 for Canada/US
    
    # 3. Validate length
    if len(digits) != 11:
        return None  # Invalid
    
    # 4. Add + prefix
    return "+" + digits
```

### Validation Rules

| Rule | Example | Valid? | Reason |
|------|---------|--------|--------|
| Exactly 10 digits | `4385551234` | ✅ | Canadian format |
| 11 digits (with 1) | `14385551234` | ✅ | North American |
| Less than 10 | `438555` | ❌ | Too short |
| More than 11 | `123456789012` | ❌ | Too long |
| Contains letters | `438-CALL-NOW` | ❌ | Not numeric |
| Empty/whitespace | ` ` | ❌ | No number |

---

## French Name Processing

### The Quebec Name Challenge

**Problem:** Quebec has compound first names that are treated as ONE name:
- Marie Eve → First name is "Marie Eve" (NOT Marie)
- Jean-Pierre → First name is "Jean-Pierre"
- Marc Andre → First name is "Marc Andre"

**Traditional parsers split incorrectly:**
```
"Marie Eve Bourgouin" 
  Wrong: First="Marie", Last="Eve Bourgouin" ❌
  Right: First="Marie Eve", Last="Bourgouin" ✅
```

### Compound First Name Detection

**Known Prefixes (from `sms_campaign.py`, lines 60-75):**

```python
COMPOUND_FIRSTNAME_PREFIXES = {
    # Common prefixes
    "marie", "jean", "marc", "anne", "pierre", "louis", "paul", "charles",
    
    # Common compound names
    "marie eve", "marie-eve", 
    "marie claire", "marie-claire",
    "marie claude", "marie-claude",
    "marie pierre", "marie-pierre",
    "marie france", "marie-france",
    "marie josee", "marie-josée",
    "marie helene", "marie-hélène",
    
    "jean pierre", "jean-pierre",
    "jean francois", "jean-françois",
    "jean philippe", "jean-philippe",
    "jean michel", "jean-michel",
    
    "marc andre", "marc-andré",
    "marc olivier", "marc-olivier",
    
    "anne marie", "anne-marie",
    "anne sophie", "anne-sophie",
    
    # ... and more
}
```

### Parsing Algorithm

```python
def parse_full_name(full_name):
    """
    Examples:
    - "Marie Eve Bourgouin" → ("Marie Eve", "Bourgouin")
    - "Jean-Pierre Tremblay" → ("Jean-Pierre", "Tremblay")
    - "Marc Andre Juteau" → ("Marc Andre", "Juteau")
    - "Caroline Gauthier" → ("Caroline", "Gauthier")
    - "Veronique Racine Brule" → ("Veronique", "Racine Brule")
    """
    parts = full_name.split()
    
    if len(parts) == 2:
        return parts[0], parts[1]  # Simple case
    
    # Check if first word is hyphenated (e.g., "Jean-Pierre")
    if "-" in parts[0]:
        return parts[0], " ".join(parts[1:])
    
    # Check if first two words form a compound name
    first_two = f"{parts[0]} {parts[1]}".lower()
    if first_two in COMPOUND_FIRSTNAME_PREFIXES:
        return f"{parts[0]} {parts[1]}", " ".join(parts[2:])
    
    # Default: first word is firstname
    return parts[0], " ".join(parts[1:])
```

### Accent Handling

**Problem:** CSV exports often have encoding issues with French accents.

**Common Issues:**
```
Expected: "Hélène"
Got:      "HÃ©lÃ¨ne"   (double-encoded UTF-8)
```

**Fix Map (from `sms_campaign.py`, lines 155-165):**

```python
KNOWN_REPLACEMENTS = {
    "\\xc3\\xa9": "é",   # é
    "\\xc3\\xa8": "è",   # è
    "\\xc3\\xa0": "à",   # à
    "\\xc3\\xa2": "â",   # â
    "\\xc3\\xae": "î",   # î
    "\\xc3\\xb4": "ô",   # ô
    "\\xc3\\xbb": "û",   # û
    "\\xc3\\xa7": "ç",   # ç
    "\\xc5\\x93": "œ",   # œ
    # ... uppercase versions
}

def fix_french_encoding(text):
    for broken, correct in KNOWN_REPLACEMENTS.items():
        text = text.replace(broken, correct)
    return text
```

---

## Message Composition & Variables

### Variable System

**Available Variables:**

| Variable | Replaced With | Example |
|----------|---------------|---------|
| `**PRENOM**` | First name | `**PRENOM**` → `Jean` |
| `**NOM**` | Last name | `**NOM**` → `Tremblay` |
| `{{prenom}}` | (Alternate syntax) | `{{prenom}}` → `Jean` |
| `{{nom}}` | (Alternate syntax) | `{{nom}}` → `Tremblay` |

**Message Template Example:**

```
Bonjour **PRENOM**,

Votre rendez-vous avec **NOM** est confirmé pour demain à 14h.

Merci!
```

**Result for contact: Jean Tremblay**

```
Bonjour Jean,

Votre rendez-vous avec Tremblay est confirmé pour demain à 14h.

Merci!
```

### Variable Replacement Logic

```python
def replace_variables(template, firstname, lastname):
    """
    Replaces variables in message template.
    Case-insensitive, supports multiple syntaxes.
    """
    message = template
    
    # Replace **PRENOM** (case-insensitive)
    message = re.sub(
        r'\*\*PRENOM\*\*', 
        firstname, 
        message, 
        flags=re.IGNORECASE
    )
    
    # Replace **NOM**
    message = re.sub(
        r'\*\*NOM\*\*', 
        lastname, 
        message, 
        flags=re.IGNORECASE
    )
    
    # Also support {{prenom}} syntax (for web version)
    message = message.replace('{{prenom}}', firstname)
    message = message.replace('{{nom}}', lastname)
    
    return message
```

### Live Preview

All versions show a **live preview** of the first contact's message:

**Mac App:**
- Updates in real-time as user types
- Shows exactly what will be sent

**Mobile Web:**
- JavaScript-based preview
- Updates on keyup event

**iOS Scriptable:**
- Shows preview in Alert dialog
- Before sending loop starts

---

## Authorization System

### Device-Based Licensing

**Architecture:**

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Mac/iOS    │ ───▶ │  n8n Webhook │ ───▶ │  Supabase    │
│   App        │      │  (Validator) │      │  (Database)  │
│              │ ◀─── │              │ ◀─── │              │
└──────────────┘      └──────────────┘      └──────────────┘
     device_id           validation          sms_authorisation
     auth_code           logic               _codes table
```

### Database Schema (Supabase)

**Table: `sms_authorisation_codes`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `code` | TEXT | Activation code (unique) |
| `device_id` | TEXT | Device UUID (null until activated) |
| `activated_at` | TIMESTAMP | When code was used |
| `created_at` | TIMESTAMP | When code was created |
| `status` | TEXT | `active`, `used`, `revoked` |

### Activation Flow

**1. First Launch (Not Activated):**

```python
# Check Keychain for existing auth
if not keychain_has("sms_auth_code"):
    # Show activation screen
    code = prompt_user_for_code()
    device_id = get_or_create_device_id()
    
    # Validate with backend
    response = validate_code(code, device_id)
    
    if response.success:
        # Save to Keychain (permanent)
        keychain_set("sms_auth_code", code)
        keychain_set("sms_device_id", device_id)
    else:
        show_error(response.error)
```

**2. Webhook Validation (n8n):**

```javascript
// Webhook receives: { code, device_id }

// 1. Check if code exists
const codeRecord = await supabase
    .from('sms_authorisation_codes')
    .select('*')
    .eq('code', code)
    .single();

if (!codeRecord) {
    return { success: false, error: "Invalid code" };
}

// 2. Check if already used
if (codeRecord.device_id && codeRecord.device_id !== device_id) {
    return { 
        success: false, 
        error: "Code already used on another device" 
    };
}

// 3. Activate code
await supabase
    .from('sms_authorisation_codes')
    .update({ 
        device_id: device_id, 
        activated_at: new Date(),
        status: 'used'
    })
    .eq('code', code);

return { success: true };
```

**3. Subsequent Launches:**

```python
# Load from Keychain
auth_code = keychain_get("sms_auth_code")
device_id = keychain_get("sms_device_id")

# Verify still valid
response = validate_code(auth_code, device_id)

if response.success:
    # Proceed to main app
    show_main_ui()
else:
    # Code was revoked or device changed
    show_activation_screen()
```

### Device ID Generation

**Mac (Python):**
```python
def get_or_create_device_id():
    # Try to load from Keychain
    existing = keychain_get("sms_device_id")
    if existing:
        return existing
    
    # Generate new UUID
    new_id = str(uuid.uuid4())
    
    # Save to Keychain (persists across reinstalls)
    keychain_set("sms_device_id", new_id)
    
    return new_id
```

**iOS (JavaScript - Scriptable):**
```javascript
function getDeviceFingerprint() {
    // Check if already exists
    if (Keychain.contains(DEVICE_KEY)) {
        return Keychain.get(DEVICE_KEY);
    }
    
    // Generate new UUID
    let newId = UUID.string();
    
    // Save to Keychain
    Keychain.set(DEVICE_KEY, newId);
    
    return newId;
}
```

### Security Features

1. **One Code, One Device**: 
   - Each activation code can only be used on one device
   - Device ID stored in Keychain (survives reinstalls)

2. **Server-Side Validation**: 
   - All checks done server-side
   - Can't be bypassed by modifying client code

3. **Revocation**: 
   - Admin can revoke codes in Supabase
   - Next validation check will fail

4. **No Expiration** (currently):
   - Once activated, works forever
   - Could add expiration logic to webhook

---

## Auto-Update System

### Update Architecture

**All three implementations check for updates from GitHub Gist:**

```
┌──────────────┐
│  GitHub Gist │  (Single source of truth)
│              │
│ - version.json      ← Version number + changelog
│ - sms_campaign.py   ← Mac app code (Mac)
│ - sms_automatisation.js ← iOS Scriptable code
└──────────────┘
       │
       │ HTTPS GET
       ▼
┌──────────────┐
│   App        │
│   (checks    │
│   on launch) │
└──────────────┘
```

### Update Check Flow

**1. On Launch:**

```python
async def check_for_updates():
    # Fetch version.json from Gist
    response = requests.get(VERSION_URL)
    latest_version = response.json()['version']
    
    # Compare with current version
    if is_newer(latest_version, CURRENT_VERSION):
        # Prompt user
        if user_confirms_update():
            await download_and_install_update()
```

**2. Version Comparison:**

```python
def is_newer_version(latest, current):
    """
    Semantic versioning: MAJOR.MINOR.PATCH
    
    Examples:
    - 1.2.3 vs 1.2.4 → True (patch bump)
    - 1.2.3 vs 1.3.0 → True (minor bump)
    - 2.0.0 vs 1.9.9 → True (major bump)
    - 1.2.3 vs 1.2.3 → False (same)
    """
    latest_parts = [int(x) for x in latest.split('.')]
    current_parts = [int(x) for x in current.split('.')]
    
    for i in range(3):
        if latest_parts[i] > current_parts[i]:
            return True
        if latest_parts[i] < current_parts[i]:
            return False
    
    return False
```

**3. Download & Install:**

**Mac App:**
```python
def install_update():
    # Download new script
    new_code = requests.get(SCRIPT_URL).text
    
    # Save to ~/.sms_campaign/sms_campaign.py
    update_path = os.path.expanduser('~/.sms_campaign/sms_campaign.py')
    with open(update_path, 'w') as f:
        f.write(new_code)
    
    # Restart app with new code
    os.execv(sys.executable, [sys.executable, update_path])
```

**iOS Scriptable:**
```javascript
async function installUpdate() {
    // Download new script
    let newScript = await (new Request(UPDATE_URL)).loadString();
    
    // Overwrite current script in Scriptable storage
    let fm = getFileManager();
    let scriptName = Script.name();
    let scriptPath = fm.joinPath(
        fm.documentsDirectory(), 
        scriptName + '.js'
    );
    
    fm.writeString(scriptPath, newScript);
    
    // Alert user to restart
    let alert = new Alert();
    alert.title = "✅ Update Installed";
    alert.message = "Please restart the script.";
    await alert.present();
}
```

### Gist Configuration

**Required Files in Gist:**

1. **version.json**
```json
{
    "version": "2.4.17",
    "changelog": "Added French name compound detection",
    "date": "2026-01-05",
    "build": 17
}
```

2. **sms_campaign.py** (for Mac)
```python
#!/usr/bin/env python3
# Full source code here
```

3. **sms_automatisation.js** (for iOS)
```javascript
// Full Scriptable code here
```

### Update Publishing Workflow

```bash
# 1. Update version in code
# mac_app/sms_campaign.py
VERSION = "2.4.18"

# 2. Update version.json
echo '{
  "version": "2.4.18",
  "changelog": "Fixed bug XYZ",
  "date": "2026-01-05"
}' > version.json

# 3. Upload to Gist
# (Manual via gist.github.com or use update_gist.sh script)

# 4. Build new .app
cd mac_app
./build.sh

# 5. Upload .app to GitHub Releases
# Users get update notification on next launch
```

---

## Build & Distribution

### Mac App Build Process

**Prerequisites:**
- macOS 10.15+
- Python 3.8+
- PyInstaller

**Build Steps:**

```bash
cd mac_app

# 1. Install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install pyinstaller pywebview

# 2. Build .app bundle
./build.sh

# Output: 
# - build/ (temporary build artifacts)
# - dist/SMS Campaign.app (unsigned .app)
# - SMS Campaign.app (copy for distribution)
```

**PyInstaller Spec File (`SMS Campaign.spec`):**

```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['sms_campaign.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['webview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SMS Campaign',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SMS Campaign',
)

app = BUNDLE(
    coll,
    name='SMS Campaign.app',
    icon=None,
    bundle_identifier='com.logipret.sms-campaign',
)
```

**Distribution Package:**

```bash
# Create ZIP for distribution
zip -r 'SMS Campaign.zip' 'SMS Campaign.app'

# Upload to:
# - GitHub Releases
# - Google Drive
# - Direct download link
```

**First-Time Installation (Users):**

Since the app is **unsigned** (no Apple Developer certificate):

1. **Method 1: Right-Click Open**
   ```
   Right-click SMS Campaign.app → Open → Click "Open" in dialog
   ```

2. **Method 2: Terminal**
   ```bash
   xattr -cr '/Applications/SMS Campaign.app'
   ```

After first launch, macOS remembers it's safe.

---

### iOS Scriptable Distribution

**Distribution via Gist:**

1. **Create Gist** at gist.github.com
   - Add `sms_automatisation.js`
   - Add `version.json`
   - Set to Public

2. **Get Raw URLs:**
   ```
   Script: https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/sms_automatisation.js
   Version: https://gist.githubusercontent.com/USERNAME/GIST_ID/raw/version.json
   ```

3. **Share with Users:**
   - Option A: Send Gist URL (users copy-paste into Scriptable)
   - Option B: Create import link (iOS 14+)
   ```
   scriptable:///run?scriptName=SMS%20Automatisation
   ```

**User Installation:**

1. Install Scriptable app (free on App Store)
2. Open Gist link on iPhone
3. Copy code
4. Create new script in Scriptable
5. Paste code
6. Save as "SMS Automatisation"

**Updates:**
- Automatic via Gist
- Script checks for updates on launch
- One-tap install

---

### Mobile Web Deployment

**Hosting Options:**

1. **GitHub Pages** (Free)
   ```bash
   # Enable in repo Settings → Pages
   # URL: https://username.github.io/repo-name/
   ```

2. **Vercel** (Free)
   ```bash
   npm i -g vercel
   vercel deploy
   ```

3. **Netlify** (Free)
   - Drag & drop folder to netlify.com/drop

4. **Cloudflare Pages** (Free)
   - Connect GitHub repo
   - Auto-deploy on push

**PWA Installation:**

On iPhone Safari:
1. Visit web app URL
2. Tap Share button
3. "Add to Home Screen"
4. App appears like native app

---

## Technical Constraints & Limitations

### Apple Messages API Limitations

**Why Manual Sending is Required:**

Apple does **NOT** allow apps to send SMS/iMessage programmatically without user interaction. This is a **security/privacy feature** to prevent:
- Spam bots
- Malicious apps sending messages without consent
- Unauthorized charges (for SMS)

**What We Can Do:**
```applescript
-- Open Messages with pre-filled message
tell application "Messages"
    set targetBuddy to participant "+14385551234"
    send "Message text" to targetBuddy
end tell
```

This **DOES NOT** actually send the message. It:
1. Opens Messages app
2. Creates a new message
3. Fills in recipient + text
4. User MUST click "Send"

**Workarounds Explored:**

1. **Accessibility API** (rejected):
   - Could simulate clicks on "Send" button
   - Requires user to enable accessibility permissions
   - Apple rejects apps doing this
   - Unreliable (UI changes break it)

2. **Private APIs** (rejected):
   - Could send directly via private frameworks
   - App Store rejects apps using private APIs
   - Breaks with macOS updates
   - Legally questionable

3. **Jailbreak Solutions** (rejected):
   - Not applicable for Mac
   - Can't distribute to normal users

**Current Approach:**
- Use AppleScript to open Messages
- User clicks "Send" for each message
- App waits for user to return before next message

**Delay Between Messages:**
```python
CONFIG = {
    "message_delay": 0.2  # 200ms between opening Messages
}

for contact in contacts:
    open_messages(contact.phone, contact.message)
    time.sleep(CONFIG["message_delay"])
    # Wait for user to send and come back
```

---

### CSV Format Support

**Supported Separators:**
- Comma (`,`)
- Semicolon (`;`)
- Tab (`\t`)
- Auto-detection via Python `csv.Sniffer`

**Supported Encodings:**
- UTF-8 (preferred)
- UTF-8 with BOM
- Latin-1 (ISO-8859-1)
- Windows-1252

**Handling Edge Cases:**

1. **Quoted Fields:**
   ```csv
   "Last Name","First Name","Phone"
   "Tremblay","Jean-Pierre","438-555-1234"
   ```

2. **Escaped Quotes:**
   ```csv
   "Last Name","Message"
   "O'Brien","He said ""Hello"""
   ```

3. **Multiline Fields:**
   ```csv
   "Name","Address"
   "John Doe","123 Main St
   Apt 4B
   Montreal"
   ```

4. **Mixed Separators:**
   ```csv
   "Name";"Phone";"Note,with,commas"
   ```

**Current Limitations:**

- **Excel-Specific Formats**: 
  - `.xlsx` files must be exported to CSV first
  - No direct Excel file support

- **Complex Encodings**:
  - Some rare encodings may fail
  - Manual re-export as UTF-8 needed

- **Very Large Files**:
  - 10,000+ contacts may slow down UI
  - All processing is in-memory (no streaming)

---

### Platform-Specific Constraints

| Feature | Mac App | Mobile Web | iOS Scriptable |
|---------|---------|------------|----------------|
| **Auto-Send** | ❌ | ❌ | ❌ |
| **Background Sending** | ❌ | ❌ | ❌ |
| **Offline Mode** | ✅ | ❌ | ✅ |
| **Code Protection** | ✅ (bytecode) | ❌ | ❌ |
| **Max CSV Size** | ~100MB | ~10MB | ~5MB |
| **Update Distribution** | Gist/GitHub | Server push | Gist |
| **Installation** | .app file | URL | Copy-paste |
| **Requires Internet** | First time only | Always | First time only |

---

## Future Possibilities

### Feature Expansion Ideas

#### 1. **Scheduled Sending**

**Concept:** Queue messages to send at specific times

**Implementation:**
- Store queue in local database (SQLite)
- Background service checks queue every minute
- Opens Messages at scheduled time
- User still clicks Send

**Challenges:**
- Mac: Need background daemon or Launch Agent
- iOS: Scriptable doesn't support background tasks
- User must keep app/device running

**Code Sketch:**
```python
# Schedule for tomorrow 9 AM
schedule = {
    "contacts": [...],
    "message": "...",
    "scheduled_for": "2026-01-06 09:00:00"
}

# Daemon checks every minute
while True:
    if is_time_to_send(schedule):
        send_campaign(schedule.contacts, schedule.message)
    time.sleep(60)
```

---

#### 2. **Delivery Tracking**

**Concept:** Track which messages were actually sent

**Current Gap:** 
- App opens Messages but can't confirm user clicked Send
- No callback from Messages app

**Possible Solutions:**

**A. Manual Confirmation:**
```python
for contact in contacts:
    open_messages(contact)
    response = prompt("Did you send it? (Y/N)")
    if response == "Y":
        mark_as_sent(contact)
```

**B. Screenshots + OCR:**
```python
# Take screenshot after opening Messages
screenshot = capture_screen()

# OCR to detect "Delivered" or "Sent" status
if ocr_contains(screenshot, "Delivered"):
    mark_as_sent(contact)
```
(Unreliable, privacy concerns)

**C. Messages Database Reading:**
```python
# Messages stores chat history in SQLite
db_path = "~/Library/Messages/chat.db"
last_message = query_db(db_path, "SELECT * FROM message ORDER BY date DESC LIMIT 1")

if last_message.text == expected_message:
    mark_as_sent(contact)
```
(Requires Full Disk Access permission)

---

#### 3. **CRM Integration**

**Concept:** Import contacts directly from CRMs

**Supported CRMs:**
- HubSpot
- Salesforce
- Pipedrive
- Airtable
- Google Sheets

**Implementation:**

```python
# OAuth flow for CRM
crm_api = authenticate_crm("hubspot")

# Fetch contacts with filter
contacts = crm_api.get_contacts(
    filter="status = 'lead' AND phone IS NOT NULL"
)

# Convert to app format
for contact in contacts:
    add_to_campaign({
        "firstname": contact.firstname,
        "lastname": contact.lastname,
        "phone": contact.phone.mobile,
        "crm_id": contact.id  # For syncing back
    })
```

**Sync Back:**
```python
# After sending, update CRM
for contact in sent_contacts:
    crm_api.update_contact(contact.crm_id, {
        "last_contacted": datetime.now(),
        "last_message": message_text,
        "campaign_id": campaign_id
    })
```

**Challenges:**
- Each CRM has different API
- OAuth authentication complexity
- Rate limits on API calls

---

#### 4. **Message Templates Library**

**Concept:** Save and reuse message templates

**UI:**
```
┌─────────────────────────────────┐
│ 📝 Template Library             │
├─────────────────────────────────┤
│ ☐ Appointment Reminder          │
│ ☐ Payment Reminder              │
│ ☐ Event Invitation              │
│ ☐ Holiday Greetings             │
│ ☐ Follow-up                     │
│                                 │
│ [+ New Template]                │
└─────────────────────────────────┘
```

**Storage:**
```json
{
  "templates": [
    {
      "id": "1",
      "name": "Appointment Reminder",
      "message": "Bonjour **PRENOM**,\n\nRappel de votre rendez-vous demain à 14h.\n\nMerci!",
      "category": "business",
      "created_at": "2026-01-05"
    },
    ...
  ]
}
```

**Features:**
- Categorize templates
- Search templates
- Edit/delete templates
- Share templates (export JSON)

---

#### 5. **Multi-Language Support**

**Current:** French + English UI

**Add:**
- Spanish
- German
- Portuguese
- Chinese

**Implementation:**
```javascript
const translations = {
  en: {
    "welcome": "Welcome",
    "select_csv": "Select CSV file",
    ...
  },
  fr: {
    "welcome": "Bienvenue",
    "select_csv": "Sélectionner un fichier CSV",
    ...
  },
  es: {
    "welcome": "Bienvenido",
    "select_csv": "Seleccionar archivo CSV",
    ...
  }
}

function t(key) {
  return translations[currentLang][key];
}
```

**Dynamic Content:**
- Detect system language
- User can switch in app
- Save preference

---

#### 6. **Rich Media Support**

**Concept:** Send images/videos with messages

**Current:** Text-only messages

**Possible:**
```python
# Attach image to message
open_messages_with_image(
    phone="+14385551234",
    message="Check this out!",
    image_path="/path/to/image.jpg"
)
```

**Implementation:**
```applescript
tell application "Messages"
    set targetBuddy to participant "+14385551234"
    send "Check this out!" to targetBuddy
    send file "/path/to/image.jpg" to targetBuddy
end tell
```

**Challenges:**
- Large files slow down sending
- iMessage required (MMS fallback for non-iMessage)
- File size limits (MMS = ~1MB)

---

#### 7. **Contact Deduplication**

**Problem:** Same person appears multiple times in CSV

**Example:**
```csv
John,Doe,438-555-1234
John,Doe,438-555-1234  ← Duplicate
Jean,Doe,4385551234    ← Same phone, different format
```

**Detection:**
```python
def deduplicate_contacts(contacts):
    seen_phones = set()
    unique = []
    
    for contact in contacts:
        # Normalize phone
        normalized = format_phone(contact.phone)
        
        if normalized not in seen_phones:
            seen_phones.add(normalized)
            unique.append(contact)
        else:
            log(f"Skipping duplicate: {contact.name}")
    
    return unique
```

**Fuzzy Matching:**
```python
# Detect similar names
if levenshtein_distance(name1, name2) < 3:
    # Probably same person with typo
    merge_contacts(contact1, contact2)
```

---

#### 8. **Analytics & Reporting**

**Track:**
- Total campaigns sent
- Messages sent per campaign
- Success/failure rate
- Average time per campaign
- Most used templates

**Dashboard:**
```
┌─────────────────────────────────┐
│ 📊 Campaign Analytics           │
├─────────────────────────────────┤
│ Total Campaigns: 45             │
│ Total Messages: 2,340           │
│ Success Rate: 98.5%             │
│                                 │
│ Last 7 Days:                    │
│ ▓▓▓▓▓░░░░░░░ 450 messages       │
│                                 │
│ Top Templates:                  │
│ 1. Appointment Reminder (150x)  │
│ 2. Payment Reminder (80x)       │
│ 3. Follow-up (60x)              │
└─────────────────────────────────┘
```

**Export:**
```csv
Date,Campaign,Messages,Success,Failed
2026-01-05,Appointment Reminders,50,49,1
2026-01-04,Holiday Greetings,200,200,0
```

---

#### 9. **Group Messaging**

**Concept:** Send one message to multiple recipients (group chat)

**Implementation:**
```applescript
tell application "Messages"
    set participants to {
        participant "+14385551234",
        participant "+15145559999",
        participant "+14505557777"
    }
    send "Meeting at 2 PM!" to participants
end tell
```

**Use Cases:**
- Team notifications
- Event invitations
- Group reminders

**Challenges:**
- Creates new group chat each time
- All recipients see each other's numbers
- Potential privacy issue

---

#### 10. **Voice Message Support (Future-Future)**

**Concept:** Record voice message, send to all contacts

**How:**
1. Record audio file
2. Convert to compatible format (.m4a)
3. Attach to each message

**Implementation:**
```python
# Record audio
audio_file = record_audio(duration=30)  # 30 seconds

# Send to each contact
for contact in contacts:
    send_audio_message(contact.phone, audio_file)
```

**Challenges:**
- Large files
- iMessage required (MMS audio quality poor)
- Recording UI complexity

---

### Architecture Improvements

#### 1. **Unified Backend API**

**Current:** Each platform implements own logic

**Future:** Central API for shared logic

```
┌──────────────┐
│  Mac App     │──┐
└──────────────┘  │
                  │
┌──────────────┐  │    ┌──────────────────┐
│  Mobile Web  │──┼───▶│  Backend API     │
└──────────────┘  │    │  (FastAPI/Flask) │
                  │    │                  │
┌──────────────┐  │    │ - CSV parsing    │
│  iOS App     │──┘    │ - Auth           │
└──────────────┘       │ - Analytics      │
                       │ - Templates      │
                       └──────────────────┘
```

**Benefits:**
- Consistent logic across platforms
- Easier to add features
- Centralized analytics
- Better security

**Drawback:**
- Requires internet
- Server costs

---

#### 2. **Local Database (SQLite)**

**Current:** All data in memory, lost on exit

**Future:** Persist data locally

```python
import sqlite3

# Schema
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY,
    name TEXT,
    created_at DATETIME,
    message_template TEXT
);

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER,
    firstname TEXT,
    lastname TEXT,
    phone TEXT,
    status TEXT,  -- 'pending', 'sent', 'failed'
    sent_at DATETIME
);
```

**Benefits:**
- Resume interrupted campaigns
- Track history
- Export reports
- Undo/redo

---

#### 3. **Plugin System**

**Concept:** Allow third-party extensions

```python
class Plugin:
    def on_campaign_start(self, campaign):
        pass
    
    def on_message_sent(self, contact):
        pass
    
    def on_campaign_end(self, campaign):
        pass

# Example plugin
class SlackNotifier(Plugin):
    def on_campaign_end(self, campaign):
        send_slack_message(
            f"Campaign '{campaign.name}' completed! "
            f"{campaign.sent_count} messages sent."
        )
```

**Plugin Ideas:**
- Slack/Discord notifications
- Google Sheets sync
- Zapier integration
- Custom analytics

---

### Distribution Improvements

#### 1. **Mac App Store Distribution**

**Why:**
- Trusted installation (no xattr issues)
- Automatic updates
- Discoverability

**Requirements:**
- Apple Developer account ($99/year)
- Code signing
- Sandboxing (limits automation)
- App review process

**Challenges:**
- **Sandboxing**: Mac App Store apps can't control Messages
- **Private APIs**: Our AppleScript automation might be rejected
- **Updates**: Must go through review (slower)

**Alternative:** 
- Notarized app (trusted by Gatekeeper, not in store)
- Requires code signing but no sandbox

---

#### 2. **iOS Native App (Swift)**

**Why:**
- True native experience
- App Store distribution
- Better performance

**Challenges:**
- **Same SMS limitation**: Still can't auto-send
- **Development time**: Rewrite from scratch
- **Maintenance**: Two codebases (Mac + iOS)

**Hybrid Approach:**
- Keep Scriptable for rapid updates
- Offer native app for premium users

---

#### 3. **TestFlight Beta Program**

**For iOS Native App:**
1. Build app in Xcode
2. Upload to App Store Connect
3. Create TestFlight beta
4. Share link with testers
5. Iterate based on feedback

**Benefits:**
- Easy to add testers
- Automatic updates
- Crash reporting
- No need to collect UDIDs

---

## Technical Summary

### What Works Well

✅ **CSV Parsing**: Robust, handles edge cases  
✅ **French Names**: Compound name detection  
✅ **Phone Handling**: Multi-phone, priority, validation  
✅ **Authorization**: Device-bound, secure  
✅ **Auto-Update**: Seamless Gist-based updates  
✅ **UI/UX**: Modern, dark-themed, responsive  

### Current Limitations

❌ **Can't Auto-Send**: Apple Messages API restriction  
❌ **No Delivery Tracking**: Can't confirm user sent message  
❌ **No Background Sending**: User must stay in app  
❌ **Memory-Only**: No persistence between sessions  
❌ **No Rich Media**: Text-only messages  

### Recommended Next Steps

**Short-term (1-2 weeks):**
1. Add template library (localStorage/SQLite)
2. Implement contact deduplication
3. Add export reports (CSV/JSON)
4. Improve error messages

**Medium-term (1-2 months):**
1. Add scheduling (queue system)
2. CRM integration (start with Google Sheets)
3. Analytics dashboard
4. Multi-language UI

**Long-term (3-6 months):**
1. Backend API (optional for cloud features)
2. iOS native app (if demand exists)
3. Plugin system
4. Rich media support

---

## Contact & Support

**Repository:** (Private - contact owner for access)  
**Version Control:** Git  
**Issue Tracking:** GitHub Issues  
**Documentation:** This file + in-code comments  

---

**End of Documentation**

*This document is maintained alongside the codebase. Last updated: January 5, 2026.*

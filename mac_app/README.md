# SMS Campaign - Mac App

Standalone Mac application for mass SMS sending via iMessage.

## Features

- ✅ **Activation system** - One code per device
- ✅ **No dependencies** - Single `.app` bundle, no Python required for users
- ✅ **Auto-updates** - Updates from Gist automatically
- ✅ **Hidden code** - Python bytecode compiled, not readable
- ✅ **iMessage integration** - Sends via native Messages app
- ✅ **CSV support** - Auto-detects separators and columns
- ✅ **French names** - Fixes accent encoding issues

## Building

### Requirements

- macOS 10.15+
- Python 3.8+
- PyInstaller

### Build Steps

```bash
# Navigate to mac_app folder
cd mac_app

# Make build script executable
chmod +x build.sh

# Build the app
./build.sh
```

The built app will be at `mac_app/SMS Campaign.app`

### Distribution

1. Build the app
2. Create a ZIP: `zip -r 'SMS Campaign.zip' 'SMS Campaign.app'`
3. Share with users along with `INSTALLATION_GUIDE.md`

## Authorization System

The app uses the same authorization backend as the iOS version:

- **Webhook**: `https://n8n-wwfb.onrender.com/webhook/...`
- **Backend**: Supabase `sms_authorisation_codes` table
- **Device ID**: Stored in macOS Keychain (persistent UUID)
- **Auth Code**: Stored in macOS Keychain

### Keychain Keys

| Key | Service | Description |
|-----|---------|-------------|
| `sms_device_id` | `com.logipret.sms-campaign` | Unique device UUID |
| `sms_auth_code` | `com.logipret.sms-campaign` | Activation code |

### Viewing Keychain entries (debug)

```bash
# View device ID
security find-generic-password -s "com.logipret.sms-campaign" -a "sms_device_id" -w

# View auth code
security find-generic-password -s "com.logipret.sms-campaign" -a "sms_auth_code" -w
```

### Clearing Keychain (reset activation)

```bash
security delete-generic-password -s "com.logipret.sms-campaign" -a "sms_auth_code"
```

## Updates

The app checks for updates from:
- `VERSION_URL`: Gist with `version.json`
- `SCRIPT_URL`: Gist with `sms_campaign.py`

When an update is available:
1. User is prompted to update
2. New script is downloaded to `~/.sms_campaign/sms_campaign.py`
3. App restarts with the updated script

**Note**: For bundled apps, updates require system Python to be installed.

## File Structure

```
mac_app/
├── sms_campaign.py       # Main application code
├── SMS Campaign.spec     # PyInstaller build configuration
├── build.sh              # Build script
├── version.json          # Version info (uploaded to Gist)
├── INSTALLATION_GUIDE.md # User installation guide
└── README.md             # This file
```

## Security Notes

- Code is compiled to Python bytecode (not easily readable)
- Activation code stored in macOS Keychain (secure, per-user)
- Device ID persists across reinstalls (Keychain)
- Each activation code works on only ONE device
- Webhook validates device_id matches stored device

## Gist Setup

1. Create a new Gist with:
   - `sms_campaign.py` (the Python script)
   - `version.json` (version info)

2. Update `GIST_ID` in `sms_campaign.py` with the new Gist ID

3. Users will get automatic updates when you update the Gist

## Troubleshooting

### App won't open (security warning)

Users need to right-click → Open, or run:
```bash
xattr -cr '/Applications/SMS Campaign.app'
```

### "Code already used on another device"

Each code can only be activated on one device. The device_id is stored in Keychain and persists across reinstalls.

### Messages not sending

Check that:
1. Messages.app is signed into iMessage
2. User has granted automation permissions
3. Phone numbers are valid (10 digits for Canada)

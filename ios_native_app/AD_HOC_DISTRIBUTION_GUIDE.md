# iOS Native App - Ad Hoc Distribution Guide

This guide explains how to build and distribute the SMS Campaign app as a native iOS app using Ad Hoc distribution, keeping your source code hidden from end users.

---

## Prerequisites

### 1. Apple Developer Account
- **Cost:** $99/year
- **Sign up:** https://developer.apple.com/programs/enroll/
- Approval takes 24-48 hours

### 2. Development Environment
- macOS with Xcode installed (free from App Store)
- iOS device for testing

---

## One-Time Setup (First Time Only)

### Step 1: Create Certificates

1. Open **Xcode** → Preferences → Accounts
2. Add your Apple ID
3. Click "Manage Certificates"
4. Click **+** → "Apple Distribution" certificate

Or via Apple Developer Portal:
1. Go to https://developer.apple.com/account/resources/certificates
2. Click **+** to create a new certificate
3. Choose "iOS Distribution (App Store and Ad Hoc)"
4. Follow the CSR (Certificate Signing Request) process

### Step 2: Register App ID

1. Go to https://developer.apple.com/account/resources/identifiers
2. Click **+** → "App IDs" → "App"
3. Fill in:
   - **Description:** SMS Campaign
   - **Bundle ID:** `com.logipret.smscampaign` (or your choice)
4. No special capabilities needed
5. Click "Continue" → "Register"

---

## Adding New Users (Repeat for Each User)

### Step 1: Collect Device UDID

Each user must send you their device's UDID. They can find it via:

**Option A: Finder/iTunes**
1. Connect iPhone to Mac
2. Open Finder (macOS Catalina+) or iTunes
3. Click on device → Click on device info until UDID appears
4. Right-click → Copy UDID

**Option B: Web Service**
- Send user to https://udid.io or similar
- They follow instructions to get UDID

**UDID Format:** `00008030-001234567890402E` (40 hex characters)

### Step 2: Register Device in Apple Portal

1. Go to https://developer.apple.com/account/resources/devices
2. Click **+**
3. Enter:
   - **Device Name:** "User Name's iPhone" (for your reference)
   - **Device ID (UDID):** paste the UDID
4. Click "Continue" → "Register"

⚠️ **Limit:** 100 devices per year (resets on membership renewal)

### Step 3: Create/Update Provisioning Profile

**First time:**
1. Go to https://developer.apple.com/account/resources/profiles
2. Click **+**
3. Choose "Ad Hoc"
4. Select your App ID (`com.logipret.smscampaign`)
5. Select your Distribution Certificate
6. Select ALL registered devices (check all)
7. Name it: "SMS Campaign Ad Hoc"
8. Click "Generate" → Download the `.mobileprovision` file

**Adding more users later:**
1. Go to Profiles → Click on "SMS Campaign Ad Hoc"
2. Click "Edit"
3. Check the new device(s)
4. Click "Generate" → Download new `.mobileprovision`

---

## Building the App

### Step 1: Open Project in Xcode

```bash
cd ios_native_app
open SMSCampaign.xcodeproj
```

### Step 2: Configure Signing

1. Select the project in the navigator
2. Select the "SMSCampaign" target
3. Go to "Signing & Capabilities" tab
4. Uncheck "Automatically manage signing"
5. Select your Team
6. Import the downloaded `.mobileprovision` file
   - Or select it from the "Provisioning Profile" dropdown

### Step 3: Archive the App

1. Select "Any iOS Device" as the build target (not a simulator)
2. Menu: **Product → Archive**
3. Wait for build to complete
4. Organizer window opens automatically

### Step 4: Export .ipa File

1. In Organizer, select the new archive
2. Click "Distribute App"
3. Choose "Ad Hoc"
4. Click "Next" through the options
5. Choose export location
6. You'll get a `.ipa` file

---

## Distributing to Users

### Option A: AirDrop (Easiest)

1. AirDrop the `.ipa` file to user's iPhone
2. They open it → Tap "Install"
3. Go to Settings → General → VPN & Device Management
4. Trust your developer certificate

### Option B: Direct Download Link

1. Host the `.ipa` on a web server (HTTPS required)
2. Create a manifest `.plist` file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>items</key>
    <array>
        <dict>
            <key>assets</key>
            <array>
                <dict>
                    <key>kind</key>
                    <string>software-package</string>
                    <key>url</key>
                    <string>https://yourserver.com/SMSCampaign.ipa</string>
                </dict>
            </array>
            <key>metadata</key>
            <dict>
                <key>bundle-identifier</key>
                <string>com.logipret.smscampaign</string>
                <key>bundle-version</key>
                <string>1.0</string>
                <key>kind</key>
                <string>software</string>
                <key>title</key>
                <string>SMS Campaign</string>
            </dict>
        </dict>
    </array>
</dict>
</plist>
```

3. Create an install link:
```html
<a href="itms-services://?action=download-manifest&url=https://yourserver.com/manifest.plist">
    Install SMS Campaign
</a>
```

### Option C: Apple Configurator 2

1. Download Apple Configurator 2 (free on Mac App Store)
2. Connect user's iPhone
3. Drag `.ipa` onto the device

---

## First Launch (User Must Do)

After installation, the app won't open until trusted:

1. Open **Settings** → **General** → **VPN & Device Management**
2. Find your developer certificate under "Developer App"
3. Tap it → Tap "Trust"
4. Confirm trust
5. App will now launch normally

---

## Annual Renewal Process

### Timeline
| Event | Action Required |
|-------|-----------------|
| ~11 months | Set reminder to renew |
| Membership expires | App stops launching for ALL users |
| After renewal | Must rebuild & redistribute |

### Renewal Steps

1. **Renew Apple Developer membership** ($99)
   - https://developer.apple.com/account

2. **Generate new provisioning profile**
   - Go to Profiles in developer portal
   - Regenerate the Ad Hoc profile

3. **Rebuild the app**
   - Open project in Xcode
   - Update provisioning profile
   - Archive → Export new `.ipa`

4. **Redistribute to ALL users**
   - Contact each user
   - Send new `.ipa` via AirDrop or download link
   - They reinstall (same trust process)

---

## Troubleshooting

### "Unable to Install"
- Device UDID not in provisioning profile → Add device, regenerate profile, rebuild

### App crashes immediately on launch
- Provisioning profile expired → Renew membership, rebuild
- Wrong bundle ID → Check Xcode settings match App ID

### "Untrusted Developer"
- User needs to trust certificate in Settings (see "First Launch" section)

### Can't find UDID
- Use https://udid.io or connect to Mac with Finder

---

## Quick Reference

| Item | Value |
|------|-------|
| Bundle ID | `com.logipret.smscampaign` |
| Provisioning Profile | SMS Campaign Ad Hoc |
| Device Limit | 100/year |
| Profile Expiry | 1 year |
| Cost | $99/year |

---

## Files to Create

When building the native app, you'll need:

```
ios_native_app/
├── SMSCampaign.xcodeproj/
├── SMSCampaign/
│   ├── AppDelegate.swift
│   ├── SceneDelegate.swift
│   ├── ContentView.swift          # Main UI
│   ├── CSVParser.swift            # Port from JS
│   ├── MessageComposer.swift      # MFMessageComposeViewController
│   ├── Assets.xcassets/
│   └── Info.plist
└── AD_HOC_DISTRIBUTION_GUIDE.md   # This file
```

The Swift app will replicate the functionality of `app/sms_automatisation.js` but compiled, so source code is hidden.

---

## Next Steps

1. ✅ Read this guide
2. ⏳ Enroll in Apple Developer Program ($99)
3. ⏳ Create the Swift iOS project (ask me when ready)
4. ⏳ Build and test on your device
5. ⏳ Collect user UDIDs and distribute

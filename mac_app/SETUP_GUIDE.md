# SMS Campaign - Setup Guide / Guide de Configuration

## 🍎 Mac Settings / Paramètres Mac

### 1. Messages App Configuration / Configuration de l'app Messages

| English | Français |
|---------|----------|
| **Open Messages app** | **Ouvrir l'app Messages** |
| Messages → Settings → iMessage | Messages → Réglages → iMessage |
| ✅ Enable "Enable Messages in iCloud" | ✅ Activer "Activer Messages sur iCloud" |
| ✅ Your phone number must be checked under "You can be reached for messages at" | ✅ Votre numéro de téléphone doit être coché sous "Vous pouvez recevoir des messages à" |

### 2. Text Message Forwarding / Transfert de messages texte

| English | Français |
|---------|----------|
| **On your iPhone**: Settings → Messages → Text Message Forwarding | **Sur votre iPhone**: Réglages → Messages → Transfert de messages texte |
| ✅ Enable your Mac in the list | ✅ Activer votre Mac dans la liste |
| A verification code will appear on your Mac - enter it on iPhone | Un code de vérification apparaîtra sur votre Mac - entrez-le sur iPhone |

### 3. System Permissions / Autorisations système

| English | Français |
|---------|----------|
| System Settings → Privacy & Security → Automation | Réglages Système → Confidentialité et sécurité → Automatisation |
| ✅ Allow Terminal (or your browser) to control Messages | ✅ Autoriser Terminal (ou votre navigateur) à contrôler Messages |
| System Settings → Privacy & Security → Accessibility | Réglages Système → Confidentialité et sécurité → Accessibilité |
| ✅ Allow Terminal if prompted | ✅ Autoriser Terminal si demandé |

### 4. AppleScript Permissions / Autorisations AppleScript

| English | Français |
|---------|----------|
| When first running the script, macOS will ask: "Terminal wants to control Messages" | Lors du premier lancement, macOS demandera: "Terminal souhaite contrôler Messages" |
| ✅ Click "OK" / "Allow" | ✅ Cliquer "OK" / "Autoriser" |

---

## 📱 iPhone Settings / Paramètres iPhone

### 1. iMessage & SMS Settings / Paramètres iMessage & SMS

| English | Français |
|---------|----------|
| Settings → Messages | Réglages → Messages |
| ✅ iMessage: ON | ✅ iMessage: ACTIVÉ |
| ✅ Send as SMS: ON | ✅ Envoyer comme SMS: ACTIVÉ |
| ✅ MMS Messaging: ON | ✅ Service MMS: ACTIVÉ |

### 2. Text Message Forwarding / Transfert de messages texte

| English | Français |
|---------|----------|
| Settings → Messages → Text Message Forwarding | Réglages → Messages → Transfert de messages texte |
| ✅ Enable your Mac (must be signed in with same Apple ID) | ✅ Activer votre Mac (doit être connecté avec le même identifiant Apple) |

### 3. Send & Receive / Envoi et réception

| English | Français |
|---------|----------|
| Settings → Messages → Send & Receive | Réglages → Messages → Envoi et réception |
| ✅ Your phone number must be checked | ✅ Votre numéro de téléphone doit être coché |
| ✅ Check "Start new conversations from" = Your phone number | ✅ Cocher "Démarrer les conversations depuis" = Votre numéro de téléphone |

### 4. Carrier Settings / Paramètres opérateur

| English | Français |
|---------|----------|
| Settings → General → About | Réglages → Général → Informations |
| Wait for carrier update prompt if available | Attendre la demande de mise à jour opérateur si disponible |
| ✅ Install any carrier updates | ✅ Installer les mises à jour opérateur |

---

## ⚠️ Troubleshooting / Dépannage

### SMS not sending / SMS non envoyés

| Problem | Solution (EN) | Solution (FR) |
|---------|---------------|---------------|
| "No SMS service" error | Ensure iPhone is connected to cellular network and Text Message Forwarding is enabled | Assurez-vous que l'iPhone est connecté au réseau cellulaire et que le Transfert de messages est activé |
| Messages appear green but don't send | Check carrier settings and cellular connection on iPhone | Vérifiez les paramètres opérateur et la connexion cellulaire sur iPhone |
| Permission denied | Re-enable Terminal in Automation settings | Réactiver Terminal dans les paramètres d'Automatisation |

### Messages delayed / Messages retardés

| Problem | Solution (EN) | Solution (FR) |
|---------|---------------|---------------|
| Conversations don't appear immediately | This is normal - iOS batches notification updates | C'est normal - iOS regroupe les notifications |
| Try: Open Messages app before running script | Ouvrir l'app Messages avant de lancer le script |
| Try: Pull down to refresh conversation list | Tirer vers le bas pour rafraîchir la liste des conversations |

### iCloud Sync Issues / Problèmes de synchronisation iCloud

| Problem | Solution (EN) | Solution (FR) |
|---------|---------------|---------------|
| Messages not syncing | Settings → Apple ID → iCloud → Messages: Toggle OFF then ON | Réglages → Identifiant Apple → iCloud → Messages: Désactiver puis réactiver |
| Wait 5 minutes for sync to complete | Attendre 5 minutes pour que la synchronisation se termine |

---

## ✅ Quick Checklist / Liste de vérification rapide

### Mac
- [ ] Messages app signed in with Apple ID / Connecté avec l'identifiant Apple
- [ ] Phone number visible in Messages → Settings / Numéro visible dans Messages → Réglages
- [ ] Terminal allowed to control Messages / Terminal autorisé à contrôler Messages

### iPhone
- [ ] iMessage ON / iMessage ACTIVÉ
- [ ] Send as SMS ON / Envoyer comme SMS ACTIVÉ
- [ ] Text Message Forwarding → Mac enabled / Transfert de messages → Mac activé
- [ ] Same Apple ID as Mac / Même identifiant Apple que le Mac
- [ ] Cellular connection active / Connexion cellulaire active

---

## 🚀 Running the App / Lancer l'application

### Terminal Command / Commande Terminal:
```bash
cd /path/to/mac_app && python3 sms_campaign.py
```

### Or double-click / Ou double-cliquer:
`SMS Campaign.command`

---

## 📞 Support

If issues persist after checking all settings:
1. Restart Messages app on Mac and iPhone
2. Sign out and back into iMessage on both devices
3. Restart both devices

Si les problèmes persistent après avoir vérifié tous les paramètres:
1. Redémarrer l'app Messages sur Mac et iPhone
2. Se déconnecter et reconnecter à iMessage sur les deux appareils
3. Redémarrer les deux appareils

# 📱 SMS Campaign - Guide d'installation

## Installation (1 minute)

### Étape 1: Télécharger
1. Téléchargez le fichier `SMS Campaign.zip`
2. Double-cliquez pour décompresser

### Étape 2: Installer
1. Glissez `SMS Campaign.app` dans votre dossier **Applications**

### Étape 3: Premier lancement (important!)

⚠️ **Comme l'application n'est pas signée par Apple, vous devez l'ouvrir manuellement la première fois:**

**Option A: Clic droit**
1. Faites un **clic droit** sur `SMS Campaign.app`
2. Cliquez sur **Ouvrir**
3. Dans la boîte de dialogue, cliquez sur **Ouvrir**

**Option B: Terminal** (plus rapide)
```bash
xattr -cr /Applications/SMS\ Campaign.app
```
Puis double-cliquez normalement.

---

## Premier lancement

1. L'application vous demandera un **code d'activation**
2. Entrez le code fourni par votre administrateur
3. Cliquez sur **Activer**

✅ L'activation est permanente sur cet appareil.

---

## Utilisation

### 1. Sélectionner un fichier CSV
- Le fichier doit contenir une colonne téléphone
- Colonnes reconnues: `phone`, `telephone`, `mobile`, `work`, `home`
- Colonnes nom: `prenom`, `nom`, `firstname`, `lastname`

### 2. Écrire le message
Utilisez les variables:
- `**PRENOM**` → remplacé par le prénom
- `**NOM**` → remplacé par le nom

Exemple:
```
Bonjour **PRENOM**, votre rendez-vous est confirmé!
```

### 3. Envoyer
- Vérifiez l'aperçu
- Cliquez sur **Envoyer**
- Les messages sont envoyés via iMessage

---

## Résolution de problèmes

### "L'application ne peut pas être ouverte"
→ Suivez l'**Étape 3** ci-dessus (clic droit → Ouvrir)

### "Code invalide"
→ Contactez votre administrateur pour un nouveau code

### "Ce code a déjà été utilisé"
→ Chaque code ne fonctionne que sur **un seul appareil**

### Messages non envoyés
→ Vérifiez que:
- Messages.app est configuré avec votre compte
- Vous êtes connecté à Internet
- Le numéro de téléphone est valide (10 chiffres)

---

## Support

📧 Contact: hugo@logipret.com

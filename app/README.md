# SMS Mass Send - iPhone App (Scriptable)

Une application iPhone utilisant Scriptable pour envoyer des SMS/iMessages en masse depuis un fichier CSV.

## 📱 Prérequis

1. **Installer Scriptable** depuis l'App Store : [Scriptable](https://apps.apple.com/app/scriptable/id1405459188)
2. **Fichier CSV** accessible depuis l'app Fichiers (iCloud Drive, On My iPhone, etc.)

## 🚀 Installation

1. Ouvrir l'app **Scriptable** sur ton iPhone
2. Appuyer sur **+** pour créer un nouveau script
3. Copier/coller le contenu de `script.js`
4. Renommer le script "SMS Mass Send"
5. Appuyer sur ▶️ pour exécuter

## 📋 Format du CSV

Le fichier CSV doit contenir au minimum :
- Une colonne **prénom** (first name, prénom, firstname, etc.)
- Une colonne **téléphone** (phone, mobile, cell, téléphone, etc.)

Optionnel :
- Une colonne **nom** (last name, nom, lastname, etc.)

### Exemple :
```csv
First Name,Last Name,Phone
Jean,Tremblay,+14385551234
Marie,Dubois,5145559876
```

## 💬 Variables disponibles dans le message

- `**PRENOM**` → Prénom du contact
- `**NOM**` → Nom du contact

### Exemple de message :
```
Bonjour **PRENOM**,

J'aimerais te contacter pour une question rapide.

Merci!
```

## ⚠️ Limitations iOS

Apple impose des restrictions de sécurité :
- **Chaque message nécessite une confirmation** (cliquer Envoyer)
- C'est une protection anti-spam d'Apple, impossible à contourner
- Le script pré-remplit tout, tu n'as qu'à cliquer Envoyer

## 📁 Structure des fichiers

```
app/
├── README.md           # Ce fichier
├── ARCHITECTURE.md     # Architecture technique
├── FLOW.md             # Flow utilisateur détaillé
├── script.js           # Le script Scriptable principal
└── examples/
    └── test.csv        # Fichier CSV de test
```

## 🔧 Fonctionnalités

- ✅ Import CSV depuis l'app Fichiers
- ✅ Détection automatique des colonnes
- ✅ Nettoyage des numéros de téléphone
- ✅ Variables dynamiques dans le message
- ✅ Support des caractères spéciaux et accents
- ✅ Gestion des virgules dans les champs CSV
- ✅ Rapport de fin avec statistiques

## 📞 Support

Pour toute question, consulter les fichiers de documentation dans ce dossier.

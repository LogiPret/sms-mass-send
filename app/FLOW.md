# Flow Utilisateur

## Vue d'ensemble du parcours

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Lancer    │────▶│  Sélection  │────▶│   Écrire    │────▶│  Confirmer  │
│   Script    │     │    CSV      │     │   Message   │     │   Envoi     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Rapport   │◀────│   Répéter   │◀────│   Cliquer   │◀────│   Message   │
│    Final    │     │   Boucle    │     │   Envoyer   │     │  Pré-rempli │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

---

## Étape 1 : Lancement du script

**Action utilisateur :** Ouvrir Scriptable → Taper sur "SMS Mass Send"

**Ce qui se passe :**
- Le script démarre
- Vérifie les permissions nécessaires

**UI :**
```
┌────────────────────────────────┐
│  📱 SMS Mass Send              │
│                                │
│  Bienvenue ! Ce script va     │
│  t'aider à envoyer des SMS    │
│  en masse depuis un CSV.      │
│                                │
│  [Commencer]                   │
└────────────────────────────────┘
```

---

## Étape 2 : Sélection du fichier CSV

**Action utilisateur :** Naviguer dans Fichiers et sélectionner le CSV

**Ce qui se passe :**
- DocumentPicker s'ouvre
- L'utilisateur choisit son fichier
- Le script lit et parse le contenu

**UI :**
```
┌────────────────────────────────┐
│  📁 Sélectionne ton CSV        │
│                                │
│  ┌────────────────────────┐   │
│  │ iCloud Drive           │   │
│  │ ├── campagne_noel.csv ✓│   │
│  │ ├── clients_2024.csv   │   │
│  │ └── contacts.csv       │   │
│  └────────────────────────┘   │
│                                │
│  [Annuler]        [Ouvrir]    │
└────────────────────────────────┘
```

---

## Étape 3 : Détection des colonnes

**Action utilisateur :** Vérifier que les colonnes sont bien détectées

**Ce qui se passe :**
- Le script analyse les en-têtes
- Détecte automatiquement prénom, nom, téléphone
- Affiche un résumé pour confirmation

**UI :**
```
┌────────────────────────────────┐
│  ✅ Colonnes détectées         │
│                                │
│  • Prénom : colonne 1 (First)  │
│  • Nom : colonne 2 (Last)      │
│  • Téléphone : colonne 3       │
│                                │
│  📊 42 contacts trouvés        │
│                                │
│  [Annuler]      [Continuer]   │
└────────────────────────────────┘
```

**Si colonnes manquantes :**
```
┌────────────────────────────────┐
│  ⚠️ Colonnes manquantes        │
│                                │
│  Je n'ai pas trouvé :          │
│  • Téléphone (phone/mobile)    │
│                                │
│  Colonnes dans ton CSV :       │
│  Name, Email, Address          │
│                                │
│  [Annuler]      [Réessayer]   │
└────────────────────────────────┘
```

---

## Étape 4 : Saisie du message

**Action utilisateur :** Taper le message avec les variables

**Ce qui se passe :**
- Un champ de texte s'affiche
- L'utilisateur tape son message
- Peut utiliser **PRENOM** et **NOM** comme variables

**UI :**
```
┌────────────────────────────────┐
│  ✏️ Ton message                 │
│                                │
│  Variables disponibles :        │
│  • **PRENOM** → prénom         │
│  • **NOM** → nom de famille    │
│                                │
│  ┌────────────────────────┐   │
│  │ Bonjour **PRENOM**,    │   │
│  │                         │   │
│  │ J'aimerais te poser    │   │
│  │ une question rapide... │   │
│  │                         │   │
│  │ Merci!                  │   │
│  └────────────────────────┘   │
│                                │
│  [Annuler]      [Suivant]     │
└────────────────────────────────┘
```

---

## Étape 5 : Confirmation avant envoi

**Action utilisateur :** Vérifier le résumé et confirmer

**Ce qui se passe :**
- Affiche un aperçu du premier message
- Montre le nombre total de messages à envoyer
- Demande confirmation

**UI :**
```
┌────────────────────────────────┐
│  📨 Prêt à envoyer             │
│                                │
│  Aperçu (1er message) :        │
│  ┌────────────────────────┐   │
│  │ À: +14385551234         │   │
│  │ Bonjour Jean,           │   │
│  │ J'aimerais te poser     │   │
│  │ une question rapide...  │   │
│  └────────────────────────┘   │
│                                │
│  📊 42 messages à envoyer      │
│                                │
│  ⚠️ Tu devras cliquer Envoyer  │
│  pour chaque message           │
│                                │
│  [Annuler]      [Commencer]   │
└────────────────────────────────┘
```

---

## Étape 6 : Boucle d'envoi

**Action utilisateur :** Pour chaque contact, cliquer "Envoyer" dans Messages

**Ce qui se passe :**
- Le script ouvre Messages avec le numéro et texte pré-remplis
- L'utilisateur clique Envoyer
- Revient à Scriptable (automatiquement ou manuellement)
- Passe au contact suivant

**UI Messages (système) :**
```
┌────────────────────────────────┐
│  Messages    +14385551234      │
│                                │
│                                │
│                                │
│  ┌────────────────────────┐   │
│  │ Bonjour Jean,           │   │
│  │ J'aimerais te poser     │   │
│  │ une question rapide...  │   │
│  │ Merci!                  │   │
│  └────────────────────────┘ ⬆️│
│                                │
└────────────────────────────────┘
```

**Entre chaque envoi (optionnel) :**
```
┌────────────────────────────────┐
│  📨 Envoi en cours...          │
│                                │
│  ✅ Jean Tremblay - envoyé     │
│  ⏳ Marie Dubois - suivant     │
│                                │
│  Progression : 12/42           │
│  ████████░░░░░░░░ 28%          │
│                                │
│  [Suivant]         [Arrêter]  │
└────────────────────────────────┘
```

---

## Étape 7 : Rapport final

**Action utilisateur :** Consulter le résumé

**Ce qui se passe :**
- Affiche les statistiques
- Liste les contacts ignorés avec la raison
- Propose de sauvegarder le rapport

**UI :**
```
┌────────────────────────────────┐
│  ✅ Campagne terminée !        │
│                                │
│  📊 Statistiques :             │
│  • Envoyés : 40                │
│  • Ignorés : 2                 │
│                                │
│  ⚠️ Lignes ignorées :          │
│  • Ligne 15 : Prénom vide      │
│  • Ligne 28 : Tél. invalide    │
│                                │
│  [Fermer]   [Sauver rapport]  │
└────────────────────────────────┘
```

---

## Gestion des erreurs

### Erreur : Fichier non CSV
```
┌────────────────────────────────┐
│  ❌ Erreur                      │
│                                │
│  Le fichier sélectionné n'est  │
│  pas un fichier CSV valide.    │
│                                │
│  [Réessayer]                   │
└────────────────────────────────┘
```

### Erreur : Fichier vide
```
┌────────────────────────────────┐
│  ❌ Erreur                      │
│                                │
│  Le fichier CSV est vide ou    │
│  ne contient que l'en-tête.    │
│                                │
│  [Réessayer]                   │
└────────────────────────────────┘
```

### Erreur : Annulation utilisateur
```
┌────────────────────────────────┐
│  ⏹ Envoi interrompu            │
│                                │
│  Tu as arrêté l'envoi.         │
│                                │
│  • Envoyés : 15                │
│  • Restants : 27               │
│                                │
│  [Reprendre]        [Quitter] │
└────────────────────────────────┘
```

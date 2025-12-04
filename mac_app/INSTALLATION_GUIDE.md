# 📱 SMS Campaign - Guide d'installation Mac

## Prérequis

- Mac avec macOS 12 (Monterey) ou plus récent
- iPhone configuré avec Messages (iMessage + SMS)
- iPhone et Mac connectés au même compte Apple ID

---

## 📋 Étape 1: Télécharger l'application

1. Téléchargez le fichier `SMS Campaign.zip`
2. Double-cliquez pour décompresser
3. Glissez `SMS Campaign.app` dans votre dossier **Applications**

```
📁 Applications
   └── 📱 SMS Campaign.app
```

---

## 🔓 Étape 2: Autoriser l'application (première fois seulement)

Comme l'application n'est pas signée par Apple, macOS la bloque par défaut.

### Méthode 1: Clic droit (Recommandée)

1. **Clic droit** sur `SMS Campaign.app`
2. Cliquez sur **"Ouvrir"**
3. Dans la fenêtre d'avertissement, cliquez **"Ouvrir"**

```
┌────────────────────────────────────────────┐
│  "SMS Campaign" ne peut pas être ouvert    │
│  car le développeur n'a pas pu être        │
│  vérifié.                                  │
│                                            │
│         [Annuler]    [Ouvrir]              │
└────────────────────────────────────────────┘
         Cliquez sur "Ouvrir" ───────────────┘
```

### Méthode 2: Via les Préférences Système

1. Ouvrez **Réglages Système** > **Confidentialité et sécurité**
2. Faites défiler jusqu'à la section **Sécurité**
3. Vous verrez: `"SMS Campaign" a été bloqué`
4. Cliquez sur **"Ouvrir quand même"**

---

## 📨 Étape 3: Configurer Messages sur Mac

### 3.1 Activer le transfert de SMS

Sur votre **iPhone**:

1. Ouvrez **Réglages** > **Messages**
2. Appuyez sur **Transfert de SMS**
3. **Activez** votre Mac dans la liste

```
┌─────────────────────────────────────┐
│ ⚙️ Réglages > Messages              │
├─────────────────────────────────────┤
│                                     │
│ Transfert de SMS           ▶       │
│                                     │
│   ┌─────────────────────────────┐  │
│   │ MacBook Pro de Hugo    [✓] │  │
│   │ iMac de Bureau         [ ] │  │
│   └─────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### 3.2 Vérifier la configuration Messages sur Mac

Sur votre **Mac**:

1. Ouvrez l'app **Messages**
2. Allez dans **Messages** > **Réglages** (ou `⌘,`)
3. Onglet **iMessage**
4. Vérifiez que votre numéro de téléphone est coché

```
┌─────────────────────────────────────────────┐
│ Messages > Réglages > iMessage              │
├─────────────────────────────────────────────┤
│                                             │
│ Vous pouvez recevoir des messages à:        │
│                                             │
│   [✓] votreemail@icloud.com                 │
│   [✓] +1 (514) 555-1234  ◀── Important!    │
│                                             │
│ Démarrer les conversations depuis:          │
│   [+1 (514) 555-1234        ▼]              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 🔐 Étape 4: Accorder les permissions (première utilisation)

Au premier lancement, macOS demandera des permissions:

### 4.1 Permission d'automatisation

```
┌────────────────────────────────────────────┐
│  "SMS Campaign" souhaite contrôler         │
│  "Messages". Cette autorisation            │
│  permet d'envoyer des SMS.                 │
│                                            │
│         [Refuser]    [OK]                  │
└────────────────────────────────────────────┘
                        ▲
                  Cliquez OK
```

### 4.2 Vérifier les permissions (si nécessaire)

Si l'app ne fonctionne pas:

1. **Réglages Système** > **Confidentialité et sécurité**
2. Cliquez sur **Automatisation** (dans la barre latérale)
3. Trouvez **SMS Campaign**
4. Cochez **Messages**

```
┌─────────────────────────────────────────────┐
│ Confidentialité et sécurité > Automatisation│
├─────────────────────────────────────────────┤
│                                             │
│ SMS Campaign                                │
│   [✓] Messages  ◀── Doit être coché        │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 📄 Étape 5: Préparer votre fichier CSV

### Format recommandé

Créez un fichier CSV avec au minimum une colonne **Nom** et une colonne **Téléphone**:

```csv
Prénom,Téléphone
Jean Dupont,514-555-1234
Marie Tremblay,438-555-5678
Pierre Côté,579-555-9012
```

### Formats de téléphone acceptés

| Format | Exemple | ✓/✗ |
|--------|---------|-----|
| 10 chiffres | `5145551234` | ✓ |
| Avec tirets | `514-555-1234` | ✓ |
| Avec espaces | `514 555 1234` | ✓ |
| Avec parenthèses | `(514) 555-1234` | ✓ |
| Avec +1 | `+1 514-555-1234` | ✓ |
| International | `+33 6 12 34 56 78` | ✓ |

### Plusieurs numéros par contact

L'app supporte plusieurs colonnes téléphone:

```csv
Nom,Mobile,Travail,Maison
Jean Dupont,514-555-1234,514-555-0000,514-555-1111
```

L'app détectera automatiquement les colonnes et vous permettra de définir la priorité.

---

## 🚀 Étape 6: Utiliser l'application

### Workflow en 4 étapes

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ÉTAPE 1    │───▶│   ÉTAPE 2    │───▶│   ÉTAPE 3    │───▶│   ÉTAPE 4    │
│ Sélectionner │    │   Mapper     │    │  Composer    │    │   Envoyer    │
│   CSV        │    │  Colonnes    │    │   Message    │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Étape 1: Sélectionner le fichier CSV
- Cliquez sur la zone de dépôt
- Sélectionnez votre fichier CSV

### Étape 2: Mapper les colonnes
- Cliquez sur la colonne **NOM** (devient vert)
- Cliquez sur la colonne **TÉLÉPHONE** (devient orange)
- Si plusieurs colonnes téléphone sont détectées, réorganisez la priorité

### Étape 3: Composer le message
- Écrivez votre message
- Utilisez `{name}` pour personnaliser avec le prénom
- Exemple: `Bonjour {name}, votre rendez-vous est confirmé.`

### Étape 4: Vérifier et envoyer
- Vérifiez la liste des contacts valides
- Consultez les contacts ignorés (numéros invalides)
- Cliquez sur **Envoyer tous les SMS**

---

## ⚠️ Dépannage

### "L'application ne s'ouvre pas"

1. Clic droit > Ouvrir
2. Ou: Réglages Système > Confidentialité > Ouvrir quand même

### "Les SMS ne s'envoient pas"

1. Vérifiez que Messages est ouvert sur Mac
2. Vérifiez le transfert SMS activé sur iPhone
3. Vérifiez les permissions d'automatisation

### "Certains contacts sont ignorés"

- Le numéro a moins de 10 chiffres
- Le numéro contient des caractères invalides
- La cellule nom ou téléphone est vide

### "Les accents s'affichent mal (�)"

L'application corrige automatiquement les accents corrompus.
Si le problème persiste, sauvegardez votre CSV en encodage UTF-8.

---

## 📞 Support

Pour toute question, contactez le support technique LogiPret.

---

*Version: 1.0 | Dernière mise à jour: Décembre 2024*

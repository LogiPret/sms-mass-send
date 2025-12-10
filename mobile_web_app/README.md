# SMS Campaign - Web App (Proof of Concept)

Une version web de l'application SMS Campaign qui fonctionne sur iPhone via Safari.

## Fonctionnalités

- ✅ Import de fichiers CSV
- ✅ Détection automatique des colonnes (prénom, nom, téléphone)
- ✅ Variables personnalisées (`**PRENOM**`, `**NOM**`)
- ✅ Aperçu du message
- ✅ Ouverture de l'app Messages avec message pré-rempli via `sms:` URL scheme
- ✅ Suivi des contacts envoyés
- ✅ Interface mobile optimisée (PWA-ready)

## Comment tester

### Option 1: Serveur local

```bash
cd mobile_web_app
python3 -m http.server 8080
```

Puis ouvrir `http://localhost:8080` sur votre iPhone (même réseau WiFi).

### Option 2: Hébergement gratuit

1. **GitHub Pages**: Push ce dossier sur GitHub et activer Pages
2. **Vercel/Netlify**: Déployer en 1 clic
3. **Cloudflare Pages**: Gratuit avec domaine personnalisé

## Ajouter à l'écran d'accueil (iPhone)

1. Ouvrir la page dans Safari
2. Appuyer sur le bouton "Partager" (carré avec flèche)
3. "Sur l'écran d'accueil"
4. L'app apparaît comme une vraie application!

## Différences avec la version Scriptable

| Fonctionnalité | Web App | Scriptable |
|----------------|---------|------------|
| Code visible par l'utilisateur | ❌ Non (sur serveur) | ✅ Oui |
| Fonctionne hors-ligne | ❌ Non | ✅ Oui |
| Mise à jour | Instantanée (serveur) | Via Gist |
| UX envoi SMS | Clic → Messages → Send | Clic → Messages → Send |
| Protection du code | ✅ Facile (login/auth) | Difficile |

## Ajouter une protection par mot de passe

Pour protéger l'accès, vous pouvez:

1. **Héberger sur un serveur avec authentification** (Vercel + Auth0, etc.)
2. **Ajouter un simple mot de passe côté client** (pas très sécurisé mais suffisant):

```javascript
// Ajouter au début du script
const PASSWORD = 'votre_mot_de_passe';
if (prompt('Mot de passe:') !== PASSWORD) {
    document.body.innerHTML = '<h1>Accès refusé</h1>';
}
```

## Prochaines étapes

- [ ] Ajouter authentification
- [ ] Stocker les CSV/messages en localStorage
- [ ] Mode hors-ligne avec Service Worker
- [ ] Export du rapport d'envoi

# Vinted Bot as SaaS

**Vinted Bot as SaaS** est une plateforme d'automatisation Python qui surveille les annonces Vinted selon des filtres définis par l'utilisateur, snipe automatiquement les articles désirés, et fournit un service multi-tenant basé sur abonnement.

## Table des Matières

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [Variables d'Environnement](#variables-denvironnement)
- [Scripts](#scripts)
- [API Endpoints](#api-endpoints)
- [Améliorations Futures](#améliorations-futures)
- [Contribution](#contribution)
- [Licence](#licence)

## Fonctionnalités

- **Modèle d'abonnement multi-tenant** avec plans de facturation
- **Surveillance en temps réel** des annonces avec filtrage et auto-sniping
- **Backend scalable** avec Python, FastAPI et MySQL
- **Dashboard frontend** (TypeScript/React) pour la gestion des utilisateurs et alertes
- **Authentification JWT** et gestion des rôles
- **Système de facturation** intégré avec Stripe
- **Monitoring des métriques** et usage tracking
- **Gestion des proxies** pour éviter la détection
- **Rate limiting** et protection DDoS
- **Scripts de déploiement** automatisés avec PM2

## Architecture

Une vue d'ensemble complète de l'architecture est décrite dans `architecture-complete.md`. En bref :

### Backend (`/backend`)
- **FastAPI** avec structure modulaire
- **Authentification** (`auth/`) - JWT, gestion des utilisateurs
- **Facturation** (`billing/`) - intégration Stripe, plans d'abonnement
- **Core** (`core/`) - logique métier centrale
- **Modèles** (`models/`) - définitions des entités de base de données
- **Monitoring** (`monitoring/`) - métriques et supervision
- **Routeurs API** (`routers/`) - endpoints REST
- **Scraping** (`scraping/`) - logique de scraping Vinted
- **Tâches** (`tasks/`) - tâches asynchrones et background jobs
- **Usage** (`usage/`) - tracking de l'utilisation par client
- **Utilitaires** (`utils/`) - fonctions communes et rate limiting

### Frontend (`/frontend`)
- **React/TypeScript** avec composants modulaires
- **Pages** : Dashboard, FilterManager, gestion des abonnements
- **Services** : API clients, authentification
- **Composants** : UI réutilisables
- **Intégration Stripe** pour les paiements

### Base de Données (`/database`)
- **Schema initial** (`init.sql`)
- **Migrations versionnées** (`migrations/001_auth_billing.sql`)
- Structure pour auth, billing, monitoring

### Infrastructure
- **NGINX** (`infrastructure/nginx/`) - reverse proxy et SSL
- **PM2** (`pm2/`) - gestionnaire de processus pour la production
- **Scripts** (`scripts/`) - démarrage/arrêt automatisés

## Prérequis

- Python 3.10+
- Node.js 16+ et npm
- MySQL 8.0+ ou compatible
- PM2 (pour la gestion des processus en production)
- NGINX (pour le reverse proxy)

## Installation

### Installation Native

```bash
# Cloner le dépôt
git clone https://github.com/VikingProduction/vinted-bot-as-saas.git
cd vinted-bot-as-saas

# Utiliser le script d'installation native
chmod +x install-native.sh
./install-native.sh
```

### Installation Manuelle

```bash
# Installer les dépendances backend
pip install -r requirements.txt

# Installer les dépendances frontend
cd frontend && npm install

# Copier le template d'environnement
cp env.example .env

# Installer des dépendances dans frontend
npm install @material-ui/core @material-ui/icons
npm install clsx moment react-router-dom
```

## Configuration

### Variables d'Environnement

Renommez `env.example` en `.env` et complétez :

```dotenv
# Base de données MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=vinted_user
DB_PASSWORD=secure_password
DB_NAME=vinted_saas

# Authentification JWT
JWT_SECRET=your_super_secret_jwt_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Credentials Vinted
VINTED_USERNAME=your_vinted_email
VINTED_PASSWORD=your_vinted_password

# Stripe pour la facturation
STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Monitoring
METRICS_ENABLED=true
LOG_LEVEL=INFO
```

### Base de Données

```bash
# Initialiser la base de données
mysql -u root -p < database/init.sql

# Appliquer les migrations
mysql -u root -p vinted_saas < database/migrations/001_auth_billing.sql
```

## Utilisation

### Développement Local

```bash
# Démarrage rapide avec le script
./quick-start.sh
```

### Production avec PM2

```bash
# Démarrer tous les services
cd scripts && ./start.sh

# Arrêter tous les services
cd scripts && ./stop.sh
```

### Démarrage Manuel

```bash
# Backend (depuis le répertoire racine)
cd backend && python -m app.main

# Frontend (depuis le répertoire frontend)
npm run dev
```

## Structure du Projet

```
vinted-bot-as-saas/
├── backend/
│   ├── app/
│   │   ├── auth/                 # Authentification et autorisation
│   │   ├── billing/              # Gestion de la facturation
│   │   ├── core/                 # Logique métier centrale
│   │   ├── models/               # Modèles de données
│   │   ├── monitoring/           # Métriques et monitoring
│   │   ├── routers/              # Routes API
│   │   ├── scraping/             # Logique de scraping Vinted
│   │   ├── tasks/                # Tâches asynchrones
│   │   ├── usage/                # Tracking d'utilisation
│   │   ├── utils/                # Utilitaires communs
│   │   ├── main.py               # Point d'entrée FastAPI
│   │   └── proxy-manager.py      # Gestionnaire de proxies
│   └── Dockerfile                # Containerisation (optionnel)
├── database/
│   ├── migrations/               # Scripts de migration versionnés
│   │   └── 001_auth_billing.sql
│   └── init.sql                  # Schema initial
├── docs/
│   ├── PRIVACY.md                # Politique de confidentialité
│   └── TERMS.md                  # Conditions d'utilisation
├── frontend/
│   ├── src/
│   │   ├── components/           # Composants React réutilisables
│   │   ├── lib/                  # Configurations (Stripe, etc.)
│   │   ├── pages/                # Pages principales
│   │   ├── services/             # Services API
│   │   ├── types/                # Définitions TypeScript
│   │   └── utils/                # Utilitaires frontend
│   └── package.json
├── infrastructure/
│   └── nginx/
│       └── vinted-bot.conf       # Configuration NGINX
├── pm2/
│   └── ecosystem.config.js       # Configuration PM2
├── scripts/
│   ├── start.sh                  # Script de démarrage
│   └── stop.sh                   # Script d'arrêt
├── .gitignore
├── README.md
├── architecture-complete.md      # Documentation architecture détaillée
├── env.example                   # Template variables d'environnement
├── install-native.sh            # Script d'installation système
├── quick-start.sh               # Démarrage rapide développement
└── requirements.txt             # Dépendances Python
```

## API Endpoints

### Authentification
- `POST /auth/register` - Inscription utilisateur
- `POST /auth/login` - Connexion
- `POST /auth/logout` - Déconnexion
- `GET /auth/profile` - Profil utilisateur

### Facturation
- `GET /billing/plans` - Liste des plans d'abonnement
- `POST /billing/subscribe` - Souscrire à un plan
- `GET /billing/subscription` - État de l'abonnement
- `POST /billing/webhook` - Webhook Stripe

### Monitoring
- `GET /monitoring/metrics` - Métriques système
- `GET /monitoring/usage` - Utilisation par utilisateur

### Scraping
- `POST /scraping/filters` - Créer un filtre de recherche
- `GET /scraping/alerts` - Alertes reçues
- `DELETE /scraping/filters/{id}` - Supprimer un filtre

## Scripts

- **`quick-start.sh`** - Démarrage rapide pour le développement
- **`install-native.sh`** - Bootstrap de l'environnement sur VM
- **`scripts/start.sh`** - Démarrage production avec PM2
- **`scripts/stop.sh`** - Arrêt des services PM2

## Améliorations Futures

### Priorité Haute
- [ ] Tests automatisés (pytest, jest)
- [ ] Pipeline CI/CD (GitHub Actions)
- [ ] Documentation API complète (Swagger/OpenAPI)
- [ ] Système de logs centralisé (ELK Stack)

### Priorité Moyenne
- [ ] Dashboard analytics avancé
- [ ] Système de notifications (email, SMS)
- [ ] API publique pour intégrations tierces
- [ ] Interface d'administration

### Priorité Basse
- [ ] Application mobile (React Native)
- [ ] Support multi-plateforme (autres sites)
- [ ] Machine Learning pour prédiction des prix
- [ ] Système de cache Redis

## Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commiter vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

Ce projet est publié sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

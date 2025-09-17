# 📁 Architecture Complète - Bot Vinted SAAS (Installation Native)

## 🏗️ Structure Principale du Projet

```
/opt/vinted-bot-saas/
├── 📋 README-native.md                     # Documentation installation native
├── 🔧 install-native.sh                   # Script d'installation automatique
├── ⚡ quick-start.sh                       # Script de démarrage rapide
├── 🚀 start.sh                            # Script de démarrage
├── 🛑 stop.sh                             # Script d'arrêt
├── 📊 monitor.sh                          # Script de monitoring
├── 💾 backup.sh                           # Script de sauvegarde
├── ⚙️  ecosystem.config.js                # Configuration PM2
├── 🔐 .env                                # Variables d'environnement
├── 📦 requirements.txt                    # Dépendances Python
├── 🐍 venv/                               # Environnement virtuel Python
├── 📝 logs/                               # Logs de l'application
│   ├── api.log
│   ├── api-error.log
│   ├── worker.log
│   ├── nginx-access.log
│   └── nginx-error.log
├── 💾 backups/                            # Sauvegardes automatiques
└── 🔄 temp/                               # Fichiers temporaires
```

## 🐍 Backend Python/FastAPI

```
backend/
├── 📄 requirements.txt                    # Dépendances spécifiques backend
├── 🐳 Dockerfile                          # Pour référence (non utilisé en native)
└── app/
    ├── 🔧 __init__.py
    ├── ⚙️  main.py                         # Application FastAPI principale
    ├── 📊 config.py                       # Configuration centralisée
    ├── 🗄️  database.py                     # Configuration SQLAlchemy + Redis
    │
    ├── 🔐 auth/                           # Authentification & Sécurité
    │   ├── __init__.py
    │   ├── jwt_handler.py                 # Gestion JWT tokens
    │   ├── auth_bearer.py                 # Middleware authentification
    │   └── hash_password.py               # Hashage mots de passe
    │
    ├── 📊 models/                         # Modèles SQLAlchemy
    │   ├── __init__.py
    │   ├── user.py                        # Modèle utilisateur
    │   ├── filter.py                      # Modèle filtres Vinted
    │   ├── alert.py                       # Modèle alertes
    │   ├── subscription.py                # Modèle abonnements Stripe
    │   └── base.py                        # Classes de base
    │
    ├── 🛣️  routers/                        # Routes API
    │   ├── __init__.py
    │   ├── auth.py                        # Routes authentification
    │   ├── users.py                       # Routes utilisateurs
    │   ├── filters.py                     # Routes filtres
    │   ├── alerts.py                      # Routes alertes
    │   ├── subscriptions.py               # Routes abonnements
    │   ├── admin.py                       # Routes administration
    │   └── webhooks.py                    # Webhooks Stripe
    │
    ├── 🕷️  scraping/                       # Moteur de scraping
    │   ├── __init__.py
    │   ├── engine.py                      # Moteur principal
    │   ├── vinted_scraper.py              # Scraper Vinted complet
    │   ├── proxy_manager.py               # Gestionnaire SmartProxy
    │   ├── anti_bot.py                    # Contournement anti-bot
    │   ├── user_agents.py                 # Pool User-Agents
    │   └── captcha_solver.py              # Résolution CAPTCHA
    │
    ├── 🎯 services/                       # Logique métier
    │   ├── __init__.py
    │   ├── user_service.py                # Service utilisateurs
    │   ├── filter_service.py              # Service filtres
    │   ├── alert_service.py               # Service alertes
    │   ├── stripe_service.py              # Service Stripe
    │   ├── notification_service.py        # Service notifications
    │   ├── scraping_service.py            # Service scraping
    │   └── analytics_service.py           # Service analytics
    │
    ├── 🔧 utils/                          # Utilitaires
    │   ├── __init__.py
    │   ├── helpers.py                     # Fonctions utilitaires
    │   ├── validators.py                  # Validateurs Pydantic
    │   ├── exceptions.py                  # Exceptions personnalisées
    │   ├── decorators.py                  # Décorateurs
    │   └── constants.py                   # Constantes
    │
    └── 📋 tasks/                          # Tâches Celery
        ├── __init__.py
        ├── celery_app.py                  # Configuration Celery
        ├── scraping_tasks.py              # Tâches scraping
        ├── notification_tasks.py          # Tâches notifications
        ├── maintenance_tasks.py           # Tâches maintenance
        └── stripe_tasks.py                # Tâches Stripe
```

## 🎨 Frontend React/TypeScript

```
frontend/
├── 📦 package.json                       # Dépendances Node.js
├── 📄 package-lock.json                  # Lock des versions
├── 🔧 tsconfig.json                      # Configuration TypeScript
├── 🎨 tailwind.config.js                 # Configuration Tailwind CSS
├── 📄 postcss.config.js                  # Configuration PostCSS
├── 🐳 Dockerfile                         # Pour référence (non utilisé)
├── 🌐 public/                            # Fichiers statiques
│   ├── index.html
│   ├── favicon.ico
│   ├── manifest.json
│   ├── logo192.png
│   └── logo512.png
├── 🏗️  build/                             # Build de production (généré)
└── src/
    ├── 🎯 index.tsx                       # Point d'entrée React
    ├── 📱 App.tsx                         # Composant principal
    ├── 🎨 index.css                       # Styles globaux
    ├── 🔧 setupTests.ts                   # Configuration tests
    │
    ├── 🧩 components/                     # Composants réutilisables
    │   ├── ui/                            # Composants UI de base
    │   │   ├── Button.tsx
    │   │   ├── Input.tsx
    │   │   ├── Modal.tsx
    │   │   ├── Card.tsx
    │   │   ├── Badge.tsx
    │   │   ├── Spinner.tsx
    │   │   └── Toast.tsx
    │   ├── layout/                        # Composants de layout
    │   │   ├── Navbar.tsx
    │   │   ├── Sidebar.tsx
    │   │   ├── Footer.tsx
    │   │   └── Layout.tsx
    │   ├── forms/                         # Composants de formulaires
    │   │   ├── FilterForm.tsx
    │   │   ├── LoginForm.tsx
    │   │   ├── RegisterForm.tsx
    │   │   └── ProfileForm.tsx
    │   ├── dashboard/                     # Composants dashboard
    │   │   ├── Dashboard.tsx
    │   │   ├── StatsCard.tsx
    │   │   ├── AlertsList.tsx
    │   │   ├── FiltersList.tsx
    │   │   └── RecentActivity.tsx
    │   ├── subscription/                  # Composants abonnements
    │   │   ├── SubscriptionPlans.tsx
    │   │   ├── PricingCard.tsx
    │   │   ├── BillingHistory.tsx
    │   │   └── PaymentForm.tsx
    │   └── alerts/                        # Composants alertes
    │       ├── AlertCard.tsx
    │       ├── AlertFilters.tsx
    │       └── AlertSettings.tsx
    │
    ├── 📄 pages/                          # Pages principales
    │   ├── auth/                          # Pages authentification
    │   │   ├── Login.tsx
    │   │   ├── Register.tsx
    │   │   ├── ForgotPassword.tsx
    │   │   └── ResetPassword.tsx
    │   ├── dashboard/                     # Pages dashboard
    │   │   ├── Dashboard.tsx
    │   │   ├── Analytics.tsx
    │   │   └── Settings.tsx
    │   ├── filters/                       # Pages filtres
    │   │   ├── FiltersList.tsx
    │   │   ├── CreateFilter.tsx
    │   │   └── EditFilter.tsx
    │   ├── alerts/                        # Pages alertes
    │   │   ├── AlertsHistory.tsx
    │   │   └── AlertsSettings.tsx
    │   ├── subscription/                  # Pages abonnements
    │   │   ├── Plans.tsx
    │   │   ├── Billing.tsx
    │   │   └── Usage.tsx
    │   ├── account/                       # Pages compte
    │   │   ├── Profile.tsx
    │   │   ├── Security.tsx
    │   │   └── Preferences.tsx
    │   └── public/                        # Pages publiques
    │       ├── Home.tsx
    │       ├── Pricing.tsx
    │       ├── About.tsx
    │       └── Contact.tsx
    │
    ├── 🔌 services/                       # Services API
    │   ├── api.ts                         # Configuration Axios
    │   ├── auth.ts                        # Service authentification
    │   ├── users.ts                       # Service utilisateurs
    │   ├── filters.ts                     # Service filtres
    │   ├── alerts.ts                      # Service alertes
    │   ├── subscriptions.ts               # Service abonnements
    │   └── websocket.ts                   # Service WebSocket
    │
    ├── 🏪 store/                          # État global (Redux)
    │   ├── index.ts                       # Configuration store
    │   ├── slices/                        # Redux slices
    │   │   ├── authSlice.ts
    │   │   ├── userSlice.ts
    │   │   ├── filtersSlice.ts
    │   │   ├── alertsSlice.ts
    │   │   └── subscriptionSlice.ts
    │   └── middleware/                    # Middleware Redux
    │       ├── apiMiddleware.ts
    │       └── loggerMiddleware.ts
    │
    ├── 🪝 hooks/                          # Hooks personnalisés
    │   ├── useAuth.ts                     # Hook authentification
    │   ├── useApi.ts                      # Hook API calls
    │   ├── useWebSocket.ts                # Hook WebSocket
    │   ├── useLocalStorage.ts             # Hook localStorage
    │   └── useDebounce.ts                 # Hook debounce
    │
    ├── 🔧 utils/                          # Utilitaires frontend
    │   ├── helpers.ts                     # Fonctions utilitaires
    │   ├── validators.ts                  # Validateurs
    │   ├── formatters.ts                  # Formatage données
    │   ├── constants.ts                   # Constantes
    │   └── types.ts                       # Types TypeScript
    │
    └── 🎨 assets/                         # Assets statiques
        ├── images/
        ├── icons/
        └── styles/
```

## 🗄️ Base de Données

```
database/
├── 📄 init.sql                           # Schéma initial complet
├── 🔄 migrations/                        # Migrations Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_indexes.py
│       ├── 003_add_subscription_fields.py
│       └── 004_add_analytics_tables.py
├── 🌱 seeds/                             # Données de test
│   ├── users_seed.sql
│   ├── plans_seed.sql
│   └── demo_data.sql
└── 📊 backups/                           # Sauvegardes automatiques
    ├── daily/
    ├── weekly/
    └── monthly/
```

## 🌐 Configuration Nginx

```
nginx/
├── 📄 nginx.conf                         # Configuration principale
├── 🔐 ssl/                               # Certificats SSL
│   ├── cert.pem
│   └── key.pem
├── 📂 sites-available/                   # Sites disponibles
│   └── vinted-bot
├── 📂 sites-enabled/                     # Sites activés
│   └── vinted-bot -> ../sites-available/vinted-bot
├── 📊 logs/                              # Logs Nginx
│   ├── access.log
│   └── error.log
└── 🎭 html/                              # Pages d'erreur personnalisées
    ├── 404.html
    ├── 50x.html
    └── maintenance.html
```

## 📊 Monitoring & Analytics

```
monitoring/
├── 📄 prometheus.yml                     # Configuration Prometheus
├── 📊 grafana/                           # Dashboards Grafana
│   ├── dashboards/
│   │   ├── api-performance.json
│   │   ├── scraping-metrics.json
│   │   ├── user-activity.json
│   │   └── system-resources.json
│   └── provisioning/
├── 📈 alertmanager/                      # Configuration alertes
│   └── alertmanager.yml
└── 📋 scripts/                           # Scripts monitoring
    ├── check-health.sh
    ├── alert-webhook.sh
    └── metrics-export.sh
```

## 📚 Documentation

```
docs/
├── 📋 README.md                          # Documentation générale
├── 🚀 installation.md                    # Guide d'installation
├── ⚙️  configuration.md                  # Guide de configuration
├── 🔧 development.md                     # Guide développement
├── 🚀 deployment.md                      # Guide déploiement
├── 📊 api.md                             # Documentation API
├── 🔐 security.md                        # Guide sécurité
├── 🐛 troubleshooting.md                 # Guide dépannage
├── 📄 user-guide.md                      # Guide utilisateur
├── 💰 business-model.md                  # Modèle économique
├── ⚖️  legal.md                          # Aspects légaux
├── 📊 analytics/                         # Analyses de marché
│   ├── architecture.json
│   ├── subscription_plans.csv
│   ├── smartproxy_analysis.json
│   ├── cost_scenarios.csv
│   └── nordvpn_comparison.csv
├── 🖼️  images/                            # Images documentation
├── 📐 diagrams/                          # Diagrammes architecture
└── 🔄 changelog.md                       # Journal des modifications
```

## 🧪 Tests

```
tests/
├── 🐍 backend/                           # Tests backend
│   ├── conftest.py                       # Configuration pytest
│   ├── test_auth.py                      # Tests authentification
│   ├── test_users.py                     # Tests utilisateurs
│   ├── test_filters.py                   # Tests filtres
│   ├── test_alerts.py                    # Tests alertes
│   ├── test_scraping.py                  # Tests scraping
│   ├── test_stripe.py                    # Tests Stripe
│   └── fixtures/                         # Données de test
├── 🎨 frontend/                          # Tests frontend
│   ├── components/                       # Tests composants
│   ├── pages/                            # Tests pages
│   ├── services/                         # Tests services
│   ├── hooks/                            # Tests hooks
│   └── utils/                            # Tests utilitaires
├── 🚀 e2e/                               # Tests end-to-end
│   ├── cypress.json
│   ├── integration/
│   └── fixtures/
└── 📊 performance/                       # Tests de performance
    ├── load-testing.js
    └── stress-testing.js
```

## 🔧 Scripts & Outils

```
scripts/
├── 🚀 install-native.sh                  # Installation automatique
├── ⚡ quick-start.sh                     # Démarrage rapide
├── 🚀 start.sh                           # Démarrage services
├── 🛑 stop.sh                            # Arrêt services
├── 🔄 restart.sh                         # Redémarrage services
├── 📊 monitor.sh                         # Monitoring
├── 💾 backup.sh                          # Sauvegarde
├── 🔄 restore.sh                         # Restauration
├── 🧹 cleanup.sh                         # Nettoyage
├── 🚀 deploy.sh                          # Déploiement
├── 🔄 update.sh                          # Mise à jour
├── 🐛 debug.sh                           # Débogage
├── 🔧 maintenance.sh                     # Maintenance
└── 📊 stats.sh                           # Statistiques
```

## 🎯 Configuration Services

```
config/
├── 📄 ecosystem.config.js                # Configuration PM2
├── 🔐 .env                               # Variables environnement
├── 📄 .env.example                       # Exemple configuration
├── 🔧 systemd/                           # Services systemd (optionnel)
│   ├── vinted-bot-api.service
│   ├── vinted-bot-worker.service
│   └── vinted-bot-scheduler.service
├── 📊 logrotate/                         # Configuration logrotate
│   └── vinted-bot
├── 🔐 ssl/                               # Certificats SSL
└── 🔒 secrets/                           # Secrets (non versionnés)
    ├── jwt-secret.txt
    ├── stripe-webhook-secret.txt
    └── smartproxy-credentials.txt
```

## 📦 Packages & Dépendances

```
packages/
├── 🐍 python/                           # Packages Python custom
├── 📦 node/                             # Packages Node custom
└── 🔧 shared/                           # Utilitaires partagés
```

## 🔄 Environnements

```
environments/
├── 🧪 development/                      # Config développement
│   ├── .env.dev
│   ├── docker-compose.dev.yml
│   └── ecosystem.dev.js
├── 🧪 staging/                          # Config staging
│   ├── .env.staging
│   └── ecosystem.staging.js
└── 🚀 production/                       # Config production
    ├── .env.prod
    ├── ecosystem.prod.js
    └── backup-config.json
```

## 📊 Fichiers de Données

```
data/
├── 📊 exports/                          # Exports de données
├── 📈 reports/                          # Rapports générés
├── 🔄 imports/                          # Imports de données
├── 📂 cache/                            # Cache applicatif
└── 🗂️  temp/                            # Fichiers temporaires
```

---

## 📋 **Résumé Architecture**

### **🔢 Statistiques du Projet**
- **Dossiers principaux** : 15+
- **Sous-dossiers** : 60+
- **Fichiers de code** : 200+
- **Scripts utilitaires** : 15+
- **Fichiers de configuration** : 25+

### **🚀 Points Clés**
- ✅ **Architecture modulaire** parfaitement organisée
- ✅ **Séparation claire** backend/frontend/database
- ✅ **Scripts d'automatisation** complets
- ✅ **Monitoring intégré** avec PM2 + Nginx
- ✅ **Configuration production-ready**
- ✅ **Tests et documentation** inclus
- ✅ **Scalabilité** et **maintenance** simplifiées

Cette architecture vous donne une **base solide professionnelle** pour développer, déployer et maintenir votre bot Vinted SAAS ! 🎯
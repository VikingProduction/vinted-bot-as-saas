# Bot Vinted SAAS - Installation Native (Sans Docker)

🤖 **Bot Vinted automatisé avec alertes et snipping en mode SAAS**

## 📋 Description

Plateforme SAAS complète permettant aux utilisateurs de:
- **Surveiller Vinted** avec des filtres personnalisés avancés
- **Recevoir des alertes** instantanées sur les nouveaux articles
- **Acheter automatiquement** (snipping) les bonnes affaires
- **Gérer plusieurs filtres** simultanément
- **Analytics détaillées** sur les performances

## 🏗️ Architecture Native

### Stack Technique
- **Backend**: FastAPI + Python 3.11+
- **Base de données**: MySQL 8.0 + Redis
- **Frontend**: React + TypeScript + Tailwind CSS
- **Scraping**: httpx + Playwright + SmartProxy
- **Paiements**: Stripe
- **Process Manager**: PM2 ou systemd

## 🚀 Installation Native Complète

### Prérequis Système
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm mysql-server redis-server nginx

# CentOS/RHEL
sudo yum install -y python3.11 nodejs npm mysql-server redis nginx

# macOS
brew install python@3.11 node mysql redis nginx
```

### 1. Configuration Base de Données MySQL

```bash
# Démarrer MySQL
sudo systemctl start mysql
sudo systemctl enable mysql

# Sécuriser MySQL
sudo mysql_secure_installation

# Créer base de données et utilisateur
sudo mysql -u root -p
```

```sql
CREATE DATABASE vinted_bot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'vinted_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON vinted_bot.* TO 'vinted_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

```bash
# Importer le schéma
mysql -u vinted_user -p vinted_bot < database/init.sql
```

### 2. Configuration Redis

```bash
# Démarrer Redis
sudo systemctl start redis
sudo systemctl enable redis

# Test connexion
redis-cli ping
# Doit retourner PONG
```

### 3. Backend Python/FastAPI

```bash
# Créer répertoire projet
mkdir -p /opt/vinted-bot-saas
cd /opt/vinted-bot-saas

# Environnement virtuel Python
python3.11 -m venv venv
source venv/bin/activate

# Installation dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Installation Playwright navigateurs
playwright install chromium
playwright install-deps
```

#### Structure Backend
```bash
mkdir -p backend/app/{auth,models,routers,scraping,services,utils,tasks}
touch backend/app/__init__.py
touch backend/app/{auth,models,routers,scraping,services,utils,tasks}/__init__.py
```

#### Configuration Environnement
```bash
# Copier configuration
cp .env.example .env

# Éditer avec vos paramètres
nano .env
```

```env
# Configuration pour installation native
DATABASE_URL=mysql://vinted_user:your_secure_password@localhost:3306/vinted_bot
REDIS_URL=redis://localhost:6379/0

# SmartProxy
SMARTPROXY_USERNAME=your_username
SMARTPROXY_PASSWORD=your_password

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_key

# JWT
JWT_SECRET_KEY=your_super_secret_key_change_in_production

# Logs
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=production
```

### 4. Frontend React/TypeScript

```bash
# Installation Node.js et npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Créer app React
cd /opt/vinted-bot-saas
npx create-react-app frontend --template typescript
cd frontend

# Installation dépendances additionnelles
npm install axios react-router-dom @tanstack/react-query react-hook-form
npm install -D tailwindcss postcss autoprefixer @types/node

# Configuration Tailwind
npx tailwindcss init -p
```

### 5. Gestion des Processus avec PM2

```bash
# Installation PM2 globalement
sudo npm install -g pm2

# Configuration PM2 pour le backend
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'vinted-bot-api',
      script: 'venv/bin/uvicorn',
      args: 'backend.app.main:app --host 0.0.0.0 --port 8000',
      cwd: '/opt/vinted-bot-saas',
      instances: 2,
      exec_mode: 'cluster',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '/opt/vinted-bot-saas'
      },
      error_file: '/var/log/vinted-bot/api-error.log',
      out_file: '/var/log/vinted-bot/api-out.log',
      log_file: '/var/log/vinted-bot/api.log'
    },
    {
      name: 'vinted-bot-worker',
      script: 'venv/bin/celery',
      args: '-A backend.app.tasks.celery_app worker --loglevel=info --concurrency=4',
      cwd: '/opt/vinted-bot-saas',
      instances: 1,
      env: {
        PYTHONPATH: '/opt/vinted-bot-saas'
      },
      error_file: '/var/log/vinted-bot/worker-error.log',
      out_file: '/var/log/vinted-bot/worker-out.log',
      log_file: '/var/log/vinted-bot/worker.log'
    },
    {
      name: 'vinted-bot-scheduler',
      script: 'venv/bin/celery',
      args: '-A backend.app.tasks.celery_app beat --loglevel=info',
      cwd: '/opt/vinted-bot-saas',
      instances: 1,
      env: {
        PYTHONPATH: '/opt/vinted-bot-saas'
      }
    },
    {
      name: 'vinted-bot-frontend',
      script: 'npm',
      args: 'start',
      cwd: '/opt/vinted-bot-saas/frontend',
      instances: 1,
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        REACT_APP_API_URL: 'http://localhost:8000'
      }
    }
  ]
};
EOF

# Créer répertoire logs
sudo mkdir -p /var/log/vinted-bot
sudo chown $USER:$USER /var/log/vinted-bot

# Démarrer tous les services
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### 6. Configuration Nginx

```bash
# Configuration Nginx
sudo tee /etc/nginx/sites-available/vinted-bot << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # Frontend React
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        if ($request_method = OPTIONS) {
            return 204;
        }
    }

    # WebSocket pour notifications temps réel
    location /ws {
        proxy_pass http://localhost:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Monitoring Celery Flower (optionnel)
    location /flower/ {
        proxy_pass http://localhost:5555/;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # Sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
}
EOF

# Activer le site
sudo ln -s /etc/nginx/sites-available/vinted-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. SSL avec Let's Encrypt (Production)

```bash
# Installation Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenir certificat SSL
sudo certbot --nginx -d your-domain.com

# Auto-renouvellement
sudo crontab -e
# Ajouter: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 8. Scripts de Gestion

#### Script de Démarrage
```bash
cat > start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Démarrage Vinted Bot SAAS..."

# Vérification services système
sudo systemctl start mysql redis nginx
sleep 2

# Activation environnement Python
source venv/bin/activate

# Démarrage avec PM2
pm2 start ecosystem.config.js

# Vérification santé
sleep 5
curl -f http://localhost:8000/health || {
    echo "❌ API non accessible"
    exit 1
}

echo "✅ Tous les services sont démarrés"
pm2 status
EOF

chmod +x start.sh
```

#### Script d'Arrêt
```bash
cat > stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Arrêt Vinted Bot SAAS..."

# Arrêt PM2
pm2 stop all

# Arrêt services (optionnel)
# sudo systemctl stop nginx redis mysql

echo "✅ Services arrêtés"
EOF

chmod +x stop.sh
```

#### Script de Maintenance
```bash
cat > maintenance.sh << 'EOF'
#!/bin/bash
echo "🔧 Maintenance Vinted Bot SAAS..."

# Sauvegarde base de données
mysqldump -u vinted_user -p vinted_bot > "backup_$(date +%Y%m%d_%H%M%S).sql"

# Nettoyage logs
pm2 flush

# Rotation logs système
sudo logrotate -f /etc/logrotate.conf

# Mise à jour dépendances (avec précaution)
source venv/bin/activate
pip list --outdated

echo "✅ Maintenance terminée"
EOF

chmod +x maintenance.sh
```

### 9. Monitoring et Logs

#### Configuration Logrotate
```bash
sudo tee /etc/logrotate.d/vinted-bot << 'EOF'
/var/log/vinted-bot/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 your-user your-group
    postrotate
        pm2 reload all > /dev/null 2>&1 || true
    endscript
}
EOF
```

#### Script de Monitoring
```bash
cat > monitor.sh << 'EOF'
#!/bin/bash

# Vérification services
check_service() {
    local service=$1
    local port=$2
    
    if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $service: OK"
    else
        echo "❌ $service: FAIL"
        pm2 restart $service
    fi
}

check_service "vinted-bot-api" 8000
check_service "vinted-bot-frontend" 3000

# Vérification base de données
mysql -u vinted_user -p -e "SELECT 1" vinted_bot > /dev/null 2>&1 && \
echo "✅ MySQL: OK" || echo "❌ MySQL: FAIL"

# Vérification Redis
redis-cli ping > /dev/null 2>&1 && \
echo "✅ Redis: OK" || echo "❌ Redis: FAIL"

# Statistiques PM2
echo "📊 Status PM2:"
pm2 jlist | jq -r '.[] | "\(.name): \(.pm2_env.status)"'
EOF

chmod +x monitor.sh

# Ajouter à crontab pour vérification périodique
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/vinted-bot-saas/monitor.sh >> /var/log/vinted-bot/monitor.log 2>&1") | crontab -
```

### 10. Service Systemd (Alternative à PM2)

```bash
# Si vous préférez systemd à PM2
sudo tee /etc/systemd/system/vinted-bot-api.service << 'EOF'
[Unit]
Description=Vinted Bot API
After=network.target mysql.service redis.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/vinted-bot-saas
Environment=PYTHONPATH=/opt/vinted-bot-saas
ExecStart=/opt/vinted-bot-saas/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Services pour Celery
sudo tee /etc/systemd/system/vinted-bot-worker.service << 'EOF'
[Unit]
Description=Vinted Bot Celery Worker
After=network.target redis.service

[Service]
Type=simple
User=your-user
WorkingDirectory=/opt/vinted-bot-saas
Environment=PYTHONPATH=/opt/vinted-bot-saas
ExecStart=/opt/vinted-bot-saas/venv/bin/celery -A backend.app.tasks.celery_app worker --loglevel=info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Activer les services
sudo systemctl daemon-reload
sudo systemctl enable vinted-bot-api vinted-bot-worker
sudo systemctl start vinted-bot-api vinted-bot-worker
```

## 🔧 Développement Local

### Mode Développement
```bash
# Backend en mode debug
source venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend en mode développement
cd frontend
npm start

# Worker Celery
celery -A backend.app.tasks.celery_app worker --loglevel=info --reload
```

### Tests
```bash
# Tests backend
pytest backend/tests/

# Tests frontend
cd frontend
npm test
```

## 📊 Performance et Optimisation

### Base de Données
```sql
-- Optimisations MySQL
SET GLOBAL innodb_buffer_pool_size = 2G;
SET GLOBAL query_cache_size = 256M;
SET GLOBAL max_connections = 200;

-- Index de performance
CREATE INDEX idx_alerts_recent ON alerts (created_at DESC, user_id);
CREATE INDEX idx_filters_active ON vinted_filters (is_active, user_id, last_check);
```

### Redis Configuration
```bash
# /etc/redis/redis.conf
maxmemory 1gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## 🎯 Avantages Installation Native

### ✅ **Avantages**
- **Performance maximale** : Pas d'overhead Docker
- **Contrôle total** : Configuration fine de chaque composant
- **Débogage facile** : Accès direct aux logs et processus
- **Ressources optimisées** : Utilisation native des ressources système
- **Intégration OS** : Services systemd, logrotate, crontab

### ⚠️ **Inconvénients**
- **Complexité setup** : Plus de configuration manuelle
- **Dépendances système** : Gestion versions OS
- **Portabilité réduite** : Configuration spécifique à l'environnement
- **Backup complexe** : Sauvegarde de multiples composants

## 📋 Checklist de Déploiement

- [ ] Services système installés (MySQL, Redis, Nginx)
- [ ] Base de données créée et configurée
- [ ] Environnement Python configuré
- [ ] Dépendances installées
- [ ] Configuration .env complète
- [ ] PM2 ou systemd configuré
- [ ] Nginx configuré et testé
- [ ] SSL configuré (production)
- [ ] Monitoring actif
- [ ] Sauvegardes programmées
- [ ] Tests de santé fonctionnels

## 🚀 Lancement Final

```bash
# Démarrage complet
./start.sh

# Vérification
curl http://localhost:8000/health
curl http://localhost:3000

# Monitoring
./monitor.sh
pm2 monit
```

Votre bot Vinted SAAS est maintenant prêt en installation native ! 🎉
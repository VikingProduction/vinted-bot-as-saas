#!/bin/bash
set -e

echo "🚀 Installation Native Vinted Bot SAAS"
echo "======================================"

# Variables de configuration
PROJECT_DIR="/opt/vinted-bot-saas"
DB_NAME="vinted_bot"
DB_USER="vinted_user"
DB_PASS="$(openssl rand -base64 32)"
PYTHON_VERSION="3.11"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "\n${GREEN}📋 $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier les privilèges sudo
if [ "$EUID" -eq 0 ]; then
    print_error "Ne pas exécuter ce script en tant que root. Utilisez sudo quand nécessaire."
    exit 1
fi

# Détecter l'OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            # Vérifier si c'est Debian 12
            DEBIAN_VERSION=$(cat /etc/debian_version)
            if [[ $DEBIAN_VERSION == *"12"* ]] || [[ $DEBIAN_VERSION == *"bookworm"* ]]; then
                echo "Debian 12 (Bookworm) détecté"
            fi
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        print_error "OS non supporté: $OSTYPE"
        exit 1
    fi
}


# Installation des prérequis système
install_system_deps() {
    print_step "Installation des dépendances système"
    
    case $OS in
        "debian")
            sudo apt update
            sudo apt install -y \
                python${PYTHON_VERSION} \
                python${PYTHON_VERSION}-venv \
                python3-pip \
                nodejs \
                mariadb-server \
                mariadb-client \
                libmariadb-dev \
                redis-server \
                nginx \
                git \
                curl \
                wget \
                unzip \
                build-essential \
                pkg-config \
            ;;
        "redhat")
            sudo yum update -y
            sudo yum install -y \
                python${PYTHON_VERSION} \
                python3-pip \
                nodejs \
                npm \
                mysql-server \
                redis \
                nginx \
                git \
                curl \
                wget \
                unzip \
                gcc \
                gcc-c++ \
                mysql-devel
            ;;
        "macos")
            # Vérifier Homebrew
            if ! command -v brew &> /dev/null; then
                print_warning "Homebrew n'est pas installé. Installation..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew install python@${PYTHON_VERSION} node mysql redis nginx git
            ;;
    esac
}

# Configuration MySQL
setup_mysql() {
    print_step "Configuration MySQL"
    
    # Démarrer MySQL
    case $OS in
        "debian"|"redhat")
            sudo systemctl start mariadb
            sudo systemctl enable mariadb   
            ;;
        "macos")
            brew services start mysql
            ;;
    esac
    
    # Attendre que MySQL soit prêt
    sleep 5
    
    # Créer la base de données et l'utilisateur
    sudo mariadb << EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
    
    echo -e "${GREEN}✅ MySQL configuré${NC}"
    echo "Base: $DB_NAME, User: $DB_USER, Pass: $DB_PASS"
}

# Configuration Redis
setup_redis() {
    print_step "Configuration Redis"
    
    case $OS in
        "debian"|"redhat")
            sudo systemctl start redis-server
            sudo systemctl enable redis-server
            ;;
        "macos")
            brew services start redis
            ;;
    esac
    
    # Test connexion
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis configuré et fonctionnel${NC}"
    else
        print_error "Échec configuration Redis"
        exit 1
    fi
}

# Créer répertoire projet
setup_project_dir() {
    print_step "Création du répertoire projet"
    
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    cd $PROJECT_DIR
    
    # Structure des dossiers
    mkdir -p {backend/{app/{auth,models,routers,scraping,services,utils,tasks}},frontend,database,logs,scripts}
    touch backend/app/__init__.py
    touch backend/app/{auth,models,routers,scraping,services,utils,tasks}/__init__.py
}

# Configuration Python et environnement virtuel
setup_python_env() {
    print_step "Configuration environnement Python"
    
    cd $PROJECT_DIR
    
    # Créer environnement virtuel
    python${PYTHON_VERSION} -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Créer requirements.txt si pas présent
    if [ ! -f requirements.txt ]; then
        cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
alembic==1.12.1
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.2
aiofiles==23.2.1
playwright==1.40.0
beautifulsoup4==4.12.2
lxml==4.9.3
fake-useragent==1.4.0
celery[redis]==5.3.4
stripe==7.8.0
sendgrid==6.10.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
structlog==23.2.0
pytest==7.4.3
pytest-asyncio==0.21.1
EOF
    fi
    
    # Installer dépendances
    pip install -r requirements.txt
    
    # Installer Playwright
    playwright install chromium
    playwright install-deps
    
    echo -e "${GREEN}✅ Environnement Python configuré${NC}"
}

# Configuration Node.js et Frontend
setup_frontend() {
    print_step "Configuration Frontend React"
    
    cd $PROJECT_DIR
    
    # Vérifier version Node
    if ! node --version | grep -q "v1[8-9]\|v[2-9]"; then
        print_warning "Version Node.js trop ancienne. Mise à jour recommandée."
    fi
    
    # Créer package.json si pas présent
    if [ ! -f frontend/package.json ]; then
        mkdir -p frontend/src/{components,pages,services,utils}
        cd frontend
        
        cat > package.json << 'EOF'
{
  "name": "vinted-bot-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "typescript": "^4.9.5",
    "react-router-dom": "^6.20.1",
    "axios": "^1.6.2",
    "@tanstack/react-query": "^5.8.4",
    "react-hook-form": "^7.48.2",
    "@hookform/resolvers": "^3.3.2",
    "yup": "^1.3.3",
    "react-hot-toast": "^2.4.1",
    "lucide-react": "^0.294.0",
    "date-fns": "^2.30.0",
    "clsx": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.42",
    "@types/react-dom": "^18.2.17",
    "@types/node": "^16.18.68",
    "tailwindcss": "^3.3.6",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "@tailwindcss/forms": "^0.5.7"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "proxy": "http://localhost:8000"
}
EOF
        
        # Configuration TypeScript
        cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src"
  ]
}
EOF
        
        # Configuration Tailwind
        cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
EOF
        
        npm install
        cd ..
    fi
    
    echo -e "${GREEN}✅ Frontend configuré${NC}"
}

# Installation PM2
install_pm2() {
    print_step "Installation PM2"
    
    sudo npm install -g pm2
    
    # Configuration PM2
    cat > $PROJECT_DIR/ecosystem.config.js << EOF
module.exports = {
  apps: [
    {
      name: 'vinted-bot-api',
      script: 'venv/bin/uvicorn',
      args: 'backend.app.main:app --host 0.0.0.0 --port 8000',
      cwd: '$PROJECT_DIR',
      instances: 1,
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: '$PROJECT_DIR'
      },
      error_file: '$PROJECT_DIR/logs/api-error.log',
      out_file: '$PROJECT_DIR/logs/api-out.log',
      log_file: '$PROJECT_DIR/logs/api.log'
    },
    {
      name: 'vinted-bot-worker',
      script: 'venv/bin/celery',
      args: '-A backend.app.tasks.celery_app worker --loglevel=info --concurrency=2',
      cwd: '$PROJECT_DIR',
      instances: 1,
      env: {
        PYTHONPATH: '$PROJECT_DIR'
      },
      error_file: '$PROJECT_DIR/logs/worker-error.log',
      out_file: '$PROJECT_DIR/logs/worker-out.log'
    },
    {
      name: 'vinted-bot-scheduler',
      script: 'venv/bin/celery',
      args: '-A backend.app.tasks.celery_app beat --loglevel=info',
      cwd: '$PROJECT_DIR',
      instances: 1,
      env: {
        PYTHONPATH: '$PROJECT_DIR'
      }
    }
  ]
};
EOF
    
    echo -e "${GREEN}✅ PM2 installé et configuré${NC}"
}

# Configuration Nginx
setup_nginx() {
    print_step "Configuration Nginx"
    
    # Configuration de base
    sudo tee /etc/nginx/sites-available/vinted-bot << EOF
server {
    listen 80;
    server_name localhost;

    client_max_body_size 10M;

    # Frontend React (build)
    location / {
        root $PROJECT_DIR/frontend/build;
        index index.html;
        try_files \$uri \$uri/ /index.html;
        
        # Headers de sécurité
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
    }

    # API Backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Documentation API (développement)
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host \$host;
    }
    
    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_set_header Host \$host;
    }

    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }

    # Logs
    access_log $PROJECT_DIR/logs/nginx-access.log;
    error_log $PROJECT_DIR/logs/nginx-error.log;
}
EOF

    # Activer le site
    sudo ln -sf /etc/nginx/sites-available/vinted-bot /etc/nginx/sites-enabled/
    
    # Désactiver site par défaut
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test configuration
    sudo nginx -t
    
    # Redémarrer Nginx
    case $OS in
        "debian"|"redhat")
            sudo systemctl restart nginx
            sudo systemctl enable nginx
            ;;
        "macos")
            brew services restart nginx
            ;;
    esac
    
    echo -e "${GREEN}✅ Nginx configuré${NC}"
}

# Créer fichier de configuration .env
create_env_file() {
    print_step "Création fichier de configuration"
    
    cat > $PROJECT_DIR/.env << EOF
# Configuration Base de données
DATABASE_URL=mysql://${DB_USER}:${DB_PASS}@localhost:3306/${DB_NAME}
REDIS_URL=redis://localhost:6379/0

# SmartProxy Configuration (À COMPLÉTER)
SMARTPROXY_USERNAME=your_smartproxy_username
SMARTPROXY_PASSWORD=your_smartproxy_password
SMARTPROXY_ENDPOINT=gate.smartproxy.com:7000

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Stripe Configuration (À COMPLÉTER)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email Configuration (Optionnel)
SENDGRID_API_KEY=
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost", "http://localhost:3000", "http://localhost:80"]

# Scraping
SCRAPING_DELAY_MIN=2
SCRAPING_DELAY_MAX=5
MAX_CONCURRENT_SCRAPERS=5
EOF

    echo -e "${GREEN}✅ Fichier .env créé${NC}"
    echo -e "${YELLOW}⚠️  N'oubliez pas de compléter les clés SmartProxy et Stripe dans .env${NC}"
}

# Scripts utilitaires
create_utility_scripts() {
    print_step "Création des scripts utilitaires"
    
    # Script de démarrage
    cat > $PROJECT_DIR/start.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Démarrage Vinted Bot SAAS..."

cd /opt/vinted-bot-saas

# Activation environnement Python
source venv/bin/activate

# Démarrage avec PM2
pm2 start ecosystem.config.js

# Vérification santé
sleep 5
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API accessible"
else
    echo "❌ API non accessible"
    pm2 logs vinted-bot-api --lines 20
    exit 1
fi

echo "✅ Tous les services sont démarrés"
pm2 status
EOF

    # Script d'arrêt
    cat > $PROJECT_DIR/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Arrêt Vinted Bot SAAS..."

pm2 stop all
pm2 kill

echo "✅ Services arrêtés"
EOF

    # Script de monitoring
    cat > $PROJECT_DIR/monitor.sh << 'EOF'
#!/bin/bash

echo "📊 Status des services Vinted Bot"
echo "================================="

# PM2 Status
echo "PM2 Processes:"
pm2 jlist | python3 -c "
import json, sys
data = json.load(sys.stdin)
for app in data:
    name = app['name']
    status = app['pm2_env']['status']
    cpu = app['monit']['cpu']
    memory = round(app['monit']['memory'] / 1024 / 1024, 1)
    print(f'{name}: {status} (CPU: {cpu}%, RAM: {memory}MB)')
"

echo -e "\nServices Système:"

# MySQL
if systemctl is-active --quiet mariadb; then
    echo "✅ MariaDB: Actif"
else
    echo "❌ MariaDB: Inactif"
fi

# Redis
if systemctl is-active --quiet redis-server; then
    echo "✅ Redis: Actif"
else
    echo "❌ Redis: Inactif"
fi

# Nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: Actif"
else
    echo "❌ Nginx: Inactif"
fi

echo -e "\nEndpoints:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "❌ API non accessible"
EOF

    # Script de sauvegarde
    cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/vinted-bot-saas/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "💾 Sauvegarde base de données..."
mysqldump -u vinted_user -p vinted_bot > "$BACKUP_DIR/vinted_bot_$DATE.sql"

echo "💾 Sauvegarde configuration..."
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env ecosystem.config.js

echo "✅ Sauvegarde terminée: $BACKUP_DIR"
ls -la $BACKUP_DIR/*$DATE*
EOF

    # Rendre les scripts exécutables
    chmod +x $PROJECT_DIR/{start.sh,stop.sh,monitor.sh,backup.sh}
    
    echo -e "${GREEN}✅ Scripts utilitaires créés${NC}"
}

# Importer le schéma de base de données
import_database_schema() {
    print_step "Import du schéma de base de données"
    
    if [ -f $PROJECT_DIR/database/init.sql ]; then
        mysql -u $DB_USER -p$DB_PASS $DB_NAME < $PROJECT_DIR/database/init.sql
        echo -e "${GREEN}✅ Schéma de base de données importé${NC}"
    else
        print_warning "Fichier database/init.sql non trouvé. Créez-le manuellement."
    fi
}

# Configuration des logs
setup_logging() {
    print_step "Configuration du logging"
    
    # Logrotate
    sudo tee /etc/logrotate.d/vinted-bot << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
    postrotate
        pm2 reload all > /dev/null 2>&1 || true
    endscript
}
EOF

    echo -e "${GREEN}✅ Logging configuré${NC}"
}

# Vérifications finales
final_checks() {
    print_step "Vérifications finales"
    
    echo "Vérification des services..."
    
    # MySQL
    if mysqladmin -u $DB_USER -p$DB_PASS ping > /dev/null 2>&1; then
        echo "✅ MySQL: OK"
    else
        echo "❌ MySQL: FAIL"
    fi
    
    # Redis
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis: OK"
    else
        echo "❌ Redis: FAIL"
    fi
    
    # Python env
    if [ -d $PROJECT_DIR/venv ]; then
        echo "✅ Python venv: OK"
    else
        echo "❌ Python venv: FAIL"
    fi
    
    # Nginx config
    if sudo nginx -t > /dev/null 2>&1; then
        echo "✅ Nginx config: OK"
    else
        echo "❌ Nginx config: FAIL"
    fi
}

# Résumé de l'installation
installation_summary() {
    echo -e "\n${GREEN}🎉 INSTALLATION TERMINÉE !${NC}"
    echo "=========================="
    echo
    echo "📁 Projet installé dans: $PROJECT_DIR"
    echo "🗄️  Base de données: $DB_NAME"
    echo "👤 Utilisateur DB: $DB_USER"
    echo "🔑 Mot de passe DB: $DB_PASS"
    echo
    echo "📋 PROCHAINES ÉTAPES:"
    echo "1. Compléter la configuration dans .env (SmartProxy, Stripe)"
    echo "2. Ajouter vos fichiers de code source"
    echo "3. Construire le frontend: cd frontend && npm run build"
    echo "4. Démarrer les services: ./start.sh"
    echo "5. Vérifier le monitoring: ./monitor.sh"
    echo
    echo "🌐 URLs d'accès:"
    echo "- Application: http://localhost"
    echo "- API Docs: http://localhost/docs"
    echo "- Monitoring: pm2 monit"
    echo
    echo "🔧 Commandes utiles:"
    echo "- Démarrer: ./start.sh"
    echo "- Arrêter: ./stop.sh"
    echo "- Monitoring: ./monitor.sh"
    echo "- Sauvegarde: ./backup.sh"
    echo
    print_warning "N'oubliez pas de configurer SmartProxy et Stripe dans le fichier .env !"
}

# MAIN - Exécution du script
main() {
    echo "🚀 Début de l'installation native Vinted Bot SAAS"
    
    detect_os
    echo "OS détecté: $OS"
    
    install_system_deps
    setup_mysql
    setup_redis
    setup_project_dir
    setup_python_env
    setup_frontend
    install_pm2
    setup_nginx
    create_env_file
    create_utility_scripts
    import_database_schema
    setup_logging
    final_checks
    installation_summary
}

# Exécuter l'installation
main "$@"

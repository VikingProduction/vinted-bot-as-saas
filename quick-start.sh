#!/bin/bash

# Script de démarrage rapide pour installation native
# Usage: ./quick-start.sh

set -e

PROJECT_DIR="/opt/vinted-bot-saas"

echo "🚀 Démarrage Rapide Vinted Bot SAAS"
echo "==================================="

# Vérifier si installé
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Installation non trouvée. Exécutez d'abord install-native.sh"
    exit 1
fi

cd $PROJECT_DIR

# 1. Vérifier les services système
echo "📋 Vérification des services système..."

# MySQL
if ! systemctl is-active --quiet mysql; then
    echo "🔄 Démarrage MySQL..."
    sudo systemctl start mysql
fi

# Redis
if ! systemctl is-active --quiet redis; then
    echo "🔄 Démarrage Redis..."
    sudo systemctl start redis-server || sudo systemctl start redis
fi

# Nginx
if ! systemctl is-active --quiet nginx; then
    echo "🔄 Démarrage Nginx..."
    sudo systemctl start nginx
fi

# 2. Construire le frontend si nécessaire
if [ ! -d "frontend/build" ]; then
    echo "🏗️ Construction du frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# 3. Activer l'environnement Python
echo "🐍 Activation environnement Python..."
source venv/bin/activate

# 4. Vérifier la base de données
echo "🗄️ Vérification base de données..."
if ! mysql -u vinted_user -p$(grep DB_PASS .env | cut -d'=' -f2) -e "USE vinted_bot;" 2>/dev/null; then
    echo "❌ Problème base de données. Vérifiez la configuration."
    exit 1
fi

# 5. Démarrer avec PM2
echo "⚡ Démarrage des services avec PM2..."

# Arrêter les anciens processus
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Démarrer les nouveaux
pm2 start ecosystem.config.js

# 6. Attendre que les services soient prêts
echo "⏳ Attente démarrage des services..."
sleep 10

# 7. Vérifications de santé
echo "🏥 Vérification de santé..."

# API
if curl -s -f http://localhost:8000/health > /dev/null; then
    echo "✅ API: OK"
else
    echo "❌ API: FAIL"
    echo "Logs API:"
    pm2 logs vinted-bot-api --lines 5
fi

# Frontend/Nginx
if curl -s -f http://localhost > /dev/null; then
    echo "✅ Frontend: OK"
else
    echo "❌ Frontend: FAIL"
fi

# Celery Worker
if pm2 list | grep -q "vinted-bot-worker.*online"; then
    echo "✅ Worker: OK"
else
    echo "❌ Worker: FAIL"
fi

# 8. Afficher le statut
echo ""
echo "📊 Statut des services:"
pm2 status

echo ""
echo "🌐 URLs d'accès:"
echo "- Application: http://localhost"
echo "- API Docs: http://localhost/docs"
echo "- API Health: http://localhost:8000/health"

echo ""
echo "🎯 TODO - Configuration requise:"
echo "1. Configurer SmartProxy dans .env:"
echo "   SMARTPROXY_USERNAME=your_username"
echo "   SMARTPROXY_PASSWORD=your_password"
echo ""
echo "2. Configurer Stripe dans .env:"
echo "   STRIPE_SECRET_KEY=sk_test_..."
echo "   STRIPE_PUBLISHABLE_KEY=pk_test_..."
echo ""
echo "3. Redémarrer après configuration: pm2 restart all"

echo ""
echo "✅ Démarrage terminé ! Votre bot Vinted SAAS est prêt."

# Proposer de lancer le monitoring
read -p "Voulez-vous lancer le monitoring temps réel ? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pm2 monit
fi
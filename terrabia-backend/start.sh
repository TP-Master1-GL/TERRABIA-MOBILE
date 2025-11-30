#!/bin/bash
# start.sh

set -e  # Arrêter en cas d'erreur

echo "=== Démarrage de l'application TERRABIA ==="

# Attendre que la base de données soit prête (si vous utilisez PostgreSQL plus tard)
# while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
#   echo "En attente de la base de données..."
#   sleep 1
# done

echo "=== Application des migrations ==="
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "=== Collecte des fichiers statiques ==="
python manage.py collectstatic --noinput

echo "=== Création d'un superutilisateur par défaut (si nécessaire) ==="
# python manage.py createsuperuser --noinput --email admin@terrabia.com || true

echo "=== Démarrage du serveur Daphne ==="
exec daphne -b 0.0.0.0 -p 8000 Terrabia.asgi:application

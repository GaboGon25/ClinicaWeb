#!/bin/bash

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Realizar migraciones
python manage.py migrate 
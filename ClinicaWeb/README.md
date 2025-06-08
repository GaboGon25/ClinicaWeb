# Clínica Web - Deploy en Render

## Cambios Realizados para el Deploy

### 1. Archivos de Configuración
- `requirements.txt`: Actualizado con las dependencias necesarias para producción
- `build.sh`: Script para instalar dependencias y recopilar archivos estáticos
- `Procfile`: Configuración para ejecutar la aplicación con Gunicorn
- `.env`: Archivo para variables de entorno (no incluido en el repositorio)

### 2. Configuración de Django (settings.py)
- Configuración de variables de entorno
- Configuración de base de datos PostgreSQL
- Configuración de archivos estáticos con WhiteNoise
- Ajuste de ALLOWED_HOSTS para Render

## Pasos para Deploy

1. **Crear cuenta en Render**
   - Registrarse en [render.com](https://render.com)
   - Conectar con GitHub

2. **Crear Base de Datos**
   - Crear nueva base de datos PostgreSQL en Render
   - Guardar la URL de la base de datos

3. **Desplegar Aplicación**
   - Crear nuevo Web Service
   - Conectar con el repositorio
   - Configurar variables de entorno:
     ```
     SECRET_KEY=tu_secret_key
     DEBUG=False
     DATABASE_URL=url_de_postgres
     ```

4. **Variables de Entorno en Render**
   - Ir a la sección Environment
   - Agregar las variables del archivo .env

## Estructura de Archivos
```
ClinicaWeb/
├── proyecto_clinica/
├── JyGDreams/
├── requirements.txt
├── build.sh
├── Procfile
├── .env (local)
└── .gitignore
```

## Notas Importantes
- El archivo `.env` no se incluye en el repositorio por seguridad
- Los archivos estáticos se sirven a través de WhiteNoise
- La base de datos local (SQLite) se reemplaza por PostgreSQL en producción 
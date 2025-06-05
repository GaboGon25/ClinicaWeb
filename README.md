# Proyecto Clínica Web

## Dependencias del Proyecto

### Dependencias Base
- `Django==5.2.1`: Framework web principal
- `asgiref==3.8.1`: Servidor ASGI para Django
- `sqlparse==0.5.3`: Parser SQL para Django
- `tzdata==2025.2`: Datos de zonas horarias

### Dependencias para PostgreSQL y Deploy
- `psycopg2-binary==2.9.9`: Adaptador PostgreSQL para Python
  - Permite la conexión entre Django y PostgreSQL
  - Versión binaria precompilada para fácil instalación

- `dj-database-url==2.1.0`: Utilidad para configurar BD con URLs
  - Facilita la configuración de la base de datos
  - Permite usar URLs de conexión en lugar de diccionarios de configuración

- `python-decouple==3.8`: Manejo de configuraciones
  - Separa la configuración del código
  - Permite usar variables de entorno y archivos .env

- `whitenoise==6.6.0`: Servidor de archivos estáticos
  - Mejora el rendimiento de archivos estáticos
  - Necesario para producción

- `gunicorn==21.2.0`: Servidor WSGI para producción
  - Servidor web para ejecutar Django en producción
  - Más robusto que el servidor de desarrollo de Django

## Pasos de Configuración

### 1. Configuración de PostgreSQL (Neon.tech)
- [x] Crear cuenta en Neon.tech
- [x] Crear proyecto y base de datos
- [x] Obtener URL de conexión
- [x] Configurar variables de entorno en .env

### 2. Configuración del Proyecto
- [x] Actualizar requirements.txt
- [x] Crear archivo .env
- [x] Instalar dependencias
- [x] Configurar settings.py para PostgreSQL
- [x] Migrar datos de SQLite a PostgreSQL

### 3. Preparación para Deploy en Vercel
- [x] Configurar archivos estáticos
- [x] Preparar configuración de producción
- [x] Configurar vercel.json
- [x] Crear build_files.sh
- [x] Configurar variables de entorno en Vercel

## Despliegue en Vercel

### 1. Configuración Inicial
1. Crear cuenta en Vercel (si no tienes una)
2. Conectar tu repositorio de GitHub con Vercel
3. Seleccionar el repositorio del proyecto

### 2. Configuración del Proyecto en Vercel
1. En la sección "Settings" del proyecto:
   - Ir a "Environment Variables"
   - Agregar las siguientes variables:
     ```
     DEBUG=False
     SECRET_KEY=tu-clave-secreta
     ALLOWED_HOSTS=.vercel.app,.now.sh,localhost,127.0.0.1
     DATABASE_URL=tu-url-de-neon
     ```

### 3. Archivos de Configuración
1. `vercel.json`:
   ```json
   {
       "version": 2,
       "builds": [
           {
               "src": "proyecto_clinica/wsgi.py",
               "use": "@vercel/python"
           },
           {
               "src": "build_files.sh",
               "use": "@vercel/static-build",
               "config": {
                   "distDir": "staticfiles"
               }
           }
       ],
       "routes": [
           {
               "src": "/static/(.*)",
               "dest": "/static/$1"
           },
           {
               "src": "/(.*)",
               "dest": "proyecto_clinica/wsgi.py"
           }
       ]
   }
   ```

2. `build_files.sh`:
   ```bash
   #!/bin/bash
   pip install -r requirements.txt
   python manage.py collectstatic --noinput
   python manage.py migrate
   ```

### 4. Proceso de Despliegue
1. Hacer commit de todos los cambios
2. Push al repositorio
3. Vercel detectará automáticamente los cambios
4. Iniciará el proceso de construcción
5. Desplegará la aplicación

### 5. Verificación Post-Despliegue
1. Verificar que la aplicación está funcionando
2. Comprobar la conexión a la base de datos
3. Verificar que los archivos estáticos se sirven correctamente
4. Probar las funcionalidades principales

## Cambios Recientes Implementados

### 1. Migración a PostgreSQL
- ✅ Migración exitosa de SQLite a PostgreSQL
- ✅ Configuración de Neon.tech como proveedor de base de datos
- ✅ Migración de datos existentes

### 2. Configuración para Vercel
- ✅ Creación de vercel.json
- ✅ Implementación de build_files.sh
- ✅ Configuración de archivos estáticos
- ✅ Optimización para producción

### 3. Mejoras de Seguridad
- ✅ Variables de entorno configuradas
- ✅ DEBUG=False en producción
- ✅ Configuración de ALLOWED_HOSTS
- ✅ Protección de credenciales

## Comandos Útiles

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Migración de Base de Datos
```bash
python manage.py makemigrations
python manage.py migrate
```

### Crear Superusuario
```bash
python manage.py createsuperuser
```

### Ejecutar Servidor
```bash
python manage.py runserver
```

### Recolectar Archivos Estáticos
```bash
python manage.py collectstatic --noinput
```

## Notas Importantes
- Mantener el archivo .env fuera del control de versiones
- No compartir credenciales de base de datos
- Hacer backup regular de la base de datos
- Seguir las mejores prácticas de seguridad de Django
- Verificar la configuración de archivos estáticos antes del deploy
- Asegurar que DEBUG=False en producción
- Mantener actualizadas las dependencias
- Revisar los logs de Vercel para debugging

## Estado Actual del Proyecto
- ✅ **Migración a PostgreSQL completada**
- ✅ **Configuración para Vercel implementada**
- ✅ **Archivos estáticos configurados**
- ✅ **Variables de entorno configuradas**
- ✅ **Listo para despliegue en producción** 
# Instalar venv

sudo apt install python3.12-venv

# Instalar entorno de venv

python3 -m venv venv

# Activar entorno local para Windows

venv\Scripts\activate

# Activar entorno local para MAC o LINUX

source venv/bin/activate

# Instalar requerimientos

pip3 install -r requirements.txt

# Iniciar fastapi con uvicorn

uvicorn main:app --reload

# -----------------------------------------------

# Instalar base de datos

sudo apt install postgresql -y

# Acceder a la consola de postgresql

sudo -i -u postgres psql

# Crear usuario en postgresql

CREATE ROLE developer WITH LOGIN SUPERUSER PASSWORD 'tu_password';

# Darle permisos

CREATE DATABASE molinos OWNER developer;

# Salir de la consola de postgresql

\q
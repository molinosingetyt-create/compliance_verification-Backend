# Configuración del backend

## 1. Entorno virtual (Python)

```bash
sudo apt install python3-venv
python3 -m venv venv
```

Activar el entorno:

- **Windows:** `venv\Scripts\activate`
- **Linux / macOS:** `source venv/bin/activate`

Instalar dependencias:

```bash
pip3 install -r requirements.txt
```

## 2. Variables de entorno

Copia el archivo de ejemplo y ajusta los valores si es necesario:

```bash
cp .env.example .env
```

Las credenciales de base de datos por defecto son:

- Usuario: `developer`
- Contraseña: `P@ssw0rd`
- Base de datos: `molinos`

## 3. PostgreSQL

Instalar y acceder a la consola:

```bash
sudo apt install postgresql -y
sudo -i -u postgres psql
```

Crear usuario y base de datos (deben coincidir con `.env`):

```sql
CREATE ROLE developer WITH LOGIN SUPERUSER PASSWORD 'P@ssw0rd';
CREATE DATABASE molinos OWNER developer;
\q
```

Si el usuario ya existe, solo actualiza la contraseña:

```sql
ALTER ROLE developer WITH PASSWORD 'P@ssw0rd';
```

## 4. Iniciar la aplicación

```bash
uvicorn main:app --reload
```

## 5. Formato de código

```bash
black .
```

# Aplicació Flask amb Gunicorn i SSH

## 🛠️ Instal·lació i Ús

### 1. Construir la imatge Docker
```bash
docker build -t flask-app .
```
### 2. Executar el contenidor
```bash
docker run -d \
  --name my-flask-app \
  -p 8000:8000 \
  -p 2222:22 \
  flask-app
```
### 3. Accés als serveis

**Aplicació Flask**:  
Disponible a `http://localhost:8000`

**Accés SSH**:
```bash
ssh root@localhost -p 2222
Contrasenya: password
```

## 🌐 URL Pública a Docker Hub

La imatge preconstruïda està disponible a [docker hub](https://hub.docker.com/r/ianditb/flask_app), o:  
`docker pull ianditb/flask_app:latest`

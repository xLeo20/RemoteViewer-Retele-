# Remote Viewer 🖥️

Un proiect client-server construit in Python care permite [scrie aici o scurta descriere, ex: transmiterea de pachete de date si vizualizarea statusului conexiunilor la distanta].

## 📂 Structura Proiectului

- `shared/` - Contine protocolul de comunicare comun (`protocol.py`), respectand principiul DRY.
- `server/` - Contine logica serverului si fisierul de configurare Docker.
- `client/` - Contine scriptul pentru conectarea la server.

## 🚀 Cum sa pornesti Serverul (cu Docker)

Serverul este "containerizat" pentru a rula usor oriunde. Asigura-te ca ai [Docker](https://www.docker.com/) instalat.

1. Deschide un terminal in **radacina** proiectului.

2. Construieste imaginea Docker:

   docker build -f server/Dockerfile -t remote-server .
   
3. Porneste containerul:
   docker run -p 5000:5000 remote-server

# Remote Viewer 🖥️

Un proiect client-server construit in Python care permite [scrie aici o scurta descriere, ex: transmiterea de pachete de date si vizualizarea statusului conexiunilor la distanta].

## 📂 Structura Proiectului

- `shared/` - Contine protocolul de comunicare comun (`protocol.py`), respectand principiul DRY.
- `server/` - Contine logica serverului si fisierul de configurare Docker.
- `client/` - Contine scriptul pentru conectarea la server.

## 🚀 Cum sa pornesti Serverul (cu Docker)

Serverul este "containerizat" pentru a rula usor oriunde.

1. Deschide un terminal in **radacina** proiectului.

2. Construieste imaginea Docker:
   
   docker build -f server/Dockerfile -t remote-server .

3. Porneste containerul:
docker run -p 5000:5000 remote-server


## 💻 Cum sa folosesti Clientul
Pentru a rula clientul, ai nevoie de Python instalat pe masina ta locala.

1. Deschide un terminal separat (in timp ce serverul ruleaza).

2. Navigheaza in folderul clientului:
cd client

3. Ruleaza scriptul:
python client.py

# 🛠️ Tehnologii Folosite
Python 3.10
Docker
Sockets / [Adauga orice alta biblioteca importanta ai folosit]
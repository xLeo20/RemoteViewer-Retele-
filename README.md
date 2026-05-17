# Remote Viewer 🖥️

Un proiect client-server construit in Python care permite vizualizarea la distanta a sesiunii grafice a unui alt utilizator, folosind un stream continuu de capturi de ecran.

## 📂 Structura Proiectului
- `shared/` - Contine protocolul de comunicare comun (`protocol.py`), respectand principiul DRY.
- `server/` - Contine logica serverului si fisierul de configurare Docker.
- `client/` - Contine scriptul pentru conectarea la server si interfata grafica.

## 🚀 Cum sa pornesti Serverul (cu Docker)
1. Deschide un terminal in **radacina** proiectului.
2. Construieste imaginea Docker:
   `docker build -f server/Dockerfile -t remote-server .`
3. Porneste containerul:
   `docker run -p 5000:5000 remote-server`

## 💻 Cum sa folosesti Clientul
Pentru a rula clientul, instaleaza dependentele externe necesare pentru captura si afisare.
1. Deschide un terminal si ruleaza:
   `pip install mss Pillow`
2. Navigheaza in folderul clientului:
   `cd client`
3. Ruleaza scriptul:
   `python client.py`

*Nota: Rata de actualizare a ecranului este configurabila. Se poate modifica variabila `REFRESH_RATE` din fisierul `client.py` (implicit este setata la 0.2 secunde).*

## 🛠️ Tehnologii si Librarii Folosite
- Python 3.10
- Docker
- Sockets (pentru TCP)
- **mss** - Librarie pentru captura de ecran ultra-rapida.
- **Pillow (PIL)** - Librarie pentru procesarea si comprimarea imaginilor (JPEG).
- **Tkinter** - Pentru interfata grafica.
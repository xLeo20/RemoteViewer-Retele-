# Folosim o imagine oficială Python, versiunea "slim"
FROM python:3.10-slim

# Setăm directorul de lucru
WORKDIR /app

# Copiem folderul comun și folderul serverului în container
COPY shared/ /app/shared/
COPY server/ /app/server/

# Expunem portul
EXPOSE 5000

# Executăm serverul (atenție, calea s-a schimbat ușor)
CMD ["python", "server/server.py"]
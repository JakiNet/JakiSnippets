#!/bin/bash
# Forzar la actualización de los archivos en el sistema
sudo mkdir -p /opt/jakisnippets

# Copiar archivos pisando los viejos
sudo cp -f jaki.py /opt/jakisnippets/
sudo cp -f snippets.json /opt/jakisnippets/

# Dar permisos
sudo chmod +x /opt/jakisnippets/jaki.py
sudo ln -sf /opt/jakisnippets/jaki.py /usr/local/bin/jaki

echo "[+] Sincronización completa en /opt/jakisnippets/"

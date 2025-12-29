#!/bin/bash

# Colores para la terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}[*] Instalando JakiSnippets v2.0...${NC}"

# 1. Crear directorio en /opt (lugar estándar para software opcional)
sudo mkdir -p /opt/jakisnippets

# 2. Copiar archivos
echo -e "${BLUE}[*] Copiando archivos a /opt/jakisnippets...${NC}"
sudo cp jaki.py /opt/jakisnippets/jaki.py
sudo cp snippets.json /opt/jakisnippets/snippets.json

# 3. Instalar dependencias de Python
echo -e "${BLUE}[*] Instalando dependencias (pyperclip para el portapapeles)...${NC}"
pip3 install pyperclip --break-system-packages 2>/dev/null || pip3 install pyperclip

# 4. Crear el enlace simbólico para que el comando 'jaki' funcione en todo el sistema
echo -e "${BLUE}[*] Creando comando global 'jaki'...${NC}"
sudo ln -sf /opt/jakisnippets/jaki.py /usr/local/bin/jaki
sudo chmod +x /usr/local/bin/jaki

echo -e "${GREEN}[+] ¡Instalación completada con éxito!${NC}"
echo -e "${GREEN}[+] Ahora puedes usar 'jaki' desde cualquier carpeta.${NC}"

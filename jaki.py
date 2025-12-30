#!/usr/bin/env python3
import json
import sys
import os

VERSION_ACTUAL = "1.2"

# Intentar importar pyperclip para copiar al portapapeles
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

class Colores:
    HEADER, BLUE, GREEN, YELLOW, RED, ENDC, BOLD = '\033[95m', '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m'

# --- CONFIGURACIÓN DE RUTAS ---
# Prioridad 1: Archivo en el HOME del usuario (Para que siempre pueda escribir)
USER_CONFIG = os.path.expanduser("~/.jaki_snippets.json")
# Prioridad 2: Archivo en la carpeta de instalación (Solo lectura si es /opt/)
SYSTEM_CONFIG = "/opt/jakisnippets/snippets.json"

def get_data_path():
    # 1. RUTA DEL SISTEMA (Donde 'update' guarda los cambios)
    SYSTEM_PATH = "/opt/jakisnippets/snippets.json"
    
    # 2. RUTA LOCAL (Donde el usuario agrega sus cosas)
    USER_PATH = os.path.expanduser("~/.jaki_snippets.json")

    # PRIORIDAD 1: Si estamos en la carpeta del repo (Desarrollo)
    if os.path.exists(".git") and os.path.exists("snippets.json"):
        return os.path.abspath("snippets.json")

    # PRIORIDAD 2: El archivo del SISTEMA (El que acabas de actualizar)
    if os.path.exists(SYSTEM_PATH):
        return SYSTEM_PATH

    # PRIORIDAD 3: El archivo del USUARIO
    return USER_PATH

def print_banner():
    print(f"""{Colores.BLUE}{Colores.BOLD}
      ██╗ █████╗ ██╗  ██╗██╗███████╗███╗   ██╗██╗██████╗ ██████╗ ███████╗████████╗███████╗
      ██║██╔══██╗██║ ██╔╝██║██╔════╝████╗  ██║██║██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝
      ██║███████║█████╔╝ ██║███████╗██╔██╗ ██║██║██████╔╝██████╔╝█████╗      ██║   ███████║
 ██   ██║██╔══██║██╔═██╗ ██║╚════██║██║╚██╗██║██║██╔═══╝ ██╔═══╝ ██╔══╝      ██║   ╚════██║
 ╚█████╔╝██║  ██║██║  ██╗██║███████║██║ ╚████║██║██║      ██║      ███████╗    ██║   ███████║
  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝╚═╝╚═╝      ╚═╝      ╚══════╝    ╚═╝   ╚══════╝
    {Colores.ENDC}""")

def load_data():
    path = get_data_path()
    if not os.path.exists(path):
        return {} # Retorna base de datos vacía si no hay archivo
    
    try:
        with open(path, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except Exception as e:
        print(f"{Colores.RED}[!] Error cargando base de datos: {e}{Colores.ENDC}")
        return {}

def buscar(data, query):
    resultados = []
    query = query.lower()
    
    for categoria, snippets in data.items():
        if query in categoria.lower():
            for s in snippets:
                s_copy = s.copy()
                s_copy['cat'] = categoria
                resultados.append(s_copy)
        else:
            for s in snippets:
                if query in s['titulo'].lower() or query in s['cmd'].lower():
                    s_copy = s.copy()
                    s_copy['cat'] = categoria
                    resultados.append(s_copy)
    
    if not resultados:
        print(f"{Colores.RED}❌ No se encontró nada que coincida con '{query}'.{Colores.ENDC}")
        return

    for idx, r in enumerate(resultados):
        print(f"{Colores.GREEN}[{idx}]{Colores.ENDC} {Colores.BLUE}[{r['cat']}]{Colores.ENDC} {Colores.BOLD}{r['titulo']}{Colores.ENDC}")
        print(f"    {Colores.YELLOW}{r['cmd']}{Colores.ENDC}")
    
    print(f"\n{Colores.BLUE}👉 Elige un número para copiar (o Enter para salir):{Colores.ENDC}")
    try:
        opcion = input("> ")
        if opcion.isdigit() and int(opcion) < len(resultados):
            cmd_final = resultados[int(opcion)]['cmd']
            if HAS_PYPERCLIP:
                pyperclip.copy(cmd_final)
                print(f"\n{Colores.GREEN}📋 ¡Copiado al portapapeles!{Colores.ENDC}")
            else:
                print(f"\n{Colores.YELLOW}📋 Copia manualmente:{Colores.ENDC}\n{cmd_final}")
    except (KeyboardInterrupt, EOFError):
        print("\nSaliendo...")

def listar_categorias(data):
    if not data:
        print(f"{Colores.YELLOW}La base de datos está vacía.{Colores.ENDC}")
        return
    print(f"{Colores.HEADER}Categorías Disponibles:{Colores.ENDC}")
    print(" | ".join(data.keys()))

def agregar_snippet(data):
    print(f"\n{Colores.BLUE}--- Añadir Nuevo Comando ---{Colores.ENDC}")
    listar_categorias(data)
    
    cat = input("\n[?] Categoría: ").strip().lower()
    tit = input("[?] Título: ").strip()
    cmd = input("[?] Comando: ").strip()
    
    if not cat or not tit or not cmd:
        print(f"{Colores.RED}❌ Error: Todos los campos son obligatorios.{Colores.ENDC}")
        return

    if cat not in data: data[cat] = []
    data[cat].append({"titulo": tit, "cmd": cmd})

    # Decidir dónde guardar: Si no tenemos permiso en /opt, guardamos en el HOME
    save_path = USER_CONFIG
    
    # Intentar guardar
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"{Colores.GREEN}✅ Guardado correctamente en: {save_path}{Colores.ENDC}")
    except Exception as e:
        print(f"{Colores.RED}❌ Error al guardar: {e}{Colores.ENDC}")

import urllib.request # Asegúrate de tener este import arriba

def actualizar():
    """Comprueba la versión y actualiza si es necesario."""
    url_version_raw = "https://raw.githubusercontent.com/JakiNet/JakiSnippets/main/jaki.py"
    
    print(f"{Colores.BLUE}[*] Comprobando actualizaciones...{Colores.ENDC}")
    
    try:
        # Intentamos leer la versión del repo remoto sin descargar todo
        with urllib.request.urlopen(url_version_raw) as response:
            contenido = response.read().decode('utf-8')
            # Buscamos la línea VERSION_ACTUAL = "X.X" en el texto
            import re
            match = re.search(r'VERSION_ACTUAL\s*=\s*["\']([^"\']+)["\']', contenido)
            
            if match:
                version_remota = match.group(1)
                if version_remota == VERSION_ACTUAL:
                    print(f"{Colores.GREEN}✅ Ya tienes la última versión (v{VERSION_ACTUAL}).{Colores.ENDC}")
                    return
                else:
                    print(f"{Colores.YELLOW}[!] Nueva versión detectada: v{version_remota} (Tienes la v{VERSION_ACTUAL}){Colores.ENDC}")
            
    except Exception:
        # Si falla la comprobación (ej. sin internet), continuamos con la actualización por si acaso
        print(f"{Colores.YELLOW}[!] No se pudo verificar la versión, procediendo con la descarga...{Colores.ENDC}")

    # --- A partir de aquí sigue tu lógica de clonación y ejecución de install.sh ---
    if os.geteuid() != 0:
        print(f"{Colores.RED}[!] Error: Debes ejecutar 'sudo jaki update' para instalar los cambios.{Colores.ENDC}")
        return

    repo_url = "https://github.com/JakiNet/JakiSnippets.git"
    temp_dir = "/tmp/jaki_update_dir"

    try:
        os.system(f"rm -rf {temp_dir}")
        print(f"{Colores.YELLOW}[*] Descargando actualización...{Colores.ENDC}")
        result = os.system(f"git clone --depth 1 {repo_url} {temp_dir} > /dev/null 2>&1")
        
        # Esta línea debe estar alineada con el 'result' de arriba
        if result == 0 and os.path.exists(temp_dir):
            os.chdir(temp_dir)
            archivos = os.listdir('.')
            instalador = next((f for f in archivos if f.lower() == "install.sh"), None)
            
            if instalador:
                os.system(f"chmod +x {instalador}")
                if os.system(f"sudo bash {instalador}") == 0:
                    v = version_remota if 'version_remota' in locals() else "nueva"
                    print(f"\n{Colores.GREEN}✅ ¡JakiSnippets actualizado a la v{v}!{Colores.ENDC}")
            else:
                print(f"{Colores.RED}[!] Error: No se encontró el instalador.{Colores.ENDC}")
                
    finally:
        os.chdir("/")
        os.system(f"rm -rf {temp_dir}")

def main():
    print_banner()
    data = load_data()
    
    if len(sys.argv) < 2:
        print(f"{Colores.YELLOW}Modo de uso:{Colores.ENDC}")
        print("  jaki <termino>        -> Buscar rápido")
        print("  jaki buscar <termino> -> Búsqueda explícita")
        print("  jaki listar           -> Ver categorías")
        print("  jaki agregar          -> Añadir comando")
        print("  sudo jaki update      -> Actualizar herramienta") # <--- AÑADE ESTO
        return

    acc = sys.argv[1].lower()

    if acc == "listar":
        listar_categorias(data)
    elif acc == "agregar":
        agregar_snippet(data)
    elif acc == "buscar":
        if len(sys.argv) > 2:
            buscar(data, " ".join(sys.argv[2:]))
        else:
            print(f"{Colores.RED}[!] Indica qué buscar después de 'buscar'.{Colores.ENDC}")
    elif acc == "update": # <--- NUEVA OPCIÓN
        actualizar()
    else:
        buscar(data, acc)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbordado.")
        sys.exit(0)

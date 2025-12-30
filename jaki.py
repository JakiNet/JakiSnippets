#!/usr/bin/env python3
import json
import sys
import os

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
    # NUEVA LÍNEA: Si hay un snippets.json aquí mismo, úsalo (Ideal para Git)
    if os.path.exists("snippets.json"):
        return os.path.abspath("snippets.json")
    
    if os.path.exists(USER_CONFIG):
        return USER_CONFIG
    if os.path.exists(SYSTEM_CONFIG):
        return SYSTEM_CONFIG
    return USER_CONFIG

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

def actualizar():
    """Descarga la última versión desde GitHub y reinstala la herramienta."""
    print(f"{Colores.BLUE}[*] Iniciando actualización desde GitHub...{Colores.ENDC}")
    
    if os.geteuid() != 0:
        print(f"{Colores.RED}[!] Error: Debes ejecutar 'sudo jaki update' para actualizar.{Colores.ENDC}")
        return

    repo_url = "https://github.com/JakiNet/JakiSnippets.git"
    temp_dir = "/tmp/jaki_update"

    try:
        os.system(f"rm -rf {temp_dir}")
        print(f"{Colores.YELLOW}[*] Clonando última versión...{Colores.ENDC}")
        # Clonamos el repositorio
        os.system(f"git clone --depth 1 {repo_url} {temp_dir} > /dev/null 2>&1")
        
        if os.path.exists(temp_dir):
            os.chdir(temp_dir)
            
            # Buscamos el instalador sin importar mayúsculas/minúsculas
            archivos = os.listdir('.')
            instalador = next((f for f in archivos if f.lower() == "install.sh"), None)
            
            if instalador:
                print(f"{Colores.YELLOW}[*] Ejecutando {instalador}...{Colores.ENDC}")
                os.system(f"chmod +x {instalador}") # Aseguramos permisos
                os.system(f"bash {instalador}")
                print(f"\n{Colores.GREEN}✅ ¡JakiSnippets actualizado con éxito!{Colores.ENDC}")
            else:
                # Si no hay install.sh, quizás solo necesites copiar el script a /usr/local/bin
                print(f"{Colores.RED}[!] Error: No se encontró 'install.sh' o 'Install.sh'.{Colores.ENDC}")
                print(f"{Colores.YELLOW}[*] Sugerencia: Revisa el nombre del archivo en el repositorio.{Colores.ENDC}")
        
    except Exception as e:
        print(f"{Colores.RED}[!] Error: {e}{Colores.ENDC}")
    finally:
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

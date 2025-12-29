#!/usr/bin/env python3
import json, sys, os

# Intentar importar pyperclip para copiar al portapapeles
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

class Colores:
    HEADER, BLUE, GREEN, YELLOW, RED, ENDC, BOLD = '\033[95m', '\033[94m', '\033[92m', '\033[93m', '\033[91m', '\033[0m', '\033[1m'

def print_banner():
    print(f"""{Colores.BLUE}{Colores.BOLD}
      ██╗ █████╗ ██╗  ██╗██╗███████╗███╗   ██╗██╗██████╗ ██████╗ ███████╗████████╗███████╗
      ██║██╔══██╗██║ ██╔╝██║██╔════╝████╗  ██║██║██╔══██╗██╔══██╗██╔════╝╚══██╔══╝██╔════╝
      ██║███████║█████╔╝ ██║███████╗██╔██╗ ██║██║██████╔╝██████╔╝█████╗     ██║   ███████╗
 ██   ██║██╔══██║██╔═██╗ ██║╚════██║██║╚██╗██║██║██╔═══╝ ██╔═══╝ ██╔══╝     ██║   ╚════██║
 ╚█████╔╝██║  ██║██║  ██╗██║███████║██║ ╚████║██║██║     ██║     ███████╗    ██║   ███████║
  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝     ╚══════╝    ╚═╝   ╚══════╝
    {Colores.ENDC}""")

def load_data():
    path = "/opt/jakisnippets/snippets.json"
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), 'snippets.json')
    
    try:
        with open(path, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except Exception as e:
        print(f"{Colores.RED}[!] Error cargando base de datos: {e}{Colores.ENDC}")
        sys.exit(1)

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

    # Mostrar resultados numerados
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
    print(f"{Colores.HEADER}Categorías Disponibles:{Colores.ENDC}")
    print(" | ".join(data.keys()))

def agregar_snippet(data):
    print(f"\n{Colores.BLUE}--- Añadir Nuevo Comando ---{Colores.ENDC}")
    listar_categorias(data)
    cat = input("\n[?] Categoría: ").lower()
    tit = input("[?] Título: ")
    cmd = input("[?] Comando: ")
    
    if cat not in data: data[cat] = []
    data[cat].append({"titulo": tit, "cmd": cmd})

    path = "/opt/jakisnippets/snippets.json"
    if not os.access(os.path.dirname(path), os.W_OK):
        path = os.path.join(os.path.dirname(__file__), 'snippets.json')

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"{Colores.GREEN}✅ Guardado.{Colores.ENDC}")

def main():
    print_banner()
    data = load_data()
    
    if len(sys.argv) < 2:
        print(f"{Colores.YELLOW}Modo de uso:{Colores.ENDC}")
        print("  jaki <termino>         -> Buscar rápido (ej: jaki sqli)")
        print("  jaki buscar <termino>  -> Búsqueda explícita")
        print("  jaki listar            -> Ver categorías")
        print("  jaki agregar           -> Añadir comando")
        return

    acc = sys.argv[1].lower()

    # Lógica de excepciones y comandos
    if acc == "listar":
        listar_categorias(data)
    elif acc == "agregar":
        agregar_snippet(data)
    elif acc == "buscar":
        if len(sys.argv) > 2:
            buscar(data, " ".join(sys.argv[2:]))
        else:
            print(f"{Colores.RED}[!] Indica qué buscar después de 'buscar'.{Colores.ENDC}")
    else:
        # EXCEPCIÓN: Si el usuario escribe 'jaki algo', se busca 'algo' directamente
        buscar(data, acc)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbordado.")
        sys.exit(0)

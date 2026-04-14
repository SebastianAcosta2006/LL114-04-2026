import re
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configuración del Analizador Léxico (Lexer)
# Cambiamos la estructura a una lista simple de tuplas para el mapeo
MAPA_TOKENS = [
    ("NUM2", r"\bdos\b"),
    ("NUM3", r"\btres\b"),
    ("NUM4", r"\bcuatro\b"),
    ("NUM5", r"\bcinco\b"),
    ("NUM6", r"\bseis\b"),
    ("NUM1", r"\buno\b"),
    ("ESPACIO", r"\s+"),
]

# Construcción de la expresión regular unificada
REGEX_LEX = re.compile("|".join(f"(?P<{k}>{v})" for k, v in MAPA_TOKENS))

def obtener_tokens(entrada):
    """Convierte el texto de entrada en una lista de pares (tipo, valor)."""
    resultado = []
    for coincidencia in REGEX_LEX.finditer(entrada):
        id_token = coincidencia.lastgroup
        if id_token != "ESPACIO":
            resultado.append((id_token, coincidencia.group()))
    return resultado

class ElementoArbol:
    """Representa un nodo en el árbol de derivación sintáctica."""
    def __init__(self, nombre):
        self.tag = nombre
        self.subnodos = []
        # Coordenadas para dibujo
        self.coord_x = 0
        self.coord_y = 0

    def vincular(self, subnodo):
        self.subnodos.append(subnodo)
        return subnodo

class AnalizadorSintactico:
    """Parser recursivo descendente con backtracking."""
    def __init__(self, lista_tokens):
        self.datos = lista_tokens
        self.idx = 0

    @property
    def token_actual(self):
        return self.datos[self.idx] if self.idx < len(self.datos) else (None, None)

    def validar(self, tipo_esperado):
        tipo, valor = self.token_actual
        if tipo == tipo_esperado:
            self.idx += 1
            return valor
        return None

    def gramatica_S(self, root):
        nodo = root.vincular(ElementoArbol("S"))
        checkpoint = self.idx

        # Opción 1: S -> A B C
        if self.gramatica_A(nodo) and self.gramatica_B(nodo) and self.gramatica_C(nodo):
            return True

        # Opción 2: S -> D E
        self.idx = checkpoint
        nodo.subnodos.clear()
        if self.gramatica_D(nodo) and self.gramatica_E(nodo):
            return True

        # Falla total para S
        self.idx = checkpoint
        root.subnodos.remove(nodo)
        return False

    def gramatica_A(self, root):
        nodo = root.vincular(ElementoArbol("A"))
        mark = self.idx

        if self.validar("NUM2"):
            nodo.vincular(ElementoArbol("dos"))
            if self.gramatica_B(nodo) and self.validar("NUM3"):
                nodo.vincular(ElementoArbol("tres"))
                return True

        # Producción vacía A -> ε
        self.idx = mark
        nodo.subnodos.clear()
        nodo.vincular(ElementoArbol("ε"))
        return True

    def gramatica_B(self, root):
        nodo = root.vincular(ElementoArbol("B"))
        if self.gramatica_B_prima(nodo):
            return True
        root.subnodos.remove(nodo)
        return False

    def gramatica_B_prima(self, root):
        nodo = root.vincular(ElementoArbol("B'"))
        mark = self.idx

        if self.validar("NUM4"):
            nodo.vincular(ElementoArbol("cuatro"))
            if self.gramatica_C(nodo) and self.validar("NUM5"):
                nodo.vincular(ElementoArbol("cinco"))
                if self.gramatica_B_prima(nodo):
                    return True

        self.idx = mark
        nodo.subnodos.clear()
        nodo.vincular(ElementoArbol("ε"))
        return True

    def gramatica_C(self, root):
        nodo = root.vincular(ElementoArbol("C"))
        mark = self.idx

        if self.validar("NUM6"):
            nodo.vincular(ElementoArbol("seis"))
            if self.gramatica_A(nodo) and self.gramatica_B(nodo):
                return True

        self.idx = mark
        nodo.subnodos.clear()
        nodo.vincular(ElementoArbol("ε"))
        return True

    def gramatica_D(self, root):
        nodo = root.vincular(ElementoArbol("D"))
        mark = self.idx

        if self.validar("NUM1"):
            nodo.vincular(ElementoArbol("uno"))
            if self.gramatica_A(nodo) and self.gramatica_E(nodo):
                return True

        self.idx = mark
        nodo.subnodos.clear()
        if self.gramatica_B(nodo):
            return True

        self.idx = mark
        root.subnodos.remove(nodo)
        return False

    def gramatica_E(self, root):
        nodo = root.vincular(ElementoArbol("E"))
        if self.validar("NUM3"):
            nodo.vincular(ElementoArbol("tres"))
            return True
        root.subnodos.remove(nodo)
        return False

    def ejecutar(self):
        inicio = ElementoArbol("S")
        es_valido = self.gramatica_S(inicio) and self.token_actual[0] is None
        return es_valido, inicio

def set_tree_coords(node, level=0, leaf_count=[0]):
    """Calcula las posiciones X e Y de forma recursiva."""
    if not node.subnodos:
        node.coord_x = leaf_count[0]
        leaf_count[0] += 1
        node.coord_y = -level
    else:
        for child in node.subnodos:
            set_tree_coords(child, level + 1, leaf_count)
        # El padre se centra sobre sus hijos
        node.coord_x = sum(c.coord_x for c in node.subnodos) / len(node.subnodos)
        node.coord_y = -level

def render_logic(node, axis):
    """Dibuja los nodos y las conexiones."""
    es_vacio = node.tag == "ε"
    es_final = not node.subnodos
    
    # Selector de color
    bg_color = "#F0B27A" if es_vacio else ("#5DADE2" if es_final else "#AF7AC5")

    for child in node.subnodos:
        axis.plot([node.coord_x, child.coord_x], [node.coord_y, child.coord_y],
                  color="#BDC3C7", lw=1.2, zorder=1)
        render_logic(child, axis)

    blob = plt.Circle((node.coord_x, node.coord_y), 0.38, color=bg_color, zorder=2)
    axis.add_patch(blob)
    axis.text(node.coord_x, node.coord_y, node.tag, ha='center', va='center',
              fontsize=8, color='white', weight='bold', zorder=3)

def export_visual(root, raw_text, success):
    """Genera y guarda el archivo de imagen."""
    set_tree_coords(root, leaf_count=[0])
    
    # Recolectar nodos para ajustar límites
    flat_list = []
    def flatten(n):
        flat_list.append(n)
        for h in n.subnodos: flatten(h)
    flatten(root)

    xs, ys = [n.coord_x for n in flat_list], [n.coord_y for n in flat_list]
    
    ancho = max(10, (max(xs) - min(xs) + 2) * 0.7)
    alto = max(6, (max(ys) - min(ys) + 2) * 1.2)
    
    fig, ax = plt.subplots(figsize=(ancho, alto))
    ax.set_aspect('equal')
    ax.axis('off')
    
    render_logic(root, ax)

    res_txt = "ACEPTADA" if success else "RECHAZADA"
    res_col = "#27AE60" if success else "#C0392B"
    ax.set_title(f"Análisis: '{raw_text}' -> {res_txt}", color=res_col, weight='bold')

    # Leyenda personalizada
    patches = [
        mpatches.Patch(color="#AF7AC5", label="Variable"),
        mpatches.Patch(color="#5DADE2", label="Terminal"),
        mpatches.Patch(color="#F0B27A", label="Vacio (ε)")
    ]
    ax.legend(handles=patches, loc='best', prop={'size': 8})

    timestamp = str(time.time()).replace('.', '')[-5:]
    filename = f"out_{re.sub(r'\W+', '', raw_text)[:15]}_{timestamp}.png"
    plt.savefig(filename, dpi=120, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: falta archivo de entrada.")
        sys.exit(1)

    with open(sys.argv[1], "r") as f:
        content = [l.strip() for l in f if l.strip()]

    for line in content:
        tokens_found = obtener_tokens(line)
        engine = AnalizadorSintactico(tokens_found)
        is_ok, tree_root = engine.ejecutar()
        
        print(f"[{'OK' if is_ok else 'ERR'}] Procesado: {line}")
        export_visual(tree_root, line, is_ok)
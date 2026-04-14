import re
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# --- Componente de Análisis Léxico ---
class LexicalScanner:
    # Definición de tokens con identificadores alternativos
    DEF_TOKENS = {
        'T_ONE': r'\buno\b',
        'T_TWO': r'\bdos\b',
        'T_THREE': r'\btres\b',
        'T_FOUR': r'\bcuatro\b',
        'GAP': r'\s+'
    }

    def __init__(self, source_code):
        self.pattern = re.compile('|'.join(f'(?P<{k}>{v})' for k, v in self.DEF_TOKENS.items()))
        self.stream = self._tokenize(source_code)

    def _tokenize(self, text):
        # Genera la secuencia filtrando los espacios en blanco
        return [(m.lastgroup, m.group()) for m in self.pattern.finditer(text) if m.lastgroup != 'GAP']

# --- Estructura del Árbol de Derivación ---
class SyntaxNode:
    def __init__(self, name):
        self.identity = name
        self.children = []
        # Coordenadas espaciales para el renderizado
        self.x, self.y = 0, 0

    def attach(self, node):
        self.children.append(node)
        return node

# --- Procesador de Gramática (Backtracking) ---
class GrammarParser:
    def __init__(self, lexer_stream):
        self.data = lexer_stream
        self.ptr = 0

    def _lookahead(self):
        return self.data[self.ptr] if self.ptr < len(self.data) else (None, None)

    def _step(self, expected):
        kind, val = self._lookahead()
        if kind == expected:
            self.ptr += 1
            return val
        return None

    # Implementación de S → A B C S'
    def rule_main_S(self, parent):
        current = parent.attach(SyntaxNode("S"))
        snap = self.ptr

        if self.rule_A(current) and self.rule_B(current) and \
           self.rule_C(current) and self.rule_Sp(current):
            return True

        self.ptr = snap
        parent.children.remove(current)
        return False

    # Implementación de S' → uno S' | ε
    def rule_Sp(self, parent):
        current = parent.attach(SyntaxNode("S'"))
        snap = self.ptr

        if self._step("T_ONE"):
            current.attach(SyntaxNode("uno"))
            if self.rule_Sp(current):
                return True

        self.ptr = snap
        current.children.clear()
        current.attach(SyntaxNode("ε"))
        return True

    # Implementación de A → dos B C | ε
    def rule_A(self, parent):
        current = parent.attach(SyntaxNode("A"))
        snap = self.ptr

        if self._step("T_TWO"):
            current.attach(SyntaxNode("dos"))
            if self.rule_B(current) and self.rule_C(current):
                return True

        self.ptr = snap
        current.children.clear()
        current.attach(SyntaxNode("ε"))
        return True

    # Implementación de B → C tres | ε
    def rule_B(self, parent):
        current = parent.attach(SyntaxNode("B"))
        snap = self.ptr

        if self.rule_C(current):
            if self._step("T_THREE"):
                current.attach(SyntaxNode("tres"))
                return True

        self.ptr = snap
        current.children.clear()
        current.attach(SyntaxNode("ε"))
        return True

    # Implementación de C → cuatro B | ε
    def rule_C(self, parent):
        current = parent.attach(SyntaxNode("C"))
        snap = self.ptr

        if self._step("T_FOUR"):
            current.attach(SyntaxNode("cuatro"))
            if self.rule_B(current):
                return True

        self.ptr = snap
        current.children.clear()
        current.attach(SyntaxNode("ε"))
        return True

    def run(self):
        root = SyntaxNode("S")
        valid = self.rule_main_S(root) and self._lookahead()[0] is None
        return valid, root

# --- Motor Gráfico del Árbol ---
def compute_positions(node, depth=0, leaf_idx=[0]):
    if not node.children:
        node.x = leaf_idx[0]
        leaf_idx[0] += 1
        node.y = -depth
        return
    
    for child in node.children:
        compute_positions(child, depth + 1, leaf_idx)
    
    node.x = sum(c.x for c in node.children) / len(node.children)
    node.y = -depth

def render_tree(node, axis):
    # Estilo visual: Nodos hoja vs Nodos internos
    is_null = node.identity == "ε"
    is_leaf = not node.children
    
    # Paleta neón/oscuro
    node_color = "#FF007F" if is_null else ("#00FFD1" if is_leaf else "#7000FF")

    for child in node.children:
        axis.plot([node.x, child.x], [node.y, child.y], 
                  color="#444444", lw=1.5, ls='-', zorder=1)
        render_tree(child, axis)

    # Dibujo de la entidad nodo
    circle = plt.Circle((node.x, node.y), 0.3, color=node_color, ec="#222222", zorder=2)
    axis.add_patch(circle)
    axis.text(node.x, node.y, node.identity, ha='center', va='center',
              fontsize=8, color='white', weight='bold', zorder=3)

def generate_output(root, original_txt, status):
    compute_positions(root, leaf_idx=[0])
    
    # Recopilar todos los nodos para encuadre
    bag = []
    def collect(n):
        bag.append(n)
        for c in n.children: collect(c)
    collect(root)

    x_coords = [n.x for n in bag]
    y_coords = [n.y for n in bag]

    # Estética de la figura (Dark Background)
    fig, ax = plt.subplots(figsize=(max(9, len(x_coords)*0.5), 6), facecolor='#121212')
    ax.set_facecolor('#121212')
    ax.set_aspect("equal")
    ax.axis("off")

    render_tree(root, ax)

    res_label = "VALID" if status else "INVALID"
    res_color = "#00FF00" if status else "#FF3131"
    ax.set_title(f"Parsing: {original_txt}\nResult: {res_label}", 
                 color='white', pad=20, weight='bold')

    # Leyenda técnica
    labels = [
        mpatches.Patch(color="#7000FF", label="Non-Terminal"),
        mpatches.Patch(color="#00FFD1", label="Terminal"),
        mpatches.Patch(color="#FF007F", label="Null/Epsilon")
    ]
    lg = ax.legend(handles=labels, loc="lower right", facecolor='#1E1E1E', edgecolor='#444444')
    plt.setp(lg.get_texts(), color='w')

    plt.tight_layout()
    plt.savefig(f"analisis_{int(time.time())}.png", dpi=130, facecolor=fig.get_facecolor())
    plt.close()

# --- Punto de Entrada ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Sintaxis: python script.py <filename>")
        sys.exit(1)

    with open(sys.argv[1], "r") as doc:
        lines = [l.strip() for l in doc if l.strip()]

    for raw in lines:
        scanner = LexicalScanner(raw)
        engine = GrammarParser(scanner.stream)
        ok, tree_data = engine.run()
        
        print(f"[{'ACCEPT' if ok else 'REJECT'}] Processing: '{raw}'")
        generate_output(tree_data, raw, ok)
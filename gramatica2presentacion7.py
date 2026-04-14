import re
import sys
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

SIMBOLOS = {
    "T1": r"\buno\b",
    "T2": r"\bdos\b",
    "T3": r"\btres\b",
    "T4": r"\bcuatro\b",
    "T5": r"\bcinco\b",
    "T6": r"\bseis\b",
    "T7": r"\bsiete\b",
    "SKIP": r"[ \t]+",
}

REGEX_MASTER = re.compile("|".join(f"(?P<{k}>{v})" for k, v in SIMBOLOS.items()))

def lexer_proc(cadena):
    """Genera la lista de tokens filtrando espacios."""
    return [(m.lastgroup, m.group()) for m in REGEX_MASTER.finditer(cadena) if m.lastgroup != "SKIP"]

class PuntoSintactico:
    def __init__(self, nombre):
        self.label = nombre
        self.branches = []
        self.posX = 0
        self.posY = 0

    def link(self, child_node):
        self.branches.append(child_node)
        return child_node

class EngineSintactico:
    def __init__(self, stream):
        self.stream = stream
        self.cursor = 0

    def get_current(self):
        return self.stream[self.cursor] if self.cursor < len(self.stream) else (None, None)

    def match(self, expected_type):
        tipo, valor = self.get_current()
        if tipo == expected_type:
            self.cursor += 1
            return valor
        return None

    def rule_S(self, parent):
        node = parent.link(PuntoSintactico("S"))
        save = self.cursor

        if self.rule_B(node):
            if self.match("T1"):
                node.link(PuntoSintactico("uno"))
                return True

        self.cursor = save
        node.branches.clear()
        if self.match("T2"):
            node.link(PuntoSintactico("dos"))
            if self.rule_C(node):
                return True

        self.cursor = save
        node.branches.clear()
        node.link(PuntoSintactico("ε"))
        return True

    def rule_A(self, parent):
        node = parent.link(PuntoSintactico("A"))
        save = self.cursor

        if self.match("T2"):
            node.link(PuntoSintactico("dos"))
            if self.rule_C(node) and self.match("T3"):
                node.link(PuntoSintactico("tres"))
                if self.rule_B(node) and self.rule_C(node) and self.rule_Ap(node):
                    return True

        self.cursor = save
        node.branches.clear()
        if self.match("T1"):
            node.link(PuntoSintactico("uno"))
            if self.match("T3"):
                node.link(PuntoSintactico("tres"))
                if self.rule_B(node) and self.rule_C(node) and self.rule_Ap(node):
                    return True

        self.cursor = save
        node.branches.clear()
        if self.match("T3"):
            node.link(PuntoSintactico("tres"))
            if self.rule_B(node) and self.rule_C(node) and self.rule_Ap(node):
                return True

        self.cursor = save
        node.branches.clear()
        if self.match("T4"):
            node.link(PuntoSintactico("cuatro"))
            if self.rule_Ap(node):
                return True

        self.cursor = save
        node.branches.clear()
        if self.rule_Ap(node):
            return True

        parent.branches.remove(node)
        return False

    def rule_Ap(self, parent):
        node = parent.link(PuntoSintactico("A'"))
        save = self.cursor

        if self.match("T5"):
            node.link(PuntoSintactico("cinco"))
            if self.rule_C(node) and self.match("T6"):
                node.link(PuntoSintactico("seis"))
                if self.match("T1"):
                    node.link(PuntoSintactico("uno"))
                    if self.match("T3"):
                        node.link(PuntoSintactico("tres"))
                        if self.rule_B(node) and self.rule_C(node) and self.rule_Ap(node):
                            return True
        
        self.cursor = save
        node.branches.clear()
        node.link(PuntoSintactico("ε"))
        return True

    def rule_B(self, parent):
        node = parent.link(PuntoSintactico("B"))
        save = self.cursor

        if self.rule_A(node):
            if self.match("T5"):
                node.link(PuntoSintactico("cinco"))
                if self.rule_C(node) and self.match("T6"):
                    node.link(PuntoSintactico("seis"))
                    return True

        self.cursor = save
        node.branches.clear()
        node.link(PuntoSintactico("ε"))
        return True

    def rule_C(self, parent):
        node = parent.link(PuntoSintactico("C"))
        save = self.cursor

        if self.match("T7"):
            node.link(PuntoSintactico("siete"))
            if self.rule_B(node):
                return True

        self.cursor = save
        node.branches.clear()
        node.link(PuntoSintactico("ε"))
        return True

    def process(self):
        root = PuntoSintactico("S")
        status = self.rule_S(root) and self.get_current()[0] is None
        return status, root

def set_layout(node, depth=0, count=[0]):
    if not node.branches:
        node.posX = count[0]
        count[0] += 1
        node.posY = -depth
        return
    for b in node.branches:
        set_layout(b, depth + 1, count)
    node.posX = sum(b.posX for b in node.branches) / len(node.branches)
    node.posY = -depth

def paint_tree(node, axis):
    is_leaf = not node.branches
    # Nuevos colores: Verde suave para hojas, Coral para vacío, Azul acero para nodos
    bg = "#F1948A" if node.label == "ε" else ("#82E0AA" if is_leaf else "#5DADE2")

    for b in node.branches:
        axis.plot([node.posX, b.posX], [node.posY, b.posY], color="#ABB2B9", lw=1, zorder=1)
        paint_tree(b, axis)

    dot = plt.Circle((node.posX, node.posY), 0.35, color=bg, ec="black", lw=1, zorder=2)
    axis.add_patch(dot)
    axis.text(node.posX, node.posY, node.label, ha="center", va="center", 
              fontsize=7, weight="bold", color="black", zorder=3)

def create_image(root_node, text, is_valid):
    set_layout(root_node, count=[0])
    
    all_n = []
    def walk(n):
        all_n.append(n)
        for b in n.branches: walk(b)
    walk(root_node)

    xs = [n.posX for n in all_n]
    ys = [n.posY for n in all_n]

    fig, ax = plt.subplots(figsize=(max(8, len(xs)*0.5), max(5, abs(min(ys))*1.2)))
    ax.set_aspect("equal")
    ax.axis("off")
    paint_tree(root_node, ax)

    title_str = f"ENTRADA: {text} | {'VÁLIDA' if is_valid else 'ERROR'}"
    ax.set_title(title_str, color="#1B4F72", weight="black")

    legend_items = [
        mpatches.Patch(color="#5DADE2", label="Variable (No Terminal)"),
        mpatches.Patch(color="#82E0AA", label="Token (Terminal)"),
        mpatches.Patch(color="#F1948A", label="Vacio (ε)")
    ]
    ax.legend(handles=legend_items, loc="lower left", fontsize=7)

    plt.tight_layout()
    plt.savefig(f"tree_{int(time.time())}.png", dpi=100)
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Indique el archivo de texto.")
        sys.exit(1)

    with open(sys.argv[1], "r") as doc:
        for entry in doc:
            clean_entry = entry.strip()
            if not clean_entry: continue
            
            lexemes = lexer_proc(clean_entry)
            analyzer = EngineSintactico(lexemes)
            success, tree = analyzer.process()
            
            print(f"[{'PASSED' if success else 'FAILED'}] -> {clean_entry}")
            create_image(tree, clean_entry, success)

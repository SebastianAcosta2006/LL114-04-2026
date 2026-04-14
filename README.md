Analizador Sintáctico Descendente Recursivo Enfoque LL1

Este proyecto presenta la implementación de tres analizadores sintácticos descendentes recursivos, cada uno diseñado para trabajar con una gramática específica. Cada analizador procesa cadenas de entrada, determina si pertenecen al lenguaje definido por su gramática y genera como resultado un árbol de derivación en formato visual. El objetivo principal es aplicar el modelo LL1.

Requisitos para ejecutarlo en ubuntu
Para ejecutar correctamente el proyecto se necesita contar con
python instalado
Librería matplotlib para la generación de los árboles

Instalación en Ubuntu:
sudo apt install python3-matplotlib

Organización del Proyecto

La estructura de archivos está organizada de la siguiente manera:

LL1
├── README.md
├── entrada1.txt
├── entrada2.txt
├── entrada3.txt
├── gramatica1presentacion7.py
├── gramatica2presentacion7.py
├── gramatica3presentacion7.py
├── INFORME DE LL1

Cada parser corresponde a una gramática distinta y cada archivo de entrada contiene las cadenas que serán evaluadas.

Forma de Ejecución

Cada programa recibe como parámetro un archivo de texto con las cadenas a analizar. El sistema procesa cada línea de manera independiente, indicando en consola si la cadena es válida o no, y generando una imagen PNG con el árbol sintáctico correspondiente.

Ejemplo de ejecución:

python3 parser_gramatica1.py entrada1.txt
python3 parser_gramatica2.py entrada2.txt
python3 parser_gramatica3.py entrada3.txt

Definición de Gramáticas
Gramática 1
<img width="321" height="473" alt="image" src="https://github.com/user-attachments/assets/8b7458eb-86fd-45e3-a8ee-cc18063799a0" />


En su forma original, esta gramática presentaba recursividad por izquierda en la producción de B. Para adaptarla al enfoque LL(1), se introdujo el no terminal auxiliar B', eliminando así el problema y permitiendo un análisis determinista.

Gramática 2
<img width="311" height="457" alt="image" src="https://github.com/user-attachments/assets/f62ebce3-d845-49fd-9844-8e96a7857356" />


Esta gramática inicialmente contenía recursividad indirecta por izquierda, generada por dependencias entre varios no terminales. Para resolverlo, se expandieron las producciones hasta hacer explícita la recursividad directa en A, la cual fue eliminada mediante la introducción de A'. El resultado final permite su uso bajo el modelo LL(1).

Gramática 3
<img width="237" height="358" alt="image" src="https://github.com/user-attachments/assets/afd6d228-db47-4fdb-bfc2-25cbc0a2c3b2" />

En este caso, la gramática original tenía recursividad directa en S, la cual fue eliminada con la inclusión del no terminal S' Sin embargo aun presenta conflictos en los conjuntos de predicción debido a la relación recursiva entre B y C. Por esta razón, no es completamente LL(1) y requiere el uso de backtracking en el parser para evaluar correctamente las cadenas.

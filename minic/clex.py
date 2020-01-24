# clexer.py
# coding: utf-8
r"""
Proyecto 1 - Escribir un Lexer
==============================

En este primer proyecto, usted debe escribir un lexer sencillo para
un lenguaje de instrucciones: MiniC.

El proyecto es basado en código que usted debe leer (en este archivo)
y completar. Por favor, lea el contenido completo de este archivo y
cuidadosamente complete los pasos indicados como comentarios.

Revisión:
---------
El proceso del analizador léxico es la de tomar el texto de entrada y
descomponerlo en un flujo de símbolos (tokens). Cada token es como una
palabra válida del diccionario.  Esencialmente, el papel del lexer es
simplemente asegurarse de que el texto de entrada se compone de símbolos
válidos antes de cualquier procesamiento adicional relacionado con el
análisis sintáctico.

Cada token es definido por una expresión regular. Por lo tanto, su
principal tarea en este primer proyecto es definir un conjunto de
expresiones regulares para el lenguaje. El trabajo actual del análisis
léxico deberá ser manejado por SLY.

Especificación:
---------------
Su lexer debe reconocer los siguientes tokens (símbolos). El nombre a la
izquierda es el nombre del token, el valor en la derecha es el texto de
coincidencia.

Palabras Reservadas:
	INT      : 'int'
	IF       : 'if'
	WHILE    : 'while'

Identificadores: (Las mismas reglas como para Python)
	IDENT    : El texto inicia con una letra o '_', seguido por
			   cualquier número de letras, dígitos o guión bajo.

Operadores y Delimitadores:
	PLUS    : '+'
	MINUS   : '-'
	TIMES   : '*'
	DIVIDE  : '/'
	ASSIGN  : '='
	SEMI    : ';'
	LPAREN  : '('
	RPAREN  : ')'
	COMMA   : ','

Literales:
	INTEGER : '123' (decimal)
              '0123'  (octal)
              '0x123' (hex)

	FLOAT   : '1.234'
              '1.234e1'
              '1.234e+1'
              '1.234e-1'
              '1e2'
              '.1234'
              '1234.'

Comentarios: Para ser ignorados por el lexer
	//             Ignora el resto de la línea
	/* ... */      Omite un bloque (sin anidamiento permitido)

Errores: Su lexer debe reportar los siguientes mensajes de error:
	lineno: Carácter ilegal 'c'
	lineno: Cadena sin terminar
	lineno: Comentario sin terminar
	lineno: Cadena de código de escape malo '\..'

Pruebas
-------
Para el desarrollo inicial, trate de correr el lexer sobre un
archivo de entrada de ejemplo, como:

	bash % python minic.tokenizer.py nibless.c

Estudie cuidadosamente la salida del lexer y asegúrese que tiene
sentido. Una vez que este razonablemente contento con la salida,
intente ejecutar alguna de las pruebas mas difíciles:

	bash % python minic.tokenizer.py testlex1.c
	bash % python minic.tokenizer.py testlex2.c

Bono: ¿Cómo haría usted para convertir estas pruebas en pruebas
unitarias adecuadas?
"""

# ----------------------------------------------------------------------
# El siguiente import carga una función error(lineno,msg) que se debe
# utilizar para informar de todos los mensajes de error emitidos por su
# lexer. Las pruebas unitarias y otras características del compilador
# confiarán en esta función. Ver el archivo errors.py para más documentación
# acerca del mecanismo de manejo de errores.
from errors import error

# ----------------------------------------------------------------------
# El paquete SLY. https://github.com/dabeaz/sly
import sly


class Lexer(sly.Lexer):
    # Conjunto de palabras reservadas. Este conjunto enumera todos los
    # nombres especiales utilizados en el lenguaje, como 'if', 'else',
    # 'while', etc.

    keywords = {
        'if', 'else', 'while', 'for', 'break', 'return', 'print', 'new',
        'size', 'void', 'bool', 'int', 'float', 'char', 'true', 'false',
    }

    # ----------------------------------------------------------------------
    # Conjunto de tokens. Este conjunto identifica la lista completa de
    # nombres de tokens que reconocerá su lexer. No cambie ninguno de estos
    # nombres.

    tokens = {
        # keywords
        *{kw.upper() for kw in keywords},
        IDENT, INT_LIT, FLOAT_LIT, CHAR_LIT, STRING_LIT, BOOL_LIT,
        ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN, MODASSIGN,
        PLUS, MINUS, TIMES, DIVIDE, MOD,
        LE, GE, EQ, NE, OR, AND, INC, DEC
    }

    literals = '(){}[];,.+-*/%<>=!'

    # ----------------------------------------------------------------------
    # Caracteres escape no permitidos

    disallowed_characters = {'\\a', '\\b', '\\e', '\\f', '\\r', '\\v'}

    # Caracteres ignorados (whitespace)
    #
    # Los siguientes caracteres son ignorados completamente por el lexer.
    # No lo cambie.

    ignore = ' \t\r'

    # ----------------------------------------------------------------------
    # Patrones ignorados. Complete las expresiones regulares a continuación
    # para ignorar los comentarios

    ignore_line_comment = r'//.*'
    ignore_block_comment = r'/\*[^*]*\*+(?:[^*/][^*]*\*+)*/'

    def ignore_block_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'/\*(.|\n)*')
    def error_comment(self, t):
        error(self.lineno, "Unterminated comment")

    # ----------------------------------------------------------------------
    #                           *** DEBE COMPLETAR ***
    #
    # Escriba las expresiones regulares que se indican a continuación.
    #
    # Tokens para símbolos simples: + - * / = ( ) ; < >, etc.
    #
    # Precaución: El orden de las definiciones es importante. Los símbolos
    # más largos deben aparecer antes de los símbolos más cortos que son
    # una sub-cadena (por ejemplo, el patrón para <= debe ir antes de <).

    INC = r'\+\+'
    DEC = r'--'
    ADDASSIGN = r'\+='
    SUBASSIGN = r'-='
    MULASSIGN = r'\*='
    DIVASSIGN = r'/='
    MODASSIGN = r'%='
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    LE = r'<='
    GE = r'>='
    EQ = r'=='
    NE = r'!='
    OR = r'\|\|'
    AND = r'&&'

    # ----------------------------------------------------------------------
    #                           *** DEBE COMPLETAR ***
    #
    # escriba las expresiones regulares y el código adicional a continuación
    #
    # Tokens para literales, INTEGER, FLOAT, STRING.
    #
    # Constante de punto flotante. Debe reconocer los números de punto
    # flotante en los siguientes formatos:
    #
    #   1.23
    #   123.
    #   .123
    #
    # Bonificación: reconocer números flotantes en notación científica
    #
    #   1.23e1
    #   1.23e+1
    #   1.23e-1
    #   1e1
    #
    # El valor debe ser convertir en un float de Python cuando se lea

    # Constante entera
    #     1234             (decimal)
    #
    # El valor debe ser convertido a un int de Python cuando se lea.
    #
    # Bonificación. Reconocer enteros en diferentes bases tales como
    # 0x1a, 013 o 0b111011.

    # Floats en o sin notación científica y enteros en notación científica
    # https://regex101.com/r/4kjMm0/1
    FLOAT_LIT = r'(\d*\.\d+|\d+\.\d*)([eE][\+-]?\d+)?|\d+[eE][\+-]?\d+'

    # Ints en base: octal, hexadecimal, binaria, decimal; y de un cero a varios
    INT_LIT = r'\b0+[1-7][0-7]*\b|\b0[xX][0-9a-fA-F]+\b|\b0[bB][01]+\b|\b[1-9]\d*\b|\b0+\b'

    STRING_LIT = r'\"(\\.|[^\n\"\\])*\"'

    # Chars básicos sin \ ó ', chars con escape \a \b etc, y escapes octal y hex
    # https://regex101.com/r/R35PuU/1
    CHAR_LIT = r'\'([^\'\\\n]|\\[abfnrtv0\\\'\"\?]|\\[0-3][0-7]{2}|\\x[0-9a-fA-F]{2})\''

    BOOL_LIT = r'\b(true|false)\b'

    def FLOAT_LIT(self, t):
        t.value = float(t.value)
        return t

    def INT_LIT(self, t):
        if t.value.startswith(('0b', '0B')):
            t.value = int(t.value, 2)  # Binario
        elif t.value.startswith(('0x', '0X')):
            t.value = int(t.value, 16)  # Hexadecimal
        elif t.value.startswith('0'):
            if int(t.value) == 0:
                t.value = int(t.value)  # Cero
            else:
                t.value = int(t.value, 8)  # Octal
        else:
            t.value = int(t.value)  # Decimal
        return t

    def STRING_LIT(self, t):
        # Agrupar los caracteres no permitidos encontrados en un string
        chars = ', '.join("'{0}'".format(char) for char in self.disallowed_characters if char in t.value)
        if chars:
            self.error_escape(chars)
        else:
            return t

    @_(r'\"[^\n\"]*')
    def error_string(self, t):
        error(self.lineno, "Unterminated string")

    @_(r'\'\\\'|\'\\\s')
    def error_char(self, t):
        error(self.lineno, "Missing terminating ' character")

    # ----------------------------------------------------------------------
    #                           *** DEBE COMPLETAR ***
    #
    # escribir la expresión regular y agregar palabras reservadas
    #
    # Identificadores y palabras reservadas
    #
    # Concuerde con un identificador. Los identificadores siguen las mismas
    # reglas que Python. Es decir, comienzan con una letra o un guión bajo (_)
    # y pueden contener una cantidad arbitraria de letras, dígitos o guiones
    # bajos después de eso.
    # Las palabras reservadas del lenguaje como "if" y "while" también se
    # combinan como identificadores. Debe capturar estos y cambiar su tipo
    # de token para que coincida con la palabra clave adecuada.

    IDENT = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'

    IDENT['if'] = IF
    IDENT['else'] = ELSE
    IDENT['while'] = WHILE
    IDENT['for'] = FOR
    IDENT['break'] = BREAK
    IDENT['return'] = RETURN
    IDENT['print'] = PRINT
    IDENT['new'] = NEW
    IDENT['size'] = SIZE
    IDENT['void'] = VOID
    IDENT['bool'] = BOOL
    IDENT['int'] = INT
    IDENT['float'] = FLOAT
    IDENT['char'] = CHAR
    IDENT['true'] = TRUE
    IDENT['false'] = FALSE

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    # ----------------------------------------------------------------------
    # Manejo de errores de caracteres incorrectos
    def error(self, t):
        error(self.lineno, "Illegal character %r" % t.value[0])
        self.index += 1

    def error_escape(self, c):
        error(self.lineno, f"Disallowed characters {c} within string")


# ----------------------------------------------------------------------
#                   NO CAMBIE NADA POR DEBAJO DE ESTA PARTE
#
# Use este programa principal para probar/depurar su Lexer. Ejecútelo
# usando la opción -m
#
#    bash% python3 -m clex filename.c
#
# ----------------------------------------------------------------------
def main():
    """
    Para propósitos de depuración
    """
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: python3 -m clex filename\n')
        raise SystemExit(1)

    lexer = Lexer()
    text = open(sys.argv[1]).read()
    for tok in lexer.tokenize(text):
        print(tok)


if __name__ == '__main__':
    main()

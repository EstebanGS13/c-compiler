# clexer.py
# coding: utf-8
r'''
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
palabra válida del diccionario.  Escencialmente, el papel del lexer es 
simplemente asegurarse de que el texto de entrada se compone de símbolos 
válidos antes de cualquier procesamiento adicional relacionado con el 
análisis sintático.

Cada token es definido por una expresion regular. Por lo tanto, su 
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
						 cualquier número de letras, digitos o guión bajo.

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
	lineno: Caracter ilegal 'c' 
	lineno: Cadena sin terminar
	lineno: Comentario sin terminar
	lineno: Cadena de código de escape malo '\..'

Pruebas
-------
Para el desarrollo inicial, trate de correr el lexer sobre un 
archivo de entrada de ejemplo, como:

	bash % python minic.tokenizer.py nibless.c

Estudie cuidadosamente la salida del lexer y asegúrese que tiene 
sentido. Una vez que este rasonablemente contento con la salida, 
intente ejecutar alguna de las pruebas mas difíciles:

	bash % python minic.tokenizer.py testlex1.c
	bash % python minic.tokenizer.py testlex2.c

Bono: ¿Cómo haría usted para convertir estas pruebas en pruebas 
unitarias adecuadas?
'''

# ----------------------------------------------------------------------
# El siguiente import carga una función error(lineno,msg) que se debe
# utilizar para informar de todos los mensajes de error emitidos por su
# lexer. Las pruebas unitarias y otras caracteristicas del compilador
# confiarán en esta función. Ver el archivo errors.py para más documentación
# acerca del mecanismo de manejo de errores.
from errors import error

# ----------------------------------------------------------------------
# El paquete SLY. https://github.com/dabeaz/sly
import sly


class Lexer(sly.Lexer):
    # -------
    # Conjunto de palabras reservadas.  Este conjunto enumera todos los
    # nombres especiales utilizados en el lenguaje, como 'if', 'else',
    # 'while', etc.
    keywords = {
        'if', 'else', 'while', 'for', 'break',
        'return', 'void', 'bool', 'int', 'float',
        'char', 'new', 'size', 'true', 'false',
    }

    # ----------------------------------------------------------------------
    # Conjunto de tokens. Este conjunto identifica la lista completa de
    # nombres de tokens que reconocerá su lexer. No cambie ninguno de estos
    # nombres.
    tokens = {
        # keywords
        * { kw.upper() for kw in keywords },

        # Identificador
        IDENT, INT_LIT, FLOAT_LIT, CHAR_LIT, STRING_LIT, BOOL_LIT,
        PREINC, PREDEC, POSTINC, POSTDEC,
        ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN, MODASSIGN,
        PLUS, MINUS, TIMES, DIVIDE, MOD,
        LE, LT, GE, GT, EQ, ASSIGN, NE, OR, AND
    }

    literals = '(){}[];,.+-*/%#<>=!'

    # ----------------------------------------------------------------------
    # Caracteres ignorados (whitespace)
    #
    # Los siguientes caracteres son ignorados completamente por el lexer.
    # No lo cambie.

    ignore = ' \t\r'

    # ----------------------------------------------------------------------
    # Patrones ignorados.  Complete las expresiones regulares a continuación
    # para ignorar los comentarios

    ignore_line_comment = r'//.*'
    ignore_block_comment = r'/\*[^*]*\*+(?:[^*/][^*]*\*+)*/|/\*(.|\n)*\*/'

    def ignore_block_comment(self, t):
        self.lineno += t.value.count('\n')

    @_(r'/\*(.|\n)*')
    def error_comment(self, t):
        error(self.lineno, 'Comentario sin terminar')

    # ----------------------------------------------------------------------
    #                           *** DEBE COMPLETAR ***
    #
    # escriba las expresiones regulares que se indican a continuación.
    #
    # Tokens para símbolos simples: + - * / = ( ) ; < >, etc.
    #
    # Precaución: El orden de las definiciones es importante. Los símbolos
    # más largos deben aparecer antes de los símbolos más cortos que son
    # una subcadena (por ejemplo, el patrón para <= debe ir antes de <).

    PREINC = r'\+\+(?= *?[a-zA-Z_][a-zA-Z0-9_]*)'
    PREDEC = r'--(?= *?[a-zA-Z_][a-zA-Z0-9_]*)'
    # regex lookahead doesn't work with + or *
    POSTINC = r'\+\+' # r'(?<=[a-zA-Z_][a-zA-Z0-9_]* *?)\+\+'
    POSTDEC = r'--'
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
    LT = r'<'
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    ASSIGN = r'='
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
    #s
    #     1234             (decimal)
    #
    # El valor debe ser convertido a un int de Python cuando se lea.
    #
    # Bonificación. Reconocer enteros en diferentes bases tales como
    # 0x1a, 0o13 o 0b111011.

    FLOAT_LIT = r'\d*\.\d+|\d+\.\d*'
    INT_LIT = r'[1-9]\d*|0[1-7][0-7]*|0[xX][0-9a-fA-F]+|0[bB][01]+|\b0\b'
    CHAR_LIT = r'\'.\''
    STRING_LIT = r'\"(\\.|[^"\\])*\"'   # simple r'\".*\"'
    BOOL_LIT = r'(true|false)$'

    def FLOAT_LIT(self, t):
        t.value = float(t.value)
        return t

    def INT_LIT(self, t):
        if ('0b' in t.value) or ('0B' in t.value):
            t.value = int(t.value, 2)
        elif len(t.value) > 1 and t.value[0] == '0' and t.value[1] in '1234567':
            t.value = int(t.value, 8)
        elif ('0x' in t.value) or ('0X' in t.value):
            t.value = int(t.value, 16)
        else:
            t.value = int(t.value)
        return t

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

    IDENT = r'[a-zA-Z_][a-zA-Z0-9_]*'

    IDENT['if'] = IF
    IDENT['else'] = ELSE
    IDENT['while'] = WHILE
    IDENT['for'] = FOR
    IDENT['break'] = BREAK
    IDENT['return'] = RETURN
    IDENT['void'] = VOID
    IDENT['bool'] = BOOL
    IDENT['int'] = INT
    IDENT['float'] = FLOAT
    IDENT['char'] = CHAR
    IDENT['new'] = NEW
    IDENT['size'] = SIZE
    IDENT['true'] = TRUE
    IDENT['false'] = FALSE

    @_(r'\n')
    def newline(self, t):
        self.lineno += 1

    # ----------------------------------------------------------------------
    # Manejo de errores de caracteres incorrectos
    def error(self, t):
        error(self.lineno, 'Caracter Ilegal %r' % t.value[0])
        self.index += 1


# ----------------------------------------------------------------------
#                   NO CAMBIE NADA POR DEBAJO DE ESTA PARTE
#
# Use este programa principal para probar/depurar su Lexer. Ejecutelo 
# usando la opción -m
#
#    bash% python3 -m minic.clexer filename.c
#
# ----------------------------------------------------------------------
def main():
    '''
    main. Para propósitos de depuracion
    '''
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write('Uso: python3 -m clexer filename\n')
        raise SystemExit(1)

    lexer = Lexer()
    text = open(sys.argv[1]).read()
    for tok in lexer.tokenize(text):
        print(tok)
    # data = '''
    # //Counting
    # x = 0;
    # float a = 0
    # for(int i = 0; i < 20; i++) {
    #     printf("%d", i);
    #     a = a + i + 0.15
    # }
    # data = '''
    # /* esto
    # es un bloque de
    # comentario */
    # while (x < 10) {
    #     print x:
    #     x = x + 1;
    # }
    # '''
    # data = '123.r'
    # data = '''   '\n' '''
    # data = '''bool truefalse = true'''
    # data = '''//qwe\nrty'''
    # lexer = Lexer()
    # for tok in lexer.tokenize(data):
    #     print(tok)

if __name__ == '__main__':
    main()

# ircode.py
"""
Proyecto 4
==========
En este proyecto, va a convertir el AST en un código de máquina
intermedio basado en el código de 3 direcciones. Hay algunas partes
importantes que necesitarás para que esto funcione. Por favor,
lea atentamente antes de comenzar:

Una Maquina "Virtual"
=====================
Una CPU normalmente consiste en registros y un pequeño conjunto de
códigos de operación básicos para realizar cálculos matemáticos,
cargar/almacenar valores desde la memoria y un flujo de control
básico (ramas, saltos, etc.). Por ejemplo, suponga que desea evaluar
una operación como esta:

    a = 2 + 3 * 4 - 5

En una CPU, podría descomponerse en instrucciones de bajo nivel
como esta:

    MOVI   #2, R1
    MOVI   #3, R2
    MOVI   #4, R3
    MULI   R2, R3, R4
    ADDI   R4, R1, R5
    MOVI   #5, R6
    SUBI   R5, R6, R7
    STOREI R7, "a"

Cada instrucción representa una sola operación, como sumar, multiplicar, etc.
Siempre hay dos operandos de entrada y un destino.

Las CPU también cuentan con un pequeño conjunto de tipos de datos centrales,
como los enteros, bytes, y floats.  Hay instrucciones dedicadas para cada tipo.
Por ejemplo:

    ADDI   R1, R2, R3        ; Integer add
    ADDF   R4, R5, R6        ; Float add

A menudo hay una desconexión entre los tipos utilizados en el lenguaje
de programación de origen y el IRCode generado.  Por ejemplo, una máquina
de destino solo puede tener enteros y flotantes.  Para representar un
valor como un booleano, debe representarlo como uno de los tipos nativos,
como un entero.  Este es un detalle de implementación que los usuarios
no se preocuparán (nunca lo verán, pero tendrá que preocuparse por eso
en el compilador).

Esta es una especificación del conjunto de instrucciones para nuestro
código de IR:

    MOVI   value, target       ;  Load a literal integer
    VARI   name                ;  Declare an integer variable
    ALLOCI name                ;  Allocate an integer variable on the stack
    LOADI  name, target        ;  Load an integer from a variable
    STOREI target, name        ;  Store an integer into a variable
    ADDI   r1, r2, target      ;  target = r1 + r2
    SUBI   r1, r2, target      ;  target = r1 - r2
    MULI   r1, r2, target      ;  target = r1 * r2
    DIVI   r1, r2, target      ;  target = r1 / r2
    PRINTI source              ;  print source  (debugging)
    CMPI   op, r1, r2, target  ;  Compare r1 op r2 -> target
    AND    r1, r2, target      :  target = r1 & r2
    OR     r1, r2, target      :  target = r1 | r2
    XOR    r1, r2, target      :  target = r1 ^ r2
    ITOF   r1, target          ;  target = float(r1)

    MOVF   value, target       ;  Load a literal float
    VARF   name                ;  Declare a float variable
    ALLOCF name                ;  Allocate a float variable on the stack
    LOADF  name, target        ;  Load a float from a variable
    STOREF target, name        ;  Store a float into a variable
    ADDF   r1, r2, target      ;  target = r1 + r2
    SUBF   r1, r2, target      ;  target = r1 - r2
    MULF   r1, r2, target      ;  target = r1 * r2
    DIVF   r1, r2, target      ;  target = r1 / r2
    PRINTF source              ;  print source (debugging)
    CMPF   op, r1, r2, target  ;  r1 op r2 -> target
    FTOI   r1, target          ;  target = int(r1)

    MOVB   value, target       ; Load a literal byte
    VARB   name                ; Declare a byte variable
    ALLOCB name                ; Allocate a byte variable
    LOADB  name, target        ; Load a byte from a variable
    STOREB target, name        ; Store a byte into a variable
    PRINTB source              ; print source (debugging)
    BTOI   r1, target          ; Convert a byte to an integer
    ITOB   r2, target          ; Truncate an integer to a byte
    CMPB   op, r1, r2, target  ; r1 op r2 -> target

Estas son algunas instrucciones de control de flujo

    LABEL  name                  ; Declare a label
    BRANCH label                 ; Unconditionally branch to label
    CBRANCH test, label1, label2 ; Conditional branch to label1 or label2 depending on test being 0 or not
    CALL   name, arg0, arg1, ... argN, target    ; Call a function name(arg0, ... argn) -> target
    RET    r1                    ; Return a result from a function

Single Static Assignment
========================
En una CPU real, hay un número limitado de registros de CPU.
En nuestra memoria virtual, vamos a suponer que la CPU tiene un número
infinito de registros disponibles. Además, asumiremos que cada registro
solo se puede asignar una vez.

Este estilo en particular se conoce como asignación única estática (SSA).
A medida que genere instrucciones, mantendrá un contador activo que se
incrementa cada vez que necesita una variable temporal.
El ejemplo en la sección anterior ilustra esto.

Su Tarea
========
Su tarea es la siguiente: escriba una clase AST Visitor() que tome
un programa y lo aplana a una sola secuencia de instrucciones de código
SSA representado como tuplas de la forma

       (operation, operands, ..., destination)
"""

from collections import ChainMap
from checker import print_node
import cast

IR_TYPE_MAPPING = {
    'int': 'I',
    'float': 'F',
    'char': 'B',
    'bool': 'I',
    'void': 'V'
}

OP_CODES = ChainMap({
    'mov': 'MOV',
    '+': 'ADD',
    '-': 'SUB',
    '*': 'MUL',
    '/': 'DIV',
    '%': 'REM',
    '&&': 'AND',
    '||': 'OR',
    'print': 'PRINT',
    'var': 'VAR',
    'alloc': 'ALLOC',  # Local allocation (inside functions)
    'load': 'LOAD',
    'store': 'STORE',
    'label': 'LABEL',
    'cbranch': 'CBRANCH',  # Conditional branch
    'branch': 'BRANCH',  # Unconditional branch
    'call': 'CALL',
    'ret': 'RET'},
    dict.fromkeys(['<', '>', '<=', '>=', '==', '!='], "CMP")
)


def get_op_code(operation, type_name=None):
    op_code = OP_CODES[operation]
    suffix = "" if not type_name else IR_TYPE_MAPPING[type_name]

    return f"{op_code}{suffix}"


class Function:
    """
    Representa una function con su lista de instrucciones IR
    """

    def __init__(self, func_name, parameters, return_type):
        self.name = func_name
        self.parameters = parameters
        self.return_type = return_type

        self.code = []

    def append(self, ir_instruction):
        self.code.append(ir_instruction)

    def __iter__(self):
        return self.code.__iter__()

    def __repr__(self):
        params = [f"{pname}:{ptype}" for pname, ptype in self.parameters]
        return f"{self.name}({params}) -> {self.return_type}"


class GenerateCode(cast.NodeVisitor):
    """
    Clase visitante de nodo que crea secuencias de instrucciones
    codificadas de 3 direcciones.
    """

    def __init__(self):
        # Contador de registros
        self.register_count = 0

        # Contador rótulos de bloque
        self.label_count = 0

        # Función especial para recoger todas las declaraciones globales.
        init_function = Function("__minic_init", [], IR_TYPE_MAPPING['int'])

        self.functions = [init_function]

        # El código generado (lista de tuplas)
        self.code = init_function.code

        # Lista de loop merge labels para BreakStmt
        self.loop_merge_labels = []

        # Esta bandera indica si el código actual que se está visitando
        # está en alcance global, o no
        self.global_scope = True

    def new_register(self):
        """
        Crea un nuevo registro temporal
        """
        self.register_count += 1
        return f"R{self.register_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    # Debe implementar los métodos visit_Nodename para todos los demás
    # Nodos AST.  En tu código, necesitarás hacer instrucciones
    # y adjuntarlas a la lista de self-code.
    #
    # Algunos métodos de muestra siguen. Puede que tenga que ajustar
    # dependiendo de los nombres y la estructura de sus nodos AST.

    def visit_IfStmt(self, node):
        self.visit(node.condition)

        # Genera etiquetas para ambas ramas
        t_label = self.new_label()
        f_label = self.new_label()
        merge_label = self.new_label()
        lbl_op_code = get_op_code('label')
        branch_op_code = get_op_code('branch')

        # Inserta la instrucción CBRANCH
        cbranch_op_code = get_op_code('cbranch')
        self.code.append((cbranch_op_code, node.condition.register, t_label, f_label))

        # Ahora, el código para el bloque true
        self.code.append((lbl_op_code, t_label))
        self.visit(node.true_block)
        # Y debemos mezclar la etiqueta
        self.code.append((branch_op_code, merge_label))

        # Genera etiqueta para bloque false
        self.code.append((lbl_op_code, f_label))
        self.visit(node.false_block)
        self.code.append((branch_op_code, merge_label))

        # Ahora insertamos la etiqueta mezclada
        self.code.append((lbl_op_code, merge_label))

    def visit_WhileStmt(self, node):
        top_label = self.new_label()  # Para antes de la evaluación de condición
        start_label = self.new_label()  # Para después de la condición
        merge_label = self.new_label()  # Para salir del ciclo
        lbl_op_code = get_op_code('label')
        branch_op_code = get_op_code('branch')

        # Guardar el merge label en la lista
        self.loop_merge_labels.append(merge_label)

        # Esto es necesario ya que LLVM requiere de un branch a label
        self.code.append((branch_op_code, top_label))

        self.code.append((lbl_op_code, top_label))
        self.visit(node.condition)  # Generar instrucción de CMP

        # Inserta la instrucción CBRANCH
        cbranch_op_code = get_op_code('cbranch')
        self.code.append((cbranch_op_code, node.condition.register, start_label, merge_label))

        # Ahora, el código para el cuerpo del ciclo
        self.code.append((lbl_op_code, start_label))
        self.visit(node.body)

        # Luego de visitar el body, remover el merge label
        self.loop_merge_labels.pop()

        # Regresa a la etiqueta inicial
        self.code.append((branch_op_code, top_label))

        # Ahora insertamos la etiqueta mezclada
        self.code.append((lbl_op_code, merge_label))

    def visit_ReturnStmt(self, node):
        self.visit(node.value)
        op_code = get_op_code('ret')
        self.code.append((op_code, node.value.register))
        node.register = node.value.register

    def visit_BreakStmt(self, node):
        branch_op_code = get_op_code('branch')
        label = self.loop_merge_labels[-1]
        inst = (branch_op_code, label)
        self.code.append(inst)

    def visit_FuncDeclStmt(self, node):
        # Genera un nuevo objeto function para colocar el código
        func = Function(node.name,
                        [(p.name, IR_TYPE_MAPPING[p.datatype.type.name]) for p in node.params],
                        IR_TYPE_MAPPING[node.datatype.type.name])

        self.functions.append(func)

        if func.name == "main":
            func.name = "__minic_main"

        # Y cambiar la función actual a la nueva.
        old_code = self.code
        self.code = func.code

        # Ahora, genera el nuevo código de función.
        self.global_scope = False  # Turn off global scope
        self.visit(node.body)
        self.global_scope = True  # Turn back on global scope

        # Y, finalmente, volver a la función original en la que estábamos
        self.code = old_code

    def visit_StaticVarDeclStmt(self, node):
        self.visit(node.datatype)

        # La declaración de variable depende del alcance
        op_code = get_op_code('var', node.type.name)
        def_inst = (op_code, node.name)
        self.code.append(def_inst)

        if node.value:
            self.visit(node.value)
            op_code = get_op_code('store', node.type.name)
            inst = (op_code, node.value.register, node.name)
            self.code.append(inst)

    def visit_StaticArrayDeclStmt(self, node):
        self.visit(node.datatype)
        self.visit(node.size)

        op_code = get_op_code('var', node.type.name)
        inst = (op_code, node.name + '[' + node.size.register + ']')
        self.code.append(inst)

    def visit_LocalVarDeclStmt(self, node):
        self.visit(node.datatype)

        # La declaración de variable depende del alcance
        op_code = get_op_code('alloc', node.type.name)
        def_inst = (op_code, node.name)
        self.code.append(def_inst)

        if node.value:
            self.visit(node.value)
            op_code = get_op_code('store', node.type.name)
            inst = (op_code, node.value.register, node.name)
            self.code.append(inst)

    def visit_LocalArrayDeclStmt(self, node):
        self.visit(node.datatype)
        self.visit(node.size)

        op_code = get_op_code('alloc', node.type.name)
        inst = (op_code, node.name + '[' + node.size.register + ']')
        self.code.append(inst)

    def visit_IntegerLiteral(self, node):
        target = self.new_register()
        op_code = get_op_code('mov', 'int')
        self.code.append((op_code, node.value, target))
        # Guarde el nombre del registro donde se colocó el valor.
        node.register = target

    def visit_FloatLiteral(self, node):
        target = self.new_register()
        op_code = get_op_code('mov', 'float')
        self.code.append((op_code, node.value, target))
        node.register = target

    def visit_CharLiteral(self, node):
        target = self.new_register()
        op_code = get_op_code('mov', 'char')
        # Se obtiene el valor ASCII del char
        self.code.append((op_code, ord(node.value), target))
        node.register = target

    def visit_BoolLiteral(self, node):
        target = self.new_register()
        op_code = get_op_code('mov', 'bool')
        value = 1 if node.value == 'true' else 0
        self.code.append((op_code, value, target))
        node.register = target

    def visit_FuncCallExpr(self, node):
        self.visit(node.arguments)
        target = self.new_register()
        op_code = get_op_code('call')
        registers = [arg.register for arg in node.arguments]
        self.code.append((op_code, node.name, *registers, target))
        node.register = target

    def visit_VarExpr(self, node):
        op_code = get_op_code('load', node.type.name)
        register = self.new_register()
        inst = (op_code, node.name, register)
        self.code.append(inst)
        node.register = register

    def visit_ArrayExpr(self, node):
        self.visit(node.index)

        op_code = get_op_code('load', node.type.name)
        register = self.new_register()
        inst = (op_code, node.name + '[' + node.index.register + ']', register)
        self.code.append(inst)
        node.register = register

    def visit_UnaryOpExpr(self, node):
        self.visit(node.expr)
        operator = node.op
        node_type = node.type.name

        if operator == '+':
            # El operador unario + no produce código extra
            node.register = node.expr.register
        else:
            # Para tener en cuenta el hecho de que el código de máquina no
            # admite operaciones unarias, primero debemos cargar un 0 o 1,
            # dependiendo de la operación, en un nuevo registro.
            mov_op_code = get_op_code('mov', node_type)
            aux_target = self.new_register()
            aux_value = 0 if operator == '-' else 1  # 0 para el menos unario
            aux_inst = (mov_op_code, aux_value, aux_target)
            self.code.append(aux_inst)

            # XOR es para el operador boolean NOT
            op_code = 'XOR' if operator == '!' else get_op_code(operator[0], node_type)

            target = self.new_register()
            if aux_value:
                inst = (op_code, node.expr.register, aux_target, target)
            else:
                inst = (op_code, aux_target, node.expr.register, target)

            self.code.append(inst)
            node.register = target

            if operator in ('++', '--'):
                # Si la operación es inc o dec, se debe
                # guardar el nuevo valor de la variable
                store_op_code = get_op_code('store', node_type)
                store_inst = (store_op_code, target, node.expr.name)
                self.code.append(store_inst)

    def visit_BinaryOpExpr(self, node):
        self.visit(node.left)
        self.visit(node.right)
        operator = node.op

        op_code = get_op_code(operator, node.left.type.name)

        target = self.new_register()
        if op_code.startswith('CMP'):
            inst = (op_code, operator, node.left.register, node.right.register, target)
        else:
            inst = (op_code, node.left.register, node.right.register, target)

        self.code.append(inst)
        node.register = target

    def visit_VarAssignmentExpr(self, node):
        self.visit(node.value)
        node.register = node.value.register
        operator = node.op
        node_type = node.type.name

        if operator != '=':
            # Cargar el valor de la propia variable
            load_op_code = get_op_code('load', node_type)
            load_register = self.new_register()
            load_inst = (load_op_code, node.name, load_register)
            self.code.append(load_inst)

            # Hacer la operación binaria
            target = self.new_register()
            op_code = get_op_code(operator[0], node_type)
            inst = (op_code, load_register, node.value.register, target)
            self.code.append(inst)
            node.register = target

        store_op_code = get_op_code('store', node_type)
        store_inst = (store_op_code, node.register, node.name)
        self.code.append(store_inst)

    def visit_ArrayAssignmentExpr(self, node):
        self.visit(node.value)
        self.visit(node.index)
        node.register = node.value.register
        index_register = node.index.register
        operator = node.op
        node_type = node.type.name

        if operator != '=':
            # Cargar el valor de la propia variable
            load_op_code = get_op_code('load', node_type)
            load_register = self.new_register()
            load_inst = (load_op_code, node.name + '[' + index_register + ']', load_register)
            self.code.append(load_inst)

            # Hacer la operación binaria
            target = self.new_register()
            op_code = get_op_code(operator[0], node_type)
            inst = (op_code, load_register, node.value.register, target)
            self.code.append(inst)
            node.register = target

        store_op_code = get_op_code('store', node_type)
        store_inst = (store_op_code, node.register,
                      node.name + '[' + index_register + ']')
        self.code.append(store_inst)


# ----------------------------------------------------------------------
#                       PRUEBAS/PROGRAMA PRINCIPAL
#
# Nota: Algunos cambios serán necesarios en proyectos posteriores.
# ----------------------------------------------------------------------


def compile_ircode(source):
    """
    Genera código intermedio desde el fuente.
    """
    from cparse import parse
    from checker import check_program
    from errors import errors_reported

    ast = parse(source)
    check_program(ast)

    # Si no ocurrió error, genere código
    if not errors_reported():
        gen = GenerateCode()
        gen.visit(ast)
        return gen.functions
    else:
        return []


def main():
    import sys

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 -m minic.ircode filename\n")
        raise SystemExit(1)

    source = open(sys.argv[1]).read()
    code = compile_ircode(source)

    for f in code:
        print(f'{"::" * 5} {f} {"::" * 5}')
        for instruction in f.code:
            print(instruction)
        print("*" * 30)


if __name__ == '__main__':
    main()

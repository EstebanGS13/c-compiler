# checker.py
"""

*** No inicie este proyecto hasta que no haya completado el parser. ***

Visión general
--------------
En este proyecto necesitas realizar verificaciones semánticas
en tu programa.  Este problema es multifacético y complicado.
Para hacerlo un poco menos complicado, necesitas tomarlo lento
y en partes pequeñas.  La idea básica de lo que debe hacer es
la siguiente:

1.	Nombres y símbolos:

    Todos los identificadores deben definirse antes de ser
    utilizados. Esto incluye variables, constantes y nombres
    tipográficos. Por ejemplo, este tipo de código genera
    un error:

       a = 3; // Error. 'a' no definido.
       int a;

2.	Tipos de literales y constantes.

    Todos los símbolos literales se escriben implícitamente
    y se les debe asignar un tipo "int", "float" o "char".
    Este tipo se utiliza para establecer el tipo de constantes.
    Por ejemplo:

       const a = 42; // Escribe "int"
       const b = 4.2; // Escribe "float"
       const c = 'a'; // Escribe "char"

3.	Comprobación del tipo de operador

    Los operadores binarios solo operan en operandos de un
    tipo compatible.  De lo contrario, obtendrá un error de
    tipo. Por ejemplo:

        int  a = 2;
        float b = 3.14;

        int c = a + 3; // OKAY
        int d = a + b; // Error. int + float
        int e = b + 4.5; // Error. int = float

    Además, debe asegurarse de que solo sea compatible
    Los operadores están permitidos. Por ejemplo:

        char a = 'a'; // OKAY
        char b = 'a' + 'b'; // Error (op + no soportada)

4.	Asignación.

    Los lados izquierdo y derecho de una operación de
    asignación deben estar declarado como el mismo tipo.

        int a;
        a = 4 + 5; // OKAY
        a = 4.5; // Error. int = float

    Los valores solo se pueden asignar a declaraciones de
    variables, no a las constantes.

        int a;
        const b = 42;

        a = 37; // OKAY
        b = 37; // Error. b es const

Estrategia de implementación:
-----------------------------
Se va a usar la clase NodeVisitor definida en ast.py
para recorrer el árbol de parse. Se van a definir
varios métodos para diferentes tipos de nodos AST.
Por ejemplo, si tiene un nodo BinOp, escribirás un
método como este:

      def visit_BinOp (self, node):
          ...

Para comenzar, haga que cada método simplemente
imprima un mensaje:

      def visit_BinOp (self, node):
          imprimir ('visit_BinOp:', nodo)
          self.visit (node.left)
          self.visit (node.right)

Esto al menos te dirá que el método se está disparando.
Prueba ejemplos de código simple y asegúrese de que todos
sus métodos en realidad están corriendo cuando recorres
el árbol de análisis.

Pruebas
-------
Construya archivos que contengan diferentes elementos que
necesita para comprobar Las instrucciones específicas se
dan en cada archivo de prueba.

Pensamientos generales y consejos.
----------------------------------
Lo principal en lo que debe estar pensando con la verificación
es el programa exactitud. ¿Esta declaración u operación que
estás mirando? en el árbol de parse tiene sentido? Si no,
algún tipo de error necesita ser generado. Use sus propias
experiencias como programador como guía (piense sobre lo que
causaría un error en tu lenguaje de programación favorito).

Un desafío será la gestión de muchos detalles complicados.
Tienes que rastrear símbolos, tipos y diferentes tipos de
capacidades. No siempre está claro cómo organizar mejor
todo eso. Entonces, espera un poco al principio.
"""

from collections import ChainMap
from errors import error
from cast import *
from typesys import Type, FloatType, IntType, BoolType, CharType, VoidType
import inspect


class CheckProgramVisitor(NodeVisitor):
    """
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    """

    def __init__(self):
        # Initialize the symbol table
        self.symbols = {}

        # Temporal symbols table to save the global symbols when checking
        # a function definition
        self.temp_symbols = {}

        # Here we save the expected return type when checking a function
        self.expected_ret_type = None

        # And here we save the observed return type when checking a function
        self.current_ret_type = None

        # A table of function definitions
        self.functions = {}

        # To check if we are inside a loop
        self.loop = False

        # Put the builtin type names in the symbol table
        # self.symbols.update(builtin_types)
        self.keywords = {t.name for t in Type.__subclasses__()}

    def visit_Program(self, node):
        self.visit(node.decl_list)

    def visit_SimpleType(self, node):
        # Associate a type name such as "int" with a Type object
        node.type = Type.get_by_name(node.name)
        if node.type is None:
            error(node.lineno, f"Invalid type '{node.name}'")

    def visit_FuncParameter(self, node):
        self.visit(node.datatype)
        node.type = node.datatype.type

    def visit_NullStmt(self, node):
        pass

    def visit_ExprStmt(self, node):
        self.visit(node.value)

    def visit_IfStmt(self, node):
        self.visit(node.condition)

        cond_type = node.condition.type
        if cond_type:
            if issubclass(node.condition.type, BoolType):
                self.visit(node.true_block)
                self.visit(node.false_block)
            else:
                error(node.lineno, f"'Condition must be of type 'bool' but got type '{cond_type.name}'")

    def visit_WhileStmt(self, node):
        # To check if it's a nested loop
        inside_loop = self.loop

        self.visit(node.condition)

        cond_type = node.condition.type
        if cond_type:
            if issubclass(node.condition.type, BoolType):
                if node.body:
                    self.loop = True
                    self.visit(node.body)

                if not inside_loop:
                    self.loop = False
            else:
                error(node.lineno, f"'Condition must be of type 'bool' but got type '{cond_type.name}'")

    def visit_ForStmt(self, node):
        # To know if it's a nested loop
        inside_loop = self.loop

        self.visit(node.init)
        self.visit(node.condition)
        self.visit(node.loop)
        if node.body:
            self.loop = True
            self.visit(node.body)

        if not inside_loop:
            self.loop = False
        # cond_type = node.condition.type
        # if cond_type:
        #     if issubclass(node.condition.type, BoolType):
        #         self.visit(node.body)
        #     else:
        #         error(node.lineno, f"'Condition must be of type 'bool' but got type '{cond_type.name}'")

    def visit_ReturnStmt(self, node):
        self.visit(node.value)
        # Propagate return value type as a special property ret_type, only
        # to be checked at function declaration checking
        if self.expected_ret_type:
            if node.value is None and self.expected_ret_type is VoidType:
                self.current_ret_type = VoidType
            elif node.value:  # Check if return has a value
                self.current_ret_type = node.value.type
                if node.value.type and node.value.type != self.expected_ret_type:
                    error(node.lineno,
                          f"Function returns '{self.expected_ret_type.name}' but return statement value is of type '{node.value.type.name}'")
        else:
            error(node.lineno, "Return statement must be within a function")

    def visit_BreakStmt(self, node):
        if not self.loop:
            error(node.lineno, "Break statement must be within a loop")

    def visit_CompoundStmt(self, node):
        self.visit(node.decl)
        self.visit(node.stmt_list)

    def visit_FuncDeclStmt(self, node):
        if node.name in self.functions:
            prev_def = self.functions[node.name].lineno
            error(node.lineno, f"Function '{node.name}' already defined at line {prev_def}")

        self.visit(node.params)
        if node.params:
            param_types_ok = all((param.type is not None for param in node.params))
            if not param_types_ok:
                error(node.lineno, f"Invalid parameter type at function definition")

            param_names = [param.name for param in node.params]
            param_names_ok = len(param_names) == len(set(param_names))
            if not param_names_ok:
                error(node.lineno, "Duplicate parameter names at function definition")

            invalid_params = tuple([param.name for param in node.params if param.type is VoidType])
            if invalid_params:
                for param in invalid_params:
                    error(node.lineno, f"Parameter '{param}' has invalid type '{VoidType.name}' at function definition")

        self.visit(node.datatype)

        # Before visiting the function, body, we must change the symbol table
        # to a new one
        if self.temp_symbols:
            error(node.lineno, f"Illegal nested function declaration '{node.name}'")
        else:
            self.temp_symbols = self.symbols
            self.symbols = ChainMap(
                {param.name: param for param in node.params},
                self.temp_symbols
            )
            # Set the expected return value to observe
            self.expected_ret_type = node.datatype.type

            # Add the function declaration for future calls
            # and to allow recursion
            self.functions[node.name] = node
            self.visit(node.body)

            if self.current_ret_type != self.expected_ret_type:
                # Remove the function name from the table
                del self.functions[node.name]

                if self.current_ret_type is None and self.expected_ret_type is not VoidType:
                    error(node.lineno, f"Function '{node.name}' has no return statement")

            self.symbols = self.temp_symbols
            self.temp_symbols = {}
            self.expected_ret_type = None
            self.current_ret_type = None

    def visit_StaticVarDeclStmt(self, node):
        # Here we must update the symbols table with the new symbol
        node.type = None

        # Before anything, if we are declaring a variable with a name that is
        # a typename, then we must fail
        if node.name in self.keywords:
            error(node.lineno, f"Name '{node.name}' is not a legal name for variable declaration")
            return

        if node.name not in self.symbols:
            # First check that the datatype node is correct
            self.visit(node.datatype)

            if node.datatype.type:
                if node.datatype.type is VoidType:
                    error(node.lineno, f"Variable '{node.name}' declared as '{VoidType.name}'")
                else:
                    # Before finishing, this var declaration may have an expression to
                    # initialize it. If so, we must visit the node, and check type errors
                    if node.value:
                        self.visit(node.value)
                        if node.value.type:  # If value has no type, then there was a previous error
                            if node.value.type == node.datatype.type:
                                # Great, the value type matches the variable type declaration
                                node.type = node.datatype.type
                                self.symbols[node.name] = node
                            else:
                                error(node.lineno,
                                      f"Declaring variable '{node.name}' of type '{node.datatype.type.name}' "
                                      f"but assigned expression of type '{node.value.type.name}'")
                    else:
                        # There is no initialization, so we have everything needed
                        # to save it into our symbols table
                        node.type = node.datatype.type
                        self.symbols[node.name] = node
            else:
                error(node.lineno, f"Unknown type '{node.datatype.name}'")
        else:
            prev_lineno = self.symbols[node.name].lineno
            error(node.lineno, f"Name '{node.name}' has already been defined at line {prev_lineno}")

    def visit_StaticArrayDeclStmt(self, node):
        # Here we must update the symbols table with the new symbol
        node.type = None

        # Before anything, if we are declaring a variable with a name that is
        # a typename, then we must fail
        if node.name in self.keywords:
            error(node.lineno, f"Name '{node.name}' is not a legal name for variable declaration")
            return

        if node.name not in self.symbols:
            # First check that the datatype node is correct
            self.visit(node.datatype)

            if node.datatype.type:
                if node.datatype.type is VoidType:
                    error(node.lineno, f"Array '{node.name}' declared as '{VoidType.name}'")
                else:
                    if node.size:
                        self.visit(node.size)
                        if isinstance(node.size, IntegerLiteral):
                            # There is no initialization and the size is valid integer,
                            # so we have everything needed to save it into our symbols table
                            node.type = node.datatype.type
                            self.symbols[node.name] = node
                        else:
                            error(node.lineno, f"Size of array '{node.name}' must be a positive integer")
                    else:
                        error(node.lineno, f"Array size missing in '{node.name}'")
            else:
                error(node.lineno, f"Unknown type '{node.datatype.name}'")
        else:
            prev_lineno = self.symbols[node.name].lineno
            error(node.lineno, f"Name '{node.name}' has already been defined at line {prev_lineno}")

    def visit_LocalVarDeclStmt(self, node):
        # Here we must update the symbols table with the new symbol
        node.type = None

        # Before anything, if we are declaring a variable with a name that is
        # a typename, then we must fail
        if node.name in self.keywords:
            error(node.lineno, f"Name '{node.name}' is not a legal name for variable declaration")
            return

        if node.name not in self.symbols:
            # First check that the datatype node is correct
            self.visit(node.datatype)

            if node.datatype.type:
                if node.datatype.type is VoidType:
                    error(node.lineno, f"Variable '{node.name}' declared as '{VoidType.name}'")
                else:
                    # Before finishing, this var declaration may have an expression to
                    # initialize it. If so, we must visit the node, and check type errors
                    if node.value:
                        self.visit(node.value)
                        if node.value.type:  # If value has no type, then there was a previous error
                            if node.value.type == node.datatype.type:
                                # Great, the value type matches the variable type declaration
                                node.type = node.datatype.type
                                self.symbols[node.name] = node
                            else:
                                error(node.lineno,
                                      f"Declaring variable '{node.name}' of type '{node.datatype.type.name}' "
                                      f"but assigned expression of type '{node.value.type.name}'")
                    else:
                        # There is no initialization, so we have everything needed
                        # to save it into our symbols table
                        node.type = node.datatype.type
                        self.symbols[node.name] = node
            else:
                error(node.lineno, f"Unknown type '{node.datatype.name}'")
        else:
            prev_lineno = self.symbols[node.name].lineno
            error(node.lineno, f"Name '{node.name}' has already been defined at line {prev_lineno}")

    def visit_LocalArrayDeclStmt(self, node):
        # Here we must update the symbols table with the new symbol
        node.type = None

        # Before anything, if we are declaring a variable with a name that is
        # a typename, then we must fail
        if node.name in self.keywords:
            error(node.lineno, f"Name '{node.name}' is not a legal name for variable declaration")
            return

        if node.name not in self.symbols:
            # First check that the datatype node is correct
            self.visit(node.datatype)

            if node.datatype.type:
                if node.datatype.type is VoidType:
                    error(node.lineno, f"Array '{node.name}' declared as '{VoidType.name}'")
                else:
                    if node.size:
                        self.visit(node.size)
                        if isinstance(node.size, IntegerLiteral):
                            # There is no initialization and the size is valid integer,
                            # so we have everything needed to save it into our symbols table
                            node.type = node.datatype.type
                            self.symbols[node.name] = node
                        else:
                            error(node.lineno, f"Size of array '{node.name}' must be a positive integer")
                    else:
                        error(node.lineno, f"Array size missing in '{node.name}'")
            else:
                error(node.lineno, f"Unknown type '{node.datatype.name}'")
        else:
            prev_lineno = self.symbols[node.name].lineno
            error(node.lineno, f"Name '{node.name}' has already been defined at line {prev_lineno}")

    def visit_IntegerLiteral(self, node):
        # For literals, you'll need to assign a type to the node and allow it to
        # propagate.  This type will work it's way through various operators
        node.type = IntType

    def visit_FloatLiteral(self, node):
        node.type = FloatType

    def visit_CharLiteral(self, node):
        node.type = CharType

    def visit_BoolLiteral(self, node):
        node.type = BoolType

    def visit_NewArrayExpr(self, node):
        self.visit(node.datatype)
        self.visit(node.value)

    def visit_FuncCallExpr(self, node):
        node.type = None

        if node.name not in self.functions:
            error(node.lineno, f"Function '{node.name}' is not declared")
        else:
            # We must check that the argument list matches the function
            # parameters definition
            self.visit(node.arguments)

            func = self.functions[node.name]
            try:
                arg_types = tuple([arg.type.name for arg in node.arguments])
                expected_types = tuple([param.type.name for param in func.params])
                if arg_types != expected_types:
                    error(node.lineno,
                          f"Function '{node.name}' expects {expected_types}, but was called with {arg_types}")
            except AttributeError:
                error(node.lineno, f"Function '{node.name}' has undefined argument(s) at function call")

            # The type of the function call is the return type of the function
            node.type = func.datatype.type

    def visit_VarExpr(self, node):
        # Associate a type name such as "int" with a Type object
        self.visit(node.name)
        if node.name in self.symbols:
            node.type = self.symbols[node.name].type
        else:
            node.type = None
            error(node.lineno, f"Name '{node.name}' was not defined")

    def visit_ArrayExpr(self, node):
        # Associate a type name such as "int" with a Type object
        self.visit(node.name)
        self.visit(node.index)
        if node.name in self.symbols:
            if node.index.type is FloatType:
                error(node.lineno, f"Index of array '{node.name}' must be '{IntType.name}' type ")

            node.type = self.symbols[node.name].type
        else:
            node.type = None
            error(node.lineno, f"Name '{node.name}' was not defined")

    def visit_UnaryOpExpr(self, node):
        node.type = None
        node.expr.type = None

        if node.op in ('++', '--') and not isinstance(node.expr, VarExpr):
            error(node.lineno, f"Operator '{node.op}' requires its operand to be an lvalue")
            return

        # Check and propagate the type of the only operand
        self.visit(node.expr)

        if node.expr.type:
            op_type = node.expr.type.unaryop_type(node.op)
            if not op_type:
                expr_tname = node.expr.type.name
                error(node.lineno, f"Unary operation '{node.op} {expr_tname}' not supported")

            node.type = op_type

    def visit_BinaryOpExpr(self, node):
        # For operators, you need to visit each operand separately. You'll
        # then need to make sure the types and operator are all compatible.
        self.visit(node.left)
        self.visit(node.right)

        node.type = None
        # Perform various checks here
        if node.left.type and node.right.type:
            op_type = node.left.type.binop_type(node.op, node.right.type)
            if (not op_type) or (op_type is FloatType and node.op == '%'):
                left_tname = node.left.type.name
                right_tname = node.right.type.name
                error(node.lineno, f"Binary operation '{left_tname} {node.op} {right_tname}' not supported")

            node.type = op_type

    def visit_VarAssignmentExpr(self, node):
        # First visit the name definition to check that it is a valid name
        self.visit(node.name)
        # Visit the value, to also get type information
        self.visit(node.value)

        node.type = None
        # Check if the variable is already declared
        if node.name in self.symbols:
            var_type = self.symbols[node.name].type
            if var_type and node.value.type:
                # If both have type information, then the type checking worked on both branches
                if var_type == node.value.type:  # If var name type is the same as value type
                    if var_type is FloatType and node.op == '%=':
                        error(node.lineno, f"Cannot perform '%' assignment operation on '{var_type.name}' type")

                    # Propagate the type
                    node.type = var_type
                else:
                    error(node.lineno,
                          f"Cannot assign type '{node.value.type.name}' to variable '{node.name}' of type '{var_type.name}'")
        else:
            error(node.lineno, f"Name '{node.name}' was not defined")

    def visit_ArrayAssignmentExpr(self, node):
        # First visit the name definition to check that it is a valid name
        self.visit(node.name)
        # Visit the index and value, to also get type information
        self.visit(node.value)
        self.visit(node.index)

        node.type = None
        # Check if the array is already declared
        if node.name in self.symbols:
            array_type = self.symbols[node.name].type
            if array_type and node.value.type:
                # If both have type information, then the type checking worked on both branches
                if array_type == node.value.type:  # If var name type is the same as value type
                    if node.index.type is FloatType:
                        error(node.lineno, f"Index of array '{node.name}' must be '{IntType.name}' type ")

                    if array_type is FloatType and node.op == '%=':
                        error(node.lineno, f"Cannot perform '%' assignment operation on '{array_type.name}' type")

                    # Propagate the type
                    node.type = array_type
                else:
                    error(node.lineno,
                          f"Cannot assign type '{node.value.type.name}' to array '{node.name}' of type '{array_type.name}'")
        else:
            error(node.lineno, f"Name '{node.name}' was not defined")

    def visit_ArraySizeExpr(self, node):
        print('visit_ArraySizeExpr')
        self.visit(node.name)
        self.visit(node.name)


def print_node(node):
    """
    Print current node info for debugging
    """
    print("\n  " + inspect.stack()[1].function)  # Caller's function name
    print(node)


# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW
# ----------------------------------------------------------------------

def check_program(ast):
    """
    Check the supplied program (in the form of an AST)
    """
    checker = CheckProgramVisitor()
    checker.visit(ast)


def main():
    """
    Main program. Used for testing
    """
    import sys
    from cparse import parse

    if len(sys.argv) < 2:
        sys.stderr.write('Usage: python3 -m minic.checker filename\n')
        raise SystemExit(1)

    ast = parse(open(sys.argv[1]).read())
    check_program(ast)
    if '--show-types' in sys.argv:
        for depth, node in flatten(ast):
            print('%s: %s%s type: %s' % (getattr(node, 'lineno', None), ' ' * (4 * depth), node,
                                         getattr(node, 'type', None)))


if __name__ == '__main__':
    main()

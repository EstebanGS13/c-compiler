# minic/checker.py
'''

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

Estrategia de implementacion:
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
estás mirando? en el arbol de parse tiene sentido? Si no,
algún tipo de error necesita ser generado. Use sus propias
experiencias como programador como guía (piense sobre lo que
causaría un error en tu lenguaje de programación favorito).

Un desafío será la gestión de muchos detalles complicados.
Tienes que rastrear símbolos, tipos y diferentes tipos de
capacidades. No siempre está claro cómo organizar mejor
todo eso. Entonces, espera un poco al principio.
'''

from collections import ChainMap
from errors import error
from cast import *
from typesys import Type, FloatType, IntType, BoolType, CharType


class CheckProgramVisitor(NodeVisitor):
    '''
    Class Chequeo Programa.   Esta clase usa el patron visitor como se describe
    en ast.py.  Usted necesita definir metodos
    Program checking class.   This class uses the visitor pattern as described
    in ast.py.   You need to define methods of the form visit_NodeName()
    for each kind of AST node that you want to process.  You may need to
    adjust the method names here if you've picked different AST node names.
    '''

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

        # Put the builtin type names in the symbol table
        # self.symbols.update(builtin_types)
        self.keywords = {t.name for t in Type.__subclasses__()}

    def visit_Program(self, node):
        print('visit_Program', node)
        self.visit(node.decl_list)

    def visit_SimpleType(self, node):
        # Associate a type name such as "int" with a Type object
        node.type = Type.get_by_name(node.name)
        if node.type is None:
            error(node.lineno, f"Invalid type '{node.name}'")

    def visit_FuncParameter(self, node):
        self.visit(node.datatype)
        node.type = node.datatype.type
        # todo visitar name?

    def visit_ExprStmt(self, node):
        # print('visit_ExprStmt', node)
        self.visit(node.expr)

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
        self.visit(node.condition)

        cond_type = node.condition.type
        if cond_type:
            if issubclass(node.condition.type, BoolType):
                self.visit(node.body)
            else:
                error(node.lineno, f"'Condition must be of type 'bool' but got type '{cond_type.name}'")

    def visit_ForStmt(self, node):
        # todo terminar el for
        self.visit(node.condition)

        cond_type = node.condition.type
        if cond_type:
            if issubclass(node.condition.type, BoolType):
                self.visit(node.body)
            else:
                error(node.lineno, f"'Condition must be of type 'bool' but got type '{cond_type.name}'")

    def visit_ReturnStmt(self, node):
        self.visit(node.value)
        # Propagate return value type as a special property ret_type, only
        # to be checked at function declaration checking
        if self.expected_ret_type:
            self.current_ret_type = node.value.type
            if node.value.type and node.value.type != self.expected_ret_type:
                error(node.lineno,
                      f"Function returns '{self.expected_ret_type.name}' but return statement value is of type '{node.value.type.name}'")
        else:
            error(node.lineno, "Return statement must be within a function")

    def visit_CompoundStmt(self, node):
        # print('visit_CompoundStmt', node)
        self.visit(node.decl)
        self.visit(node.stmt_list)

    def visit_FuncDeclStmt(self, node):
        if node.name in self.functions:
            prev_def = self.functions[node.name].lineno
            error(node.lineno, f"Function '{node.name}' already defined at line {prev_def}")

        self.visit(node.params)

        param_types_ok = all((param.type is not None for param in node.params))
        param_names = [param.name for param in node.params]
        param_names_ok = len(param_names) == len(set(param_names))
        if not param_names_ok:
            error(node.lineno, "Duplicate parameter names at function definition")

        self.visit(node.datatype)
        ret_type_ok = node.datatype.type is not None

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

            self.visit(node.body)

            if not self.current_ret_type:
                error(node.lineno, f"Function '{node.name}' has no return statement")
            elif self.current_ret_type == self.expected_ret_type:
                # We must add the function declaration as available for
                # future calls
                self.functions[node.name] = node

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
                # Before finishing, this var declaration may have an expression
                # to initialize it. If so, we must visit the node, and check
                # type errors
                if node.value:
                    self.visit(node.value)

                    if node.value.type:  # If value has no type, then there was a previous error
                        if node.value.type == node.datatype.type:
                            # Great, the value type matches the variable type
                            # declaration
                            node.type = node.datatype.type
                            self.symbols[node.name] = node
                        else:
                            error(node.lineno,
                                  f"Declaring variable '{node.name}' of type '{node.datatype.type.name}' but assigned expression of type '{node.value.type.name}'")
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
                # Before finishing, this var declaration may have an expression
                # to initialize it. If so, we must visit the node, and check
                # type errors
                if node.value:
                    self.visit(node.value)

                    if node.value.type:  # If value has no type, then there was a previous error
                        if node.value.type == node.datatype.type:
                            # Great, the value type matches the variable type
                            # declaration
                            node.type = node.datatype.type
                            self.symbols[node.name] = node
                        else:
                            error(node.lineno,
                                  f"Declaring variable '{node.name}' of type '{node.datatype.type.name}' but assigned expression of type '{node.value.type.name}'")
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

    def visit_LocalDeclStmt(self, node):
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
                # Before finishing, this var declaration may have an expression
                # to initialize it. If so, we must visit the node, and check
                # type errors
                if node.value:
                    self.visit(node.value)

                    if node.value.type:  # If value has no type, then there was a previous error
                        if node.value.type == node.datatype.type:
                            # Great, the value type matches the variable type
                            # declaration
                            node.type = node.datatype.type
                            self.symbols[node.name] = node
                        else:
                            error(node.lineno,
                                  f"Declaring variable '{node.name}' of type '{node.datatype.type.name}' but assigned expression of type '{node.value.type.name}'")
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
                # Before finishing, this var declaration may have an expression
                # to initialize it. If so, we must visit the node, and check
                # type errors
                if node.value:
                    self.visit(node.value)

                    if node.value.type:  # If value has no type, then there was a previous error
                        if node.value.type == node.datatype.type:
                            # Great, the value type matches the variable type
                            # declaration
                            node.type = node.datatype.type
                            self.symbols[node.name] = node
                        else:
                            error(node.lineno,
                                  f"Declaring variable '{node.name}' of type '{node.datatype.type.name}' but assigned expression of type '{node.value.type.name}'")
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
        print('visit_NewArrayExpr')
        self.visit(node.datatype)
        self.visit(node.value)

    def visit_CallExpr(self, node):
        if node.name not in self.functions:
            error(node.lineno, f"Function '{node.name}' is not declared")
        else:
            # We must check that the argument list matches the function
            # parameters definition
            self.visit(node.arguments)

            arg_types = tuple([arg.type.name for arg in node.arguments])
            func = self.functions[node.name]
            expected_types = tuple([param.type.name for param in func.params])
            if arg_types != expected_types:
                error(node.lineno, f"Function '{node.name}' expects {expected_types}, but was called with {arg_types}")

            # The type of the function call is the return type of the function
            node.type = func.datatype.type

    def visit_VarExpr(self, node):
        print('visit_VarExpr')
        self.visit(node.name)

    def visit_ArrayLookupExpr(self, node):
        print('visit_ArrayLookupExpr')
        self.visit(node.name)
        self.visit(node.value)

    def visit_UnaryOpExpr(self, node):
        # Check and propagate the type of the only operand
        self.visit(node.right)

        node.type = None
        if node.right.type:
            op_type = node.right.type.unaryop_type(node.op)
            if not op_type:
                right_tname = node.right.type.name
                error(node.lineno, f"Unary operation '{node.op} {right_tname}' not supported")

            node.type = op_type

    def visit_BinaryOpExpr(self, node):
        # For operators, you need to visit each operand separately.  You'll
        # then need to make sure the types and operator are all compatible.
        self.visit(node.left)
        self.visit(node.right)

        node.type = None
        # Perform various checks here
        if node.left.type and node.right.type:
            op_type = node.left.type.binop_type(node.op, node.right.type)
            if not op_type:
                left_tname = node.left.type.name
                right_tname = node.right.type.name
                error(node.lineno, f"Binary operation '{left_tname} {node.op} {right_tname}' not supported")

            node.type = op_type

    def visit_IncDecExpr(self, node):
        print('visit_IncDecExpr')
        self.visit(node.op)
        self.visit(node.name)

    def visit_VarAssignmentExpr(self, node):
        print('visit_VarAssignmentExpr')
        self.visit(node.name)
        self.visit(node.value)

    def visit_ArrayAssignmentExpr(self, node):
        print('visit_ArrayAssignmentExpr')
        self.visit(node.name)
        self.visit(node.index)
        self.visit(node.value)

    def visit_IntToFloatExpr(self, node):
        print('visit_IntToFloatExpr')
        self.visit(node.name)
        self.visit(node.value)

    def visit_ArraySizeExpr(self, node):
        print('visit_ArraySizeExpr')
        self.visit(node.name)
        self.visit(node.name)

    def visit_SimpleLocation(self, node):
        if node.name not in self.symbols:
            node.type = None
            error(node.lineno, f"Name '{node.name}' was not defined")
        else:
            node.type = self.symbols[node.name].type

    def visit_ReadLocation(self, node):
        # Associate a type name such as "int" with a Type object
        self.visit(node.location)
        node.type = node.location.type

    def visit_WriteLocation(self, node):
        # First visit the location definition to check that it is a valid
        # location
        self.visit(node.location)
        # Visit the value, to also get type information
        self.visit(node.value)

        node.type = None
        if node.location.type and node.value.type:
            loc_name = node.location.name

            if isinstance(self.symbols[loc_name], ConstDeclaration): # todo const?
                # Basically, if we are writting a to a location that was
                # declared as a constant, then this is an error
                error(node.lineno, f"Cannot write to constant '{loc_name}'")
                return

            # If both have type information, then the type checking worked on
            # both branches
            if node.location.type == node.value.type:
                # Propagate the type
                node.type = node.value.type
            else:
                error(node.lineno,
                      f"Cannot assign type '{node.value.type.name}' to variable '{node.location.name}' of type '{node.location.type.name}'")


# ----------------------------------------------------------------------
#                       DO NOT MODIFY ANYTHING BELOW
# ----------------------------------------------------------------------

def check_program(ast):
    '''
    Check the supplied program (in the form of an AST)
    '''
    checker = CheckProgramVisitor()
    checker.visit(ast)


def main():
    '''
    Main program. Used for testing
    '''
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

'''
cast.py

Analizador descendente recursivo.
'''

# -------------------------------------------
# Nodos Abstract Syntax Tree (AST)

class AST(object):
    _nodes = {}

    @classmethod
    def __init_subclass__(cls):
        AST._nodes[cls.__name__] = cls

        if not hasattr(cls, '__annotations__'):
            return

        fields = list(cls.__annotations__.items())

        def __init__(self, *args, **kwargs):
            if len(args) != len(fields):
                raise TypeError(f'{len(fields)} argumentos esperados')
            for (name, ty), arg in zip(fields, args):
                if isinstance(ty, list):
                    if not isinstance(arg, list):
                        raise TypeError(f'{name} debe ser una lista')
                    if not all(isinstance(item, ty[0]) for item in arg):
                        raise TypeError(f'Todos los tipos de {name} deben ser {ty[0]}')
                elif not isinstance(arg, ty):
                    raise TypeError(f'{name} debe ser {ty}')
                setattr(self, name, arg)

            for name, val in kwargs.items():
                setattr(self, name, val)

        cls.__init__ = __init__
        cls._fields = [name for name, _ in fields]

    def __repr__(self):
        vals = [getattr(self, name) for name in self._fields]
        argstr = ', '.join(f'{name}={type(val).__name__ if isinstance(val, AST) else repr(val)}'
                           for name, val in zip(self._fields, vals))
        return f'{type(self).__name__}({argstr})'


# Nodos Abstract del AST

class Statement(AST):
    pass


class Expression(AST):
    pass


class Literal(Expression):
    '''
    Un valor literal como 2, 2.5, o "dos"
    '''
    pass


class Location(AST):
    pass


# Nodos Reales del AST

class NullStmt(Statement):
    pass


class ExprStmt(Statement):
    expr: Expression


class IfStmt(Statement):
    condition: Expression
    true_stmt: Statement
    else_stmt: Statement


class WhileStmt(Statement):
    condition: Expression
    stmt: Statement


class ForStmt(Statement):
    init: Expression
    condition: Expression
    loop: Expression
    stmt: Statement


class ReturnStmt(Statement):
    expr: Expression


class BreakStmt(Statement):
    pass


class CompoundStmt(Statement):
    pass


class FuncDeclStmt(Statement):
    type: str
    name: str
    params: Statement  # todo verificar
    stmt: Statement


class StaticVarDeclStmt(Statement):
    pass


class IntegerLiteral(Literal):
    value: int


class FloatLiteral(Literal):
    value: float


class CharLiteral(Literal):
    value: str


class StringLiteral(Literal):
    value: str


class BoolLiteral(Literal):
    value: str


class NewArrayExpr(Expression):
    type: str
    expr: Expression


class CallExpr(Expression):
    name: str
    expr: Expression


class VarExpr(Expression):
    expr: Expression


class ArrayLookupExpr(Expression):
    name: str
    value: Expression


class UnaryOpExpr(Expression):
    op: str
    expr: Expression


class BinaryOpExpr(Expression):
    '''
    Un operador binario como 2 + 3 o x * y
    '''
    op: str
    left: Expression
    right: Expression


class VarAssignmentExpr(Expression):
    name: str
    expr: Expression


class ArrayAssignmentExpr(Expression):
    name: str
    expr0: Expression
    expr1: Expression


class IntToFloatExpr(Expression):
    name: str
    expr: Expression


class ArraySizeExpr(Expression):
    name: str
    value: str


class SimpleLocation(Location):
    name: str


class ReadLocation(Expression):
    location: Location


class WriteLocation(Statement):
    location: Location
    value: Expression


# ----------------------------------------------------------------------
# Las siguientes clases para visitar y reescribir el AST se toman del 
# módulo ast de Python.

# NO MODIFIQUE
class NodeVisitor(object):
    '''
    Clase para visitar los nodos del árbol de análisis sintáctico.
    Esto se modela después de una clase similar en la biblioteca estándar
    ast.NodeVisitor. Para cada nodo, el método de visit(node) llama a
    un método visit_NodeName(node) que debe implementarse en subclases.
    El método generic_visit() se llama para todos los nodos donde no hay
    ningún método de matching_NodeName() coincidente.

    Este es un ejemplo de un visitante que examina un operador binario:

    class VisitOps(NodeVisitor):
        visit_BinOp(self,node):
            print('Binary operator', node.op)
            self.visit(node.left)
            self.visit(node.right)
            visit_UnaryOp(self,node):
            print('Unary operator', node.op)
            self.visit(node.expr)

    tree = parse(txt)
    VisitOps().visit(tree)
    '''

    def visit(self, node):
        '''
        Enecuta un metodo de la forma visit_NodeName(node) donde
        NodeName es el nombre de la clase de un nodo particular.
        '''
        if isinstance(node, list):
            for item in node:
                self.visit(item)
        elif isinstance(node, AST):
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            visitor(node)

    def generic_visit(self, node):
        '''
        Metodo ejecutado si no se encuentra el metodo visit_.
        Este examina el nodo para ver si tiene _fields, una lista,
        o puede ser atravesado.
        '''
        for field in getattr(node, '_fields'):
            value = getattr(node, field, None)
            self.visit(value)

    @classmethod
    def __init_subclass__(cls):
        '''
        Revision de sanidad. Se asegura que las clases visitor usen los
        nombres adecuados.
        '''
        for key in vars(cls):
            if key.startswith('visit_'):
                assert key[6:] in globals(), f"{key} no coincide con nodos AST"


# NO MODIFICAR
def flatten(top):
    '''
    Aplana todo el árbol de análisis sintáctico en una lista para
    depurar y probar.  Esto devuelve una lista de tuplas de la
    forma (depth, node) donde depth es un entero que representa
    la profundidad y node es el nodo AST asociado.
    '''

    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []

        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes

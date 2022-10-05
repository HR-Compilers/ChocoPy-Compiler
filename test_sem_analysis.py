#
# Test semantic analyser. Version 1.0
import parser
import disp_symtable
import semantic_error
import symtable_visitor
import print_visitor
# import type_visitor

filename = 'test/test03.cpy'

# Read in and print out the code.
with open(filename) as f:
    code = f.read()
print(code)

# Parse the code.
with open(filename) as f:
    p = parser.Parser(f)
    ast = p.parse()

# Now do the semantic analysis.
try:
    st_visitor = symtable_visitor.SymbolTableVisitor()
    st_visitor.do_visit(ast)
except semantic_error.ParserException as e:
    print(e.message)
    exit(-1)
st = st_visitor.get_symbol_table()
disp_symtable.print_symtable(st)

# Do the type checking.
# t_visitor = type_visitor.TypeVisitor(st)
# t_visitor.do_visit(ast)
# p_visitor = print_visitor.PrintVisitor()
# p_visitor.do_visit(ast)

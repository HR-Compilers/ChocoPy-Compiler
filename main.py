from fileinput import filename
from os import listdir
from os.path import isfile, join

import parser
import disp_symtable
import semantic_error
import symtab_visitor
import print_visitor

# We took all the test files from the github repository of ChocoPy
# Here we iterate over them and parse each of them as test
# mypath = "tests/"
# files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
# filtered_files = ["tests/" + element for element in files if element.endswith('.py') and not element.startswith('bad')]
# filtered_files.sort()

# for filename in filtered_files:

filename = "tests/test03.cpy"

# Parse the code.
with open(filename) as f:
    p = parser.Parser(f)
    ast = p.parse()

# Semantic analysis.
try:
    st_visitor = symtab_visitor.SymbolTableVisitor()
    st_visitor.do_visit(ast)
except semantic_error.ParserException as e:
    print(e.message)
    exit(-1)
st = st_visitor.get_symbol_table()
disp_symtable.print_symtable(st)
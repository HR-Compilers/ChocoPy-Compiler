from os import listdir
from os.path import isfile, join

import parser as parser
import lexer as lexer
import print_visitor

# We took all the test files from the github repository of ChocoPy
# Here we iterate over them and parse each of them as test
mypath = "tests/"
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
filtered_files = ["tests/" + element for element in files if element.endswith('.py') and not element.startswith('bad')]
filtered_files.sort()

for filename in filtered_files:
    with open(filename) as f:
        print('\n' + filename)
        p = parser.Parser(f)
        node = p.parse()
        pv = print_visitor.PrintVisitor()
        pv.do_visit(node)
        print("fully parsed file")

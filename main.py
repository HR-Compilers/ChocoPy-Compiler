from os import listdir
from os.path import isfile, join

import parser as parser
import lexer as lexer

# We took all the test files from the github repository of ChocoPy
# Here we iterate over them and parse each of them

mypath = "tests/"
files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
filtered_files = ["tests/" + element for element in files if element.endswith('.py') and not element.startswith('bad')]

for filename in filtered_files:
    with open(filename) as f:
        print('\n' + filename)
        p = parser.Parser(f)
        p.parse()
        print("fully parsed file")

import parser as parser
filename = 'test2.txt'
with open(filename) as f:
    parser = parser.Parser(f)
    parser.parse()
    print("fully parsed")
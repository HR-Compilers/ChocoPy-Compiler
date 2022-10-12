#
# disp_symtable. Version 1.2
#
import symbol_table


# def display(code):
#    st = symtable.symtable(code, "", "exec")  # To get Python's symbol table
#    print_symtable(st)

class DispSymbolTable:

    def __init__(self, do_print=True):
        self.do_print = do_print
        self.lines = []

    def clear(self):
        self.lines = []

    def lprint(self, text):
        if self.do_print:
            print(text)
        else:
            self.lines.append(text)

    def print_symbol(self, s, level, st):
        text = "{} {:15s} {:6s} {:6s} {:6s} {:6s} {:10s} {:s}".format(
                ' ' * level * 4,
                s.get_name(),
                str(s.is_global()),
                str(s.is_local()),
                str(s.is_parameter()),
                str(s.is_read_only() if hasattr(s, "is_read_only") else "na"),
                s.get_type_str() if hasattr(s, "get_type_str") else "na",
                str(symbol_table.symbol_decl_type(st, s.get_name()))
                )
        self.lprint(text)

    def print_symtable(self, st, level=0):
        self.lprint("{:s}{:s}".format(' ' * level * 4, '-' * 100))
        text = f" {st.get_name()=} {st.get_type()=} {st.is_nested()=} {st.has_children()=}"
        self.lprint("{:s}{:s}".format(' ' * level * 4, text))
        self.lprint("{:s}{:s}".format(' ' * level * 4, '-' * 100))
        text = "{} {:15s} {:6s} {:6s} {:6s} {:6s} {:10s}".format(
            ' ' * level * 4,
            'name', 'Global', 'Local', 'Param', 'ReadO', 'Type(str)')
        self.lprint(text)
        for s in st.get_symbols():
            self.print_symbol(s, level, st)
        if st.has_children():
            self.lprint("{:s}{:s}".format(' ' * level * 4, '->'))
            for child in st.get_children():
                self.print_symtable(child, level+1)

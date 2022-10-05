#
# disp_symtable. Version 1.0
#
import symtable


def display(code):
    st = symtable.symtable(code, "", "exec")
    print_symtable(st)


def print_symbol(s, level):
    text = "{} {:15s} {:6s} {:6s} {:6s} {:6s} {:10s}".format(
            ' ' * level * 4,
            s.get_name(),
            str(s.is_global()),
            str(s.is_local()),
            str(s.is_parameter()),
            str(s.is_read_only() if hasattr(s, "is_read_only") else "na"),
            s.get_type_str() if hasattr(s, "get_type_str") else "na"
            )
    print(text)


def print_symtable(st, level=0):
    print(' ' * level * 4, '-' * 100)
    print(' ' * level * 4, end='')
    text = f" {st.get_name()=} {st.get_type()=} {st.is_nested()=} {st.has_children()=}"
    print(text)
    print(' ' * level * 4, '-' * 100)
    text = "{} {:15s} {:6s} {:6s} {:6s} {:6s} {:10s}".format(
            ' ' * level * 4,
            'name', 'Global', 'Local', 'Param', 'ReadO', 'Type(str)')
    print(text)
    for s in st.get_symbols():
        print_symbol(s, level)
    if st.has_children():
        print(' ' * level * 4, '->')
        for child in st.get_children():
            print_symtable(child, level+1)

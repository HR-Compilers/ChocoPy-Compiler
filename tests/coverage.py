count:int = 0

class bar(object):
    p: bool = True

    def baz(self:"bar", xx: [int]) -> bool:
        global count
        count = count + 1
        return True


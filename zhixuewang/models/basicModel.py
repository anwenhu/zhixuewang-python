class ExtendedList(list):
    def __init__(self, l: list = None):
        if l is None:
            l = list()
        super().__init__(l)

    def find(self, f):
        for each in self:
            if f(each):
                return each

    def find_by_name(self, name: str):
        return self.find(lambda d: d.name == name)

    def find_by_id(self, id: str):
        return self.find(lambda d: d.id == id)

class listModel(list):
    def __init__(self, l: list):
        super().__init__(l)

    def find(self, f):
        for one in self:
            if f(one):
                return one

    def findByName(self, name: str):
        return self.find(lambda d: d.name == name)

    def findById(self, id: str):
        return self.find(lambda d: d.id == id)

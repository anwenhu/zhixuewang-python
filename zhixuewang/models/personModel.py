class personDataModel:
    def __init__(self, userName: str, userId: str):
        self.userName = userName
        self.userId = userId

    def __str__(self):
        return self.userName
    
    def __repr__(self):
        return self.userName

class classDataModel:
    def __init__(self, className: str, classId: str):
        self.className = className
        self.classId = classId

    def __str__(self):
        return self.className
    
    def __repr__(self):
        return self.className
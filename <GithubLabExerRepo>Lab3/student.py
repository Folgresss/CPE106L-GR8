class Student:
    def __init__(self, name,grade):
        self.name = name
        self.grade = grade

    def __eq__ (self, compareWith):
        return self.name == compareWith.name
    
    def __lt__ (self, compareWith):
        return self.name < compareWith.name
    
    def __ge__ (self, compareWith):
        return self.name >= compareWith.name

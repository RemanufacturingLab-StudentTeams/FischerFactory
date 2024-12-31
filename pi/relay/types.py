class Mapping:
    def __new__(self, FROM: str, TO: str, namespace=3):
        self.FROM = FROM
        self.TO = TO

    #!TODO: throw an exception if the provided topic or NodeID is not valid
        
class SpecialRuleOPCUA:
    def __new__(self, ORIGINAL: str, MEANS: str):
        self.ORIGINAL = ORIGINAL
        self.MEANS = MEANS

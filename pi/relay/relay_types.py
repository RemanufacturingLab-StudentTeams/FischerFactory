class Mapping:
    def __init__(self, FROM: str, TO: str, namespace=3):
        self.FROM = FROM
        self.TO = TO
        
class SpecialRuleOPCUA:
    def __init__(self, ORIGINAL: str, MEANS: str):
        self.ORIGINAL = ORIGINAL
        self.MEANS = MEANS

__all__ = ["Mapping", "SpecialRuleOPCUA"]
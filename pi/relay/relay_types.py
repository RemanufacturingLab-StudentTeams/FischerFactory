from typing import Optional
class Mapping:
    def __init__(self, FROM: str, TO: str, EXCLUDE:Optional[list[str]]=None, namespace:int=3):
        self.FROM = FROM
        self.TO = TO
        self.EXCLUDE = EXCLUDE
        
class SpecialRuleOPCUA:
    def __init__(self, ORIGINAL: str, MEANS: str):
        self.ORIGINAL = ORIGINAL
        self.MEANS = MEANS

__all__ = ["Mapping", "SpecialRuleOPCUA"]
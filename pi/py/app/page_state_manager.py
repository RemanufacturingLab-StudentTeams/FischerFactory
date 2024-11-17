from common import singleton_decorator as s 

@s.singleton
class PageStateManager():
    pages = []
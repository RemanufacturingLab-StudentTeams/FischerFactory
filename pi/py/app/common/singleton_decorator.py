def singleton(class_):
    """Decorator to mark a class as a singleton. This means that only one instance of the class can exist during the program lifetime. When the constructor is called and an instance already exists, the existing instance is return instead of making a new one.
    """    
    instances = {} # dict to store instances as values and the class as a key.
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

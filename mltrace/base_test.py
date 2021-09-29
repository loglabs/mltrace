"""
Base class for test objects.
"""

class Test():
    def __init__(self, name: str = "", args): # pass in list as args type?
        self.name = name
        self.args = args
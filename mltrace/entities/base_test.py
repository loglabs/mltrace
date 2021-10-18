"""
Base class for test objects.
"""

# from mltrace.entities.base import Base


class Test:
    def __init__(self, name: str = ""): # pass in list as args type?
        self.name = name

    # function utilities, all test functions, other details may want ot knwo about test

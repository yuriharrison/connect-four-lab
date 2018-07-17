"""Exceptions"""


class BadImplementation(Exception):
    """Bad Implementation Exception. Raised when a class
    didn't implemented a required method.
    """
    def __init__(self, cls_name, method_name):
        msg = 'Bad implementation: Class {} needs to implement the {} method.' \
                .format(cls_name, method_name)
        super().__init__(msg)


class MissingModel(Exception):
    """Missing Model Exception. Raise when an agent is
    instantiated and the required model(s) wasn't defined.
    """
    def __init__(self, cls_name, model_description):
        msg = 'MissingModel: The class {} require the model "{}".' \
                .format(cls_name, model_description)
        super().__init__(msg)
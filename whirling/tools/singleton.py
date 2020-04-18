"""Singletons are classes you intend to have one of. I like using them for
manager type classes.
"""


class Singleton:
    """This class is meant to be an example on how to create a singleton."""

    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Singleton.__instance is None:
            Singleton()
        return Singleton.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Singleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Singleton.__instance = self

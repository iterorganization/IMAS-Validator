from abc import ABC, abstractmethod

class CommandNotExecutedException(Exception):
    ...

class CommandInterface(ABC):

    @property
    @abstractmethod
    def result(self):
        ...

    @abstractmethod
    def __init__(self, args):
        ...

    @abstractmethod
    def __str__(self):
        '''
        Cast class instance to string.
        :return:
            String in format: COMMAND <argument1_name>=<argument1_value> ... <argumentN_name>=<argumentN_value>
        '''
        ...

    @abstractmethod
    def executed(self):
        '''
        Returns True if command was executed, False otherwise
        '''
        ...
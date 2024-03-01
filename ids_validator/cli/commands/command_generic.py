from .command_interface import CommandInterface, CommandNotExecutedException
from abc import abstractmethod

class GenericCommand(CommandInterface):

    @property
    def result(self):
        if self._result:
            return self._result
        else:
            additional_info = str(self)
            raise CommandNotExecutedException(f'Cannot collect result of command that was not executed.\nAdditional info: {additional_info}')

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

    def executed(self):
        try:
            self.result
            return True
        except CommandNotExecutedException:
            return False



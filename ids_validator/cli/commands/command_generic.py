from .command_interface import CommandInterface, CommandNotExecutedException, RulesetNotImplementedException
from abc import abstractmethod

class GenericCommand(CommandInterface):

    @property
    def result(self):
        if not self._result and self.executed():
            raise RulesetNotImplementedException(f'All rulesets are not implemented')

        elif not self.executed():
            additional_info = str(self)
            raise CommandNotExecutedException(f'Cannot collect result of command that was not executed.\nAdditional info: {additional_info}')

        return self._result

    def __init__(self, args):
        self._executed = False

    @abstractmethod
    def __str__(self):
        '''
        Cast class instance to string.
        :return:
            String in format: COMMAND <argument1_name>=<argument1_value> ... <argumentN_name>=<argumentN_value>
        '''

    def executed(self):
        return self._executed
    def execute(self):
        self._executed = True
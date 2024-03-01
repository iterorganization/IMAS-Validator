from commands.validate_command import ValidateCommand
import logging

class CommandParser:
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self):
        ...

    def parse(self, args):
        command = args.command
        command_objs = []

        if command.lower() == 'validate':
            command_objs.append(ValidateCommand(args))
        elif command.lower() == '<put new commands here>':
            ...
        else:
            raise Exception(f'Command < {command} > not recognised, stopping execution.')

        return command_objs

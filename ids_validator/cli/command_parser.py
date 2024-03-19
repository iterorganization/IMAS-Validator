import argparse
import logging
from typing import Sequence

from .commands.command_interface import CommandInterface
from .commands.validate_command import ValidateCommand


class CommandParser:
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self) -> None: ...

    def parse(self, args: argparse.Namespace) -> Sequence[CommandInterface]:
        command = args.command
        command_objs = []
        uri_list = args.uri[:]
        if command.lower() == "validate":
            for uri in uri_list:
                args.uri = [uri]
                command_objs.append(ValidateCommand(args))
        elif command.lower() == "<put new commands here>":
            ...
        else:
            raise Exception(
                f"Command < {command} > not recognised, stopping execution."
            )

        return command_objs

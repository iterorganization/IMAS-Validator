import argparse
import logging
from typing import List

from .commands.command_interface import (
    CommandInterface,
    CommandNotRecognisedException,
    IncorrectParameterUsageException,
)
from .commands.explore_command import ExploreCommand
from .commands.validate_command import ValidateCommand


class CommandParser:
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self) -> None: ...

    def parse(self, args: argparse.Namespace) -> List[CommandInterface]:
        command = args.command
        command_objs: List[CommandInterface] = []
        if command == "validate":
            if args.debug:
                print("debug option enabled")
            uri_list = args.URI[:][0]
            for uri in uri_list:
                args.uri = [uri]
                command_objs.append(ValidateCommand(args))
        elif command == "explore":
            if args.verbose is not None and args.no_docstring is not None:
                raise IncorrectParameterUsageException
            else:
                command_objs.append(ExploreCommand(args))
        else:
            raise CommandNotRecognisedException(
                f"Command < {command} > not recognised, stopping execution."
            )

        return command_objs

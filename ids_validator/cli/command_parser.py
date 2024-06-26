import argparse
import logging
from typing import Sequence

from .commands.command_interface import CommandInterface, CommandNotRecognisedException
from .commands.validate_command import ValidateCommand, ExploreCommand
from ids_validator.validate.explore import explore

class CommandParser:
    # Class logger
    __logger = logging.getLogger(__name__ + "." + __qualname__)

    def __init__(self) -> None: ...

    def parse(self, args: argparse.Namespace) -> Sequence[CommandInterface]:
        command = args.command
        command_objs = []
        if command == "validate":
            # if args.debug:
            #     print("debug option enabled")
            uri_list = args.URI[:][0]
            for uri in uri_list:
                args.uri = [uri]
                command_objs.append(ValidateCommand(args))
        elif command == "explore":
            command_objs.append(ExploreCommand(args))
        else:
            raise CommandNotRecognisedException(
                f"Command < {command} > not recognised, stopping execution."
            )

        return command_objs

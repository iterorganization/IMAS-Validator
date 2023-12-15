""" """

import click

@click.group()
def main():
    """ """
    pass


@main.command()
@click.option(
    "--arg",
    type='',
    default="",
    help="",
)
def report_func():
    """"""
    pass


if __name__ == "__main__":
    main()

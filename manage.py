import click

from servers.metrics.start import metrics_server


@click.group()
def cli():
    pass


cli.add_command(metrics_server)


if __name__ == '__main__':
    cli()

import click

from aeapi import AtomicEmpireAPI
from models.credentials import Credentials
from models.crud import get_credentials, save_credentials


# https://github.com/pallets/click/issues/921
def deactivate_prompts(ctx, param, value):
    if value:
        for p in ctx.command.params:
            if isinstance(p, click.Option) and p.prompt is not None:
                p.prompt = None
    return value


@click.command("login")
@click.option('--email', '-e', prompt=True, help='Login email for atomicempire.com')
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True, help='Login password for atomicempire.com')
@click.option('--saved', '-s', is_flag=True, is_eager=True, callback=deactivate_prompts, help='Use saved credentials to login')
def cli(email: str, password: str, saved: bool):
    if saved:
        creds = get_credentials()
        email = creds.email
        password = creds.password

    AtomicEmpireAPI().login(email, password)
    print('Login successfull')

    if not saved:
        creds = Credentials(email=email, password=password)
        save_credentials(creds)

import click

from aeapi import AtomicEmpireAPI


@click.command("login")
@click.option('--email', '-e', prompt=True, help='Login email for atomicempire.com')
@click.option('--password', '-p', prompt=True, hide_input=True, confirmation_prompt=True, help='Login password for atomicempire.com')
def cli(email: str, password: str):
    api = AtomicEmpireAPI()
    api.login(email, password)
    print('Login successfull')

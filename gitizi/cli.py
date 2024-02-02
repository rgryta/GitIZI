"""
Git IZI : CLI
"""

import sys

import click

from .ai import ask as ask_ai, Context
from .exceptions import GitiziException
from .util import (
    default_remote_branch,
    default_local_branch,
    current_synced,
    default_synced,
    reset_default,
    is_current_default,
    current_branch,
    default_remote,
    all_commited,
    checkout,
    commit,
    fetch_default,
    merge_to_current,
    last_shared,
    get_log_until,
    get_hash,
    reset_branch,
    delete_branch,
    ammend_commit_msg,
)


@click.group()
def main():
    """Git IZI entrypoint command"""

def _default(reset: bool):
    """Helper function"""
    fetch_default()
    click.echo(
        f"[{default_local_branch().name}] ----[In sync: {default_synced()}]----> [{default_remote_branch().name}]"
    )

    if reset:
        checked = False
        old_branch = None
        if not is_current_default():
            if not all_commited():
                click.echo(
                    "All local changes have to be commited or stashed before reset"
                )
                raise click.Abort
            checked, old_branch = checkout()
        if not default_synced():
            reset_default()
            if checked:
                checkout(old_branch)
            click.echo(f"Default branch [{default_local_branch()}] synchronised")
        else:
            if checked:
                checkout(old_branch)
            click.echo(f"Branch [{default_local_branch()}] is already synchronised")


@main.command()
@click.option(
    "--reset/--no-reset",
    is_flag=True,
    default=False,
    help="Reset local branch to its remote state.",
)
def default(reset: bool = False):
    """Print default branch name"""
    _default(reset=reset)


@main.group()
def current():
    """Operations on current branch"""


@current.command()
def info():
    """Current branch info"""
    click.echo(
        f"Current branch is: {current_branch()}, is default: {is_current_default()}"
    )
    click.echo(
        f"Default branch is: {default_local_branch()}, is in sync with remote [{default_remote()}]: {default_synced()}"
    )


def _squash(force: bool = False):
    """Squash current commit"""
    fetch_default()
    if is_current_default():
        click.echo(f"Branch currenly in use is a default branch: {current_branch()}")
        raise click.Abort
    click.echo("Non-default branch, continuing...")

    if not all_commited():
        if not force:
            click.echo("All local changes have to be commited or stashed before squash")
            raise click.Abort
        commit()
    click.echo("Everything is commited, continuing...")

    if not default_synced():
        if not force:
            click.echo(
                f"Default branch [{default_local_branch()}] is not in sync with remote default [{default_remote_branch()}]"
            )
            raise click.Abort
        _default(reset=True)
        # TODO: Pull default -- check if reset is all that's needed
    click.echo("Default branch is in sync with remote, continuing...")

    if not current_synced(can_ahead=True):
        if not force:
            click.echo(
                f"Current branch [{current_branch()}] is behind with local default [{default_local_branch()}]"
            )
            raise click.Abort
        merge_to_current()
    click.echo("Default branch is ahead or in sync with default, continuing...")

    shared = last_shared()
    logs = get_log_until(commit_hash=shared)

    _, old_branch = checkout()  # Checkout to default
    checkout(branch="gitizi/temp", new=True)

    merge_to_current(branch=old_branch, with_squash=True)
    commit(with_no_edit=True)
    current_hash = get_hash()

    checkout(branch=old_branch)
    reset_branch(from_hash=current_hash)

    delete_branch("gitizi/temp")
    click.echo("Commits squashed, aggregating message...")

    try:
        squashed_message = ask_ai(msg=logs, ctx=Context.SQUASH)
        ammend_commit_msg(squashed_message)
        click.echo(f"Amended commit message: {squashed_message}")
        sys.exit(0)
    except GitiziException:
        click.echo("Connection failure. Generating squashed commit message failed.")
        sys.exit(1)


@current.command()
@click.option(
    "-f",
    "--force",
    is_flag=True,
    default=False,
    help="Try to perform all actions needed to create a squashed commit.",
)
def squash(force: bool = False):
    _squash(force=force)


@main.command()
@click.argument("message")
def ask(message: str):
    """Ask AI"""
    click.echo(ask_ai(message))


@click.command()
def main_squash():
    _squash(force=True)

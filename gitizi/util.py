"""
Git IZI : Util
"""

import os
import sys

from contextlib import contextmanager, redirect_stderr, redirect_stdout

import click
import git

from .exceptions import GitiziException


@contextmanager
def suppress_output():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, "w", encoding="utf-8") as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield err, out


try:
    repo = git.Repo(os.getcwd())
except git.exc.InvalidGitRepositoryError:
    click.echo("Invalid repository!")
    sys.exit(1)


def default_remote():
    """Get default remote"""
    candidates = ["origin", "remote"]
    for remote in repo.remotes:
        if remote.name in candidates:
            return remote
    return repo.remotes[0]


def default_remote_branch(remote: str | git.Remote | None = None) -> git.Reference:
    """Get default branch"""
    remote = (
        remote
        if isinstance(remote, git.Remote)
        else git.Remote(repo=repo, name=remote) if remote else default_remote()
    )

    return next(filter(lambda ref: ref.name == f"{remote.name}/HEAD", remote.refs)).ref


def default_local_branch() -> git.Reference:
    """Get default local branch"""
    remote_branch = default_remote_branch()

    return next(
        filter(
            lambda branch: branch.tracking_branch() == remote_branch,
            remote_branch.repo.branches,
        )
    )


def current_branch() -> git.Head:
    """Get current branch"""
    return repo.active_branch


def is_current_default() -> bool:
    """Check if current branch is a default branch"""
    current = current_branch()
    default = default_local_branch()

    return current == default


def default_synced(can_behind: bool = False, can_ahead: bool = False) -> bool:
    """Check if default branch is synced with remote"""
    local = default_local_branch()
    remote = default_remote_branch()

    if not can_behind:
        commits_behind = repo.iter_commits(f"{local.name}..{remote.name}")
        count_behind = sum(1 for _ in commits_behind)
    else:
        count_behind = 0

    if not can_ahead:
        commits_ahead = repo.iter_commits(f"{remote.name}..{local.name}")
        count_ahead = sum(1 for _ in commits_ahead)
    else:
        count_ahead = 0

    return count_behind == 0 and count_ahead == 0


def current_synced(can_behind: bool = False, can_ahead: bool = False) -> bool:
    """Check if current branch is in sync with default local branch"""
    curr_branch = current_branch()

    local_name = default_local_branch().name

    if not can_behind:
        commits_behind = repo.iter_commits(f"{curr_branch.name}..{local_name}")
        count_behind = sum(1 for _ in commits_behind)
    else:
        count_behind = 0

    if not can_ahead:
        commits_ahead = repo.iter_commits(f"{local_name}..{curr_branch.name}")
        count_ahead = sum(1 for _ in commits_ahead)
    else:
        count_ahead = 0

    return count_behind == 0 and count_ahead == 0


def reset_default():
    """Fully resets default branch to be in-line with its remote"""
    repo.head.reset(
        commit=f"{default_remote()}/HEAD", index=True, working_tree=True, paths=None
    )


def all_commited() -> bool:
    """Check if everything is commited and we can safely check out"""
    return not repo.is_dirty()


def checkout(branch: str | None = None, new: bool = False) -> tuple[bool, str]:
    """Checkout to provided branch or to default branch if None"""
    if branch is None:
        branch = default_local_branch().name
    else:
        branches = (branch.name for branch in repo.branches)
        if new:
            if branch in branches:
                raise GitiziException("Branch already exists")
        else:
            if branch not in branches:
                raise GitiziException("Incorrect branch")

    curr_branch = current_branch().name
    if branch != curr_branch:
        args = tuple()
        if new:
            args = args + ("-b",)
        args = args + (branch,)
        repo.git.checkout(*args)
        return True, curr_branch
    return False, curr_branch


def fetch_default():
    """Fetch default branch from default remote"""
    default_remote().fetch(
        refspec=f"refs/heads/{default_local_branch().name}:{default_remote_branch().path}"
    )


def commit(with_no_edit: bool = False):
    """Create a commit with all uncommited changes"""
    files = repo.git.diff(None, name_only=True)
    for f in files.split("\n"):
        if f:
            repo.git.add(f)
    if not with_no_edit:
        repo.git.commit(
            "-m",
            "Modified files: " + ", ".join(files.split("\n")),
            "--allow-empty",
        )
    else:
        repo.git.commit("--no-edit", "--allow-empty")


def merge_to_current(
    branch: str = None,
    with_squash: bool = False,
    with_commit: bool = False,
    with_no_edit: bool = False,
):
    """Merge default branch to current branch"""
    branch = default_local_branch().name if branch is None else branch

    args = (branch,)
    if with_squash:
        args = args + ("--squash",)
    if with_commit:
        args = args + ("--commit",)
    if with_no_edit:
        args = args + ("--no-edit",)

    repo.git.merge(*args)


def get_hash():
    """Get current commit hash"""
    return repo.head._get_commit().hexsha  # pylint:disable=protected-access


def last_shared():
    """Get last shared commit hash"""
    if is_current_default():
        return None
    branch = default_local_branch().name
    cmd = ["git", "merge-base", "--fork-point", branch]
    last_shared_hash = repo.git.execute(cmd)
    return last_shared_hash


def get_log_until(commit_hash: str):
    """Get commit messages until commit_hash"""
    cmd = ["git", "log", f"{commit_hash}..", "--pretty=format:%s", "--abbrev-commit"]
    return repo.git.execute(cmd)


def reset_branch(from_hash: str | None = None):
    """Reset current branch"""
    if from_hash:
        repo.head.reset(commit=from_hash)
    else:
        repo.head.reset()


def delete_branch(branch_name: str):
    """Delete a branch"""
    cmd = ["git", "branch", "-D", branch_name]
    repo.git.execute(cmd)


def ammend_commit_msg(new_msg: str):
    """Ammend last commit message"""
    repo.git.commit("--amend", "-m", new_msg, "--allow-empty")

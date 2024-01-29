"""
Git IZI : AI
"""

from json import JSONDecodeError

from aiohttp import WSServerHandshakeError

from gitizi.util import suppress_output
from ..exceptions import GitiziException, GitiziParseException

with suppress_output():
    import g4f

from g4f.Provider import (
    Bing,
)

from .context import Context

from .context.squash import (
    CONTEXT as S_CONTEXT,
    USER_MSG_WRAPPER as S_WRAPPER,
    retrieve_response as S_RESPONSE,
)


def contextualize(msg: str, ctx: Context = Context.ASK) -> list[dict]:
    """Contextualize message"""
    match ctx:
        case Context.SQUASH:
            ai_ctx = S_CONTEXT
            wrapper = S_WRAPPER
            msg = msg if msg else "No changes"
        case Context.ASK | _:
            ai_ctx = []
            wrapper = "{user_message}"
    ai_ctx.append({"role": "user", "content": wrapper.format(user_message=msg)})

    return ai_ctx


def parse_response(msg, ctx: Context = Context.ASK) -> str:
    """Return contextualized response message"""
    match ctx:
        case Context.SQUASH:
            return S_RESPONSE(response=msg)
        case Context.ASK | _:
            return msg


def ask(msg: str, ctx: Context = Context.ASK):
    """Ask AI"""
    messages = contextualize(msg=msg, ctx=ctx)

    with suppress_output():
        for _ in range(3):
            try:
                response = g4f.ChatCompletion.create(
                    model=g4f.models.default,
                    messages=messages,
                    provider=Bing,
                    auth=True,
                )
                return parse_response(msg=response, ctx=ctx)
            except WSServerHandshakeError | GitiziParseException:
                pass
        else:
            raise GitiziException("Connection error")

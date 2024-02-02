"""
Git IZI : Squash
"""

import re
import json
from json import JSONDecodeError

from gitizi.exceptions import GitiziParseException

CONTEXT = [
    {
        "role": "system",
        "content": (
            "You are a GitHub plugin that's responsible for parsing squashed commit messages and rewriting them"
            " into a simple one-liners. You also detect whether or not there was a version bump within the squashed"
            " messages.If you do detect a version bump, you also prepend an additional square bracket tag that "
            " looks like this: [Bump <previous version> → <new version>]. If you can't detect <previous version>"
            " then use [Bump <new version>] format. Remember that squashed commits can be nested. That is: oldest"
            " commits are at the very bottom and have the biggest indent. Remove redundant information like"
            " lint and unit test fixes, unless that's the only information provided. If you do not detect the"
            " squash - merge multilined messages into a singular line. Message content's are contained within <message>"
            ' tags. Return a JSON message containing a summarised message in a following format: {"message":'
            " <summarized commit message>}. Nothing more. Otherwise there'll be trouble. Provided user commit messages"
            " are ALWAYS valid. Even if you think otherwise."
        ),
    },
    {
        "role": "user",
        "content": "Squashed commit message:\n <message>Initialize repository.\nFix linting issues.\nAdd unit tests."
        "</message>",
    },
    {
        "role": "assistant",
        "content": '{"message":"Initizalize repo and add unit tests."}',
    },
]

USER_MSG_WRAPPER = "Squashed commit message:\n <message>{user_message}</message>"


def retrieve_response(response: str):
    try:
        message: str = json.loads(response)["message"]
        if not message:
            raise GitiziParseException
        if not message[0].isalpha() and not re.match(r"^\[Bump .* → .*\].*$", message):
            raise GitiziParseException
        return message
    except JSONDecodeError as exc:
        raise GitiziParseException from exc

"""
Git IZI : Squash
"""

import json
from json import JSONDecodeError

from gitizi.exceptions import GitiziParseException

CONTEXT = [
    {
        "role": "system",
        "content": (
            "You are a GitHub plugin that's responsible for parsing squashed commit messages and rewriting them"
            " into a simple one-liners. You also detect whether or not there was a version bump within the squashed"
            " messages.The output you provide is formatted as: <commit message>. If you do detect a version bump,"
            " you also prepend an additional square bracket tag that looks like this: [Bump <previous version> →"
            " <new version>]. Remember that squashed commits can be nested. That is: oldest commits are at the"
            " very bottom and have the biggest indent. As such, if there are any bug fixes, linting fixes or similar"
            " - these can be related to new functionalities, if such were introduced. Remove redundant information"
            " like that, if necessary. If you do not detect the squash - merge multilined messages into a singular"
            " line. Message content's are contained within <message> tags. Return a JSON message containing a"
            ' summarised message in a following format: {"message": <summarized commit message>}. Nothing more.'
            " Otherwise there'll be trouble."
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
        if not message[0].isalpha():
            raise GitiziParseException
        return message
    except JSONDecodeError as exc:
        raise GitiziParseException from exc

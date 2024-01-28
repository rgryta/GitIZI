"""
Git IZI : Exceptions
"""


class GitiziException(Exception):
    """General Git IZI Exception"""


class GitiziParseException(GitiziException):
    """Error while parsing g4f response"""

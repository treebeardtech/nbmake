from _pytest._code.code import (  # type: ignore
    ReprFileLocation,
    TerminalRepr,
    TerminalWriter,
)


class NbMakeFailureRepr(TerminalRepr):  # type: ignore
    """
    Representation of a test failure.
    """

    def __init__(self, term: str, summary: str):
        self.term = term
        self.reprcrash = ReprFileLocation("", "", summary)  # type: ignore

    def toterminal(self, tw: TerminalWriter) -> None:  # type: ignore
        tw.write(f"{self.term}\n")

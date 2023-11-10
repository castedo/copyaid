# Python Standard Library
import math, re
from difflib import SequenceMatcher

from typing import Iterator

###############################################################################
# Code that "diff-adapts" altered text to be more diff-friendly with original
###############################################################################


class TokenSequenceMatcher:

    # just an opaque token object to represent end-of-message for matching algo
    EOM = "just-random-a0f75a980e88b9c27fa02ed5b8def537d131f281"

    def __init__(self, focal_text: str):
        isjunk = lambda x: x == " "
        self.matcher = SequenceMatcher(isjunk, autojunk=False)
        self.re_token = re.compile(r"\w+|\W|\n")
        self.focus = self.tokenize(focal_text) + [TokenSequenceMatcher.EOM]
        # SequenceMatcher: ... caches detailed information about the second sequence,
        # so if you want to compare one sequence against many sequences,
        # use set_seq2() ...
        self.matcher.set_seq2(self.focus)

    def tokenize(self, text: str) -> list[str]:
        return [match[0] for match in self.re_token.finditer(text)]

    def set_alternative(self, alt_text: str) -> None:
        self.alt = self.tokenize(alt_text) + [TokenSequenceMatcher.EOM]
        self.matcher.set_seq1(self.alt)

    def operations(self) -> Iterator[tuple[str, list[str], list[str]]]:
        """tag meaning is relative to going from alt text to focal text"""

        return (
            (tag, self.alt[a1:a2], self.focus[f1:f2])
            for tag, a1, a2, f1, f2 in self.matcher.get_opcodes()
        )


class DiffAdaptedRevisionTokens:
    def __init__(self) -> None:
        self.line_debt = 0
        self.tokens: list[str] = []

    def __str__(self) -> str:
        strs = self.tokens
        if strs and strs[-1] == TokenSequenceMatcher.EOM:
            strs = self.tokens[:-1]
        return "".join(strs)

    def append_operations(self, matcher: TokenSequenceMatcher) -> None:
        # ops for converting revised text back to orig
        for tag, rev_chunk, orig_chunk in matcher.operations():
            if tag == "equal":
                self.append_unrevised(rev_chunk)
            else:
                self.line_debt += orig_chunk.count("\n")
                if len(rev_chunk) > 0:
                    self.append_revised(rev_chunk)
                else:
                    self.undo_delete(orig_chunk)

    def undo_delete(self, orig_chunk: list[str]) -> None:
        new_line = (len(self.tokens) == 0 or self.tokens[-1:] == ['\n'])
        if new_line and all(s.isspace() for s in orig_chunk):
            # undo deletion of indentation and extra newlines
            self.tokens += orig_chunk

    def append_unrevised(self, chunk: list[str]) -> None:
        self._preempt_chunk(chunk)
        # Ideally line debt goes to zero when chunks are unrevised.
        # But sometimes a sequence matcher gets confused and matches
        # chunks that are from totally different lines.
        if len(chunk) > 1:
            # Only consider unrevised chunk longer than one token.
            # Halving and truncating is safer than just setting to zero.
            self.line_debt = math.trunc(self.line_debt / 2)
        self.tokens += chunk

    def append_revised(self, rev_chunk: list[str]) -> None:
        self._preempt_chunk(rev_chunk)
        for i in range(len(rev_chunk)):
            if rev_chunk[i] == "\n":
                self.line_debt -= 1
            elif rev_chunk[i : (i+2)] == [".", " "]:
                rev_chunk[i+1] = "\n"
            elif self.line_debt > 0:
                if rev_chunk[i : (i+2)] in ([",", " "], [";", " "]):
                    rev_chunk[i+1] = "\n"
        self.tokens += rev_chunk

    def _preempt_chunk(self, chunk: list[str]) -> None:
        if self.line_debt > 0 and chunk[0:1] == [" "] and self.tokens[-1:] != ["\n"]:
            chunk[0] = "\n"


def diffadapt(orig_text: str, revisions: list[str]) -> list[str]:
    ret = []
    matcher = TokenSequenceMatcher(orig_text)
    for rev_text in revisions:
        if not rev_text.endswith("\n"):
            rev_text += "\n"
        matcher.set_alternative(rev_text)
        tokens = DiffAdaptedRevisionTokens()
        tokens.append_operations(matcher)
        ret.append(str(tokens))
    return ret

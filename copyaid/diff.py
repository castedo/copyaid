# Python Standard Library
import difflib, re

from typing import Iterator, Optional

###############################################################################
# Code that "diff-adapts" altered text to be more diff-friendly with original
###############################################################################

Tokens = list[str]


class TokenSequenceMatcher:

    # just an opaque token object to represent end-of-message for matching algo
    EOM = "just-random-a0f75a980e88b9c27fa02ed5b8def537d131f281"

    def __init__(self, focal_text: str):
        isjunk = lambda x: x == " "
        self.matcher = difflib.SequenceMatcher(isjunk, autojunk=False)
        self.re_token = re.compile(r"\w+|\W|\n")
        self.focus = self.tokenize(focal_text) + [TokenSequenceMatcher.EOM]
        # SequenceMatcher: ... caches detailed information about the second sequence,
        # so if you want to compare one sequence against many sequences,
        # use set_seq2() ...
        self.matcher.set_seq2(self.focus)

    def tokenize(self, text: str) -> Tokens:
        return [match[0] for match in self.re_token.finditer(text)]

    def set_alternative(self, alt_text: str) -> None:
        self.alt = self.tokenize(alt_text) + [TokenSequenceMatcher.EOM]
        self.matcher.set_seq1(self.alt)

    def operations(self) -> Iterator[tuple[str, Tokens, Tokens]]:
        """tag meaning is relative to going from alt text to focal text"""

        return (
            (tag, self.alt[a1:a2], self.focus[f1:f2])
            for tag, a1, a2, f1, f2 in self.matcher.get_opcodes()
        )


class DiffAdaptor:
    def __init__(self) -> None:
        self.prev_token: Optional[str] = None
        self.orig_todo: Tokens = []
        self.line_debt = 0

    @staticmethod
    def apply_operations(matcher: TokenSequenceMatcher) -> str:
        tokens = []
        adaptor = DiffAdaptor()
        # ops for converting revised text back to orig
        for tag, rev_chunk, orig_chunk in matcher.operations():
            tokens += adaptor._do_operation(tag, rev_chunk, orig_chunk)
        assert tokens[-1] == TokenSequenceMatcher.EOM
        return "".join(tokens[:-1])

    def _do_operation(self, tag: str, rev: Tokens, orig: Tokens) -> Tokens:
        assert rev or orig
        ret = []
        if tag == "equal" and not self.orig_todo:
            ret = self._adapt_unrevised(rev)
        else:
            self.line_debt += orig.count("\n")
            self.orig_todo += orig
            if len(rev) > 0:
                ret = self._adapt_revised(rev, self.orig_todo)
                self.orig_todo = []
            else:
                if self._undo_delete(self.orig_todo):
                    ret = self.orig_todo
                    self.orig_todo = []
        if ret:
            self.prev_token = ret[-1]
        return ret

    def _undo_delete(self, orig: Tokens) -> bool:
        assert orig
        new_line = (orig[0] == "\n" or self.prev_token in ("\n", None))
        if new_line and all(s.isspace() for s in orig):
            # undo deletion of indentation and extra newlines
            return True
        return False

    def _adapt_unrevised(self, chunk: Tokens) -> Tokens:
        assert chunk
        if self.line_debt > 0 and self.prev_token not in (" ", "\n"):
            if chunk[0] == " ":
                chunk[0] = "\n"
                self.line_debt -= 1
        if len(chunk) > 1:
            self.line_debt = 0
        return chunk

    def _adapt_revised(self, rev: Tokens, orig: Tokens) -> Tokens:
        assert rev or orig
        if rev == [" "] and orig in (['\n'], ['.', '\n'], [',', '\n'], [';', '\n']):
            self.line_debt -= 1
            return ["\n"]
        prev_token = self.prev_token
        for i in range(len(rev)):
            if rev[i] == "\n":
                self.line_debt -= 1
            elif self.line_debt > 0:
                if prev_token in (".", ",", ";"):
                    if rev[i] == " ":
                        rev[i] = "\n"
                        self.line_debt -= 1
            prev_token = rev[i]
        if not orig and rev.count("\n") > 1:
            # insertion of multiple lines
            self.line_debt = 0
        return rev


def diffadapt(orig_text: str, revisions: list[str]) -> list[str]:
    ret = []
    matcher = TokenSequenceMatcher(orig_text)
    for rev_text in revisions:
        if not rev_text.endswith("\n"):
            rev_text += "\n"
        matcher.set_alternative(rev_text)
        ret.append(DiffAdaptor.apply_operations(matcher))
    return ret


def cli(cmd_line_args: Optional[list[str]] = None) -> int:
    import argparse, pathlib
    parser = argparse.ArgumentParser(prog="diffadapt")
    parser.add_argument("src")
    parser.add_argument("rev", nargs="+")
    args = parser.parse_args(cmd_line_args)
    with open(args.src) as file:
        source_text = file.read()
    rev_texts = list()
    for rev in args.rev:
        with open(rev) as file:
            rev_texts.append(file.read())
    rev_texts = diffadapt(source_text, rev_texts)
    for i, rev in enumerate(args.rev):
        with open(rev, "w") as file:
            file.write(rev_texts[i])
    return 0

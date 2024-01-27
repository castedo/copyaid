from copyaid.diff import diffadapt
import tomli

# Python Standard Library
import filecmp, json, logging, os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TextIO
from typing_extensions import Protocol

LOGGER = logging.getLogger('copyaid')
error = LOGGER.error
warning = LOGGER.warning
info = LOGGER.info
debug = LOGGER.debug


class LiveOpenAiApi:
    def __init__(self, api_key: Optional[str] = None):
        from openai import OpenAI  # delay a slow import

        self.client = OpenAI(api_key=api_key)

    def query(self, req: Any) -> Any:
        return self.client.chat.completions.create(**req)


class PromptSettings:
    def __init__(self, path: Path):
        with open(path, "rb") as file:
            data = tomli.load(file)
        self.max_tokens_ratio = data["max_tokens_ratio"]
        self.system_prompt = data["chat_system"]
        self._openai = data.get("openai")
        self._prepend = data.get("prepend", "")
        self._append = data.get("append", "")

    @property
    def num_revisions(self) -> int:
        return int(self._openai.get("n", 1)) if self._openai else 1

    def make_openai_request(self, source: str) -> dict[str, Any]:
        assert isinstance(self._openai, dict)
        ret = dict(self._openai)
        ret["max_tokens"] = max(32, int(self.max_tokens_ratio * len(source) / 4))
        ret["messages"] = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": self._prepend + source + self._append
            },
        ]
        return ret


class ApiProxy:
    ApiClass = LiveOpenAiApi

    def __init__(
        self, api_key: Optional[str], log_path: Path, log_format: Optional[str]
    ):
        self.log_path = log_path
        self.log_format = log_format
        self._api = ApiProxy.ApiClass(api_key)

    def do_request(self, settings: PromptSettings, text: str, name: str) -> list[str]:
        request = settings.make_openai_request(text)
        response = self._api.query(request)
        self.log_openai_query(name, request, response)
        return [c.message.content for c in response.choices]

    def log_openai_query(self, name: str, request: Any, response: Any) -> None:
        if not self.log_format:
            return
        t = datetime.utcfromtimestamp(response.created)
        ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
        response_ex = {
            'choices': {
                '__all__': {
                    'logprobs': {
                        'content': {
                            '__all__': {
                                'bytes': True,
                                'top_logprobs': {
                                    0: True,
                                    '__all__': {'bytes'},
                                },
                            }
                        },
                    },
                }
            },
        }
        response_dump = response.model_dump(exclude_unset=True, exclude=response_ex)
        data = dict(request=request, response=response_dump)
        os.makedirs(self.log_path, exist_ok=True)
        save_stem = name + "." + ts
        print("Logging OpenAI response", save_stem)
        if self.log_format == "jsoml":
            import jsoml
            jsoml.dump(data, self.log_path / (save_stem + ".xml"))
        elif self.log_format == "json":
            with open(self.log_path / (save_stem + ".json"), "w") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.write("\n")
        else:
            warning("Unsupported log format: {}".format(self.log_format))


class WorkFiles:
    def __init__(self, src: str | Path, dest: str | Path, max_num_revs: int = 1):
        assert 0 < max_num_revs < 10
        self.src = Path(src)
        dest = str(dest)
        self._dests = [Path(dest.format(i + 1)) for i in range(max_num_revs)]
        self.dest_glob = dest.format("?")
        self._files: list[TextIO] = list()

    def revisions(self) -> list[Path]:
        return [p for p in self._dests if p.exists()]

    def open_new_dests(self, n: int = 1) -> None:
        assert n > 0
        self._files = []
        for i, path in enumerate(self._dests):
            if i < n:
                os.makedirs(path.parent, exist_ok=True)
                self._files.append(open(path, "w"))
            else:
                path.unlink(missing_ok=True)

    def write_dest(self, text: str, i: int = 1) -> None:
        self._files[i].write(text)
        self._files[i].flush()

    def close_dests(self) -> None:
        for f in self._files:
            f.close()
        self._files = []


@dataclass
class Copybreak:
    raw_line: str
    args: list[str]

    @property
    def keyword(self) -> str | None:
        return self.args[0] if self.args else None

    @property
    def instruction(self) -> str | None:
        return self.args[1] if len(self.args) > 1 else None


@dataclass
class TextSegment:
    copybreak: Copybreak | None
    text: str


class ParsedSource:
    def __init__(self) -> None:
        self.segments: list[TextSegment] = list()

    def instructions(self) -> set[str]:
        ret = set()
        for seg in self.segments:
            if seg.copybreak and seg.copybreak.instruction:
                ret.add(seg.copybreak.instruction)
        return ret


class SourceParserProtocol(Protocol):
    def parse(self, src: Path) -> ParsedSource | None:
        ...


def parse_source(parsers: list[SourceParserProtocol], src: Path) -> ParsedSource:
    for parser in parsers:
        if ret := parser.parse(src):
            return ret
    raise RuntimeError(f"Not able to parse format of {src}")


class TrivialParser:
    def parse(self, src_path: Path) -> ParsedSource | None:
        ret = ParsedSource()
        warning(f"No file format configured for: {src_path}")
        with open(src_path) as file:
            ret.segments.append(TextSegment(None, file.read()))
        return ret


@dataclass
class CopybreakSyntax:
    keywords: list[str]
    prefix: str
    suffix: str | None

    def parse(self, line: str) -> Copybreak | None:
        s = line.strip()
        if not s.startswith(self.prefix):
            return None
        s = s[len(self.prefix):]
        idx = 0
        if self.suffix:
            idx = s.find(self.suffix)
            if idx > 0:
                s = s[:idx]
        candidate = Copybreak(line, s.split())
        if candidate.keyword not in self.keywords:
            return None
        if idx < 0:
            warning("Copybreak line missing suffix '{}'".format(self.suffix))
        return candidate

    @staticmethod
    def from_POD(pod: dict[str, Any]) -> "CopybreakSyntax":
        return CopybreakSyntax(pod["keywords"], pod["prefix"], pod.get("suffix"))


class SimpleParser:
    def __init__(self, copybreak: CopybreakSyntax):
        self.copybreak = copybreak
        self.extensions_filter: list[str] | None = None

    def parse(self, src: Path) -> ParsedSource | None:
        if self.extensions_filter is not None:
            if src.suffix not in self.extensions_filter:
                return None
        ret = ParsedSource()
        pending_copybreak = None
        pending_lines: list[str] = list()
        with open(src) as file:
            for line in file:
                if new_copybreak := self.copybreak.parse(line):
                    segment = TextSegment(pending_copybreak, "".join(pending_lines))
                    ret.segments.append(segment)
                    pending_copybreak = new_copybreak
                    pending_lines = list()
                else:
                    pending_lines.append(line)
            segment = TextSegment(pending_copybreak, "".join(pending_lines))
            ret.segments.append(segment)
        return ret

    @staticmethod
    def from_POD(pod: dict[str, Any]) -> "SimpleParser":
        ret = SimpleParser(CopybreakSyntax.from_POD(pod["copybreak"]))
        ret.extensions_filter = pod.get("extensions")
        return ret


class CopyEditor:
    def __init__(self, api: ApiProxy):
        self.api = api
        self.parsers: list[SourceParserProtocol] = []
        self._instructions: dict[str, PromptSettings | None] = dict()

    @property
    def has_instructions(self) -> bool:
        return any(bool(p) for p in self._instructions.values())

    def set_instruction(self, instruction: str, settings: Path | str) -> None:
        self._instructions[instruction] = PromptSettings(Path(settings))

    def add_off_instruction(self, instruction: str) -> None:
        self._instructions[instruction] = None

    def set_init_instruction(self, instruction: str | None) -> None:
        settings = self._instructions[instruction] if instruction else None
        self._instructions[""] = settings

    def _num_revisions(self, src: ParsedSource) -> int:
        ret = 1
        if init_instr := self._instructions.get(""):
            ret = init_instr.num_revisions
        for iid in src.instructions():
            if iid not in self._instructions:
                raise SyntaxError(f"'{iid}' is not a configured copybreak instruction.")
            if instr := self._instructions.get(iid):
                assert instr.num_revisions > 0
                if ret == 1:
                    if instr.num_revisions > ret:
                        ret = instr.num_revisions
                elif instr.num_revisions > 1:
                    if instr.num_revisions < ret:
                        ret = instr.num_revisions
                        warning(f"Instruction {iid} sets number of revisions to {ret}.")
                    elif instr.num_revisions > ret:
                        msg = "Only {} of {} revisions used with instruction {}."
                        warning(msg.format(ret, instr.num_revisions, iid))
        return ret

    def revise(self, work: WorkFiles) -> None:
        parsed = parse_source(self.parsers, work.src)
        num_revisions = self._num_revisions(parsed)
        work.open_new_dests(num_revisions)
        cur_settings = self._instructions.get("")
        for si, seg in enumerate(parsed.segments):
            if seg.copybreak:
                for ri in range(num_revisions):
                    work.write_dest(seg.copybreak.raw_line, ri)
                if seg.copybreak.instruction:
                    cur_settings = self._instructions[seg.copybreak.instruction]
            log_name = "{}.{}".format(work.src.stem, si)
            if cur_settings and len(seg.text.strip()):
                revisions = self.api.do_request(cur_settings, seg.text, log_name)
                if len(revisions) > num_revisions:
                    revisions = revisions[:num_revisions]
                elif len(revisions) == 1 and num_revisions > 1:
                    revisions = list(revisions[0]) * num_revisions
                assert len(revisions) == num_revisions
                revisions = diffadapt(seg.text, revisions)
            else:
                revisions = [seg.text] * num_revisions
            for ri, rev in enumerate(revisions):
                work.write_dest(rev, ri)
        work.close_dests()

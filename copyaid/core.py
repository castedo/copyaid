from copyaid.diff import diffadapt
import tomli

# Python Standard Library
import filecmp, json, os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, TextIO
from warnings import warn
from typing_extensions import Protocol


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
            warn("Unsupported log format: {}".format(self.log_format))


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

    def one_revision_equal_to_source(self) -> Path | None:
        ret = None
        if len(self._dests) == 1:
            one = self._dests[0]
            if one.exists() and filecmp.cmp(self.src, one, shallow=False):
                ret = one
        return ret

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

    def close_dests(self) -> None:
        for f in self._files:
            f.close()
        self._files = []


@dataclass
class Copybreak:
    raw_line: str
    args: list[str]

    @property
    def instruction(self) -> str | None:
        return self.args[0] if self.args else None


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
        with open(src_path) as file:
            ret.segments.append(TextSegment(None, file.read()))
        return ret


@dataclass
class CopybreakSyntax:
    ids: list[str]
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
        if candidate.instruction not in self.ids:
            return None
        if idx < 0:
            warn("Copybreak line missing suffix '{}'".format(self.suffix))
        return candidate


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


class CopyEditor:
    def __init__(self, api: ApiProxy):
        self.api = api
        self.parsers: list[SourceParserProtocol] = []
        self.init_instruct_id: str | None = None
        self.instructions: dict[str, PromptSettings | None] = dict()

    @property
    def has_instructions(self) -> bool:
        iid = self.init_instruct_id
        return bool(iid) and iid in self.instructions

    def add_off_instruction(self, instruct_id: str) -> None:
        self.instructions[instruct_id] = None

    def add_instruction(self, instruct_id: str, settings: Path | str) -> None:
        self.instructions[instruct_id] = PromptSettings(Path(settings))

    def revise(self, work: WorkFiles) -> None:
        assert self.init_instruct_id is not None
        settings = self.instructions[self.init_instruct_id]
        assert settings
        parsed = parse_source(self.parsers, work.src)
        work.open_new_dests(settings.num_revisions)
        for si, seg in enumerate(parsed.segments):
            if seg.copybreak:
                for ri in range(settings.num_revisions):
                    work.write_dest(seg.copybreak.raw_line, ri)
            log_name = "{}.{}".format(work.src.stem, si)
            revisions = self.api.do_request(settings, seg.text, log_name)
            assert len(revisions) == settings.num_revisions
            revisions = diffadapt(seg.text, revisions)
            for ri, rev in enumerate(revisions):
                work.write_dest(rev, ri)
        work.close_dests()

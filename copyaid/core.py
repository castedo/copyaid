import tomli

# Python Standard Library
import filecmp, json, os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
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

    def revisions(self) -> list[Path]:
        return [p for p in self._dests if p.exists()]

    def one_revision_equal_to_source(self) -> Path | None:
        ret = None
        if len(self._dests) == 1:
            one = self._dests[0]
            if one.exists() and filecmp.cmp(self.src, one, shallow=False):
                ret = one
        return ret

    def write_revisions(self, revisions: list[str]) -> None:
        for i, path in enumerate(self._dests):
            if i < len(revisions):
                os.makedirs(path.parent, exist_ok=True)
                with open(path, "w") as file:
                    file.write(revisions[i])
            else:
                path.unlink(missing_ok=True)


class ParsedSource:
    def __init__(self, contents: str):
        self.contents = contents


class SourceParserProtocol(Protocol):
    def parse(self, src_path: Path) -> ParsedSource | None:
        ...


class CopyEditor:
    def __init__(self, api: ApiProxy):
        self.api = api
        self._parsers: list[SourceParserProtocol] = []
        self.init_instruct_id: str | None = None
        self.instructions: dict[str, PromptSettings | None] = dict()

    @property
    def has_instructions(self) -> bool:
        iid = self.init_instruct_id
        return bool(iid) and iid in self.instructions

    def add_parser(self, p: SourceParserProtocol) -> None:
        self._parsers.append(p)

    def add_off_instruction(self, instruct_id: str) -> None:
        self.instructions[instruct_id] = None

    def add_instruction(self, instruct_id: str, settings: Path | str) -> None:
        self.instructions[instruct_id] = PromptSettings(Path(settings))

    def revise(self, work: WorkFiles) -> None:
        assert self.init_instruct_id is not None
        settings = self.instructions[self.init_instruct_id]
        assert settings
        parsed = None
        for parser in self._parsers:
            parsed = parser.parse(work.src)
            if parsed:
                break
        if parsed is None:
            raise RuntimeError(f"Not able to parse format of {work.src}")
        revisions = self.api.do_request(settings, parsed.contents, work.src.stem)
        work.write_revisions(revisions)

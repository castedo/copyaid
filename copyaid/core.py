# Python Standard Library
import json, os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from warnings import warn


class LiveOpenAiApi:
    def __init__(self, api_key: Optional[str] = None):
        import openai  # delay a very slow import

        if api_key is not None:
            openai.api_key = api_key

    def query(self, req: Any) -> Any:
        import openai

        return openai.ChatCompletion.create(**req)  # type: ignore


def make_openai_request(settings: Any, source: str) -> Any:
    ret = settings["openai"]
    ret["max_tokens"] = max(6, int(settings["max_tokens_ratio"] * len(source) / 4))
    prompt = settings.get("prepend", "") + source + settings.get("append", "")
    ret["messages"] = [
        {
            "role": "system",
            "content": settings["chat_system"]
        },
        {
            "role": "user",
            "content": prompt
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

    def do_request(self, settings: Any, src_path: Path) -> list[str]:
        with open(src_path) as file:
            source_text = file.read()
        request = make_openai_request(settings, source_text)
        response = self._api.query(request)
        self.log_openai_query(src_path.stem, request, response)
        revisions = list()
        for choice in response.get("choices", []):
            text = choice.get("message", {}).get("content")
            revisions.append(text)
        return revisions

    def log_openai_query(self, name: str, request: Any, response: Any) -> None:
        if not self.log_format:
            return
        t = datetime.utcfromtimestamp(response["created"])
        ts = t.isoformat().replace("-", "").replace(":", "") + "Z"
        data = dict(request=request, response=response)
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

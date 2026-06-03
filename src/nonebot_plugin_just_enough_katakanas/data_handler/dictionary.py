import json

import httpx
import aiofiles
import nonebot_plugin_localstore as localstore
from nonebot import require

require("nonebot_plugin_localstore")
dict_path = localstore.get_plugin_data_dir() / "katakana_dict.jsonl"


class DictionaryHandler:
    def __init__(self) -> None:
        self.dict_path = dict_path

    def check_dictionary(self) -> bool:
        return self.dict_path.exists()

    async def download_dictionary(self) -> None:
        url = "https://github.com/Patchethium/e2k/releases/download/0.2.0/katakana_dict.jsonl"

        self.dict_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                async with client.stream("GET", url) as r:
                    r.raise_for_status()

                    async with aiofiles.open(str(self.dict_path), "wb") as f:
                        async for chunk in r.aiter_bytes():
                            if chunk:
                                await f.write(chunk)

            if not self.dict_path.exists() or self.dict_path.stat().st_size == 0:
                raise RuntimeError("downloaded dictionary is empty")
        except Exception:
            try:
                if self.dict_path.exists():
                    self.dict_path.unlink()
            except Exception:
                pass
            raise

    def load_dictionary(self) -> dict[str, list[str]]:
        if not self.dict_path.exists():
            return {}

        ktkn_dict: dict[str, list[str]] = {}
        with open(self.dict_path, encoding="utf-8") as f:
            for line in f:
                loading_line = json.loads(line)
                word = loading_line["word"]
                katakanas = loading_line["kata"]
                ktkn_dict[word] = katakanas
        return ktkn_dict


ktkndict = DictionaryHandler()

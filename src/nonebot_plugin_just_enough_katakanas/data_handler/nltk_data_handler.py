import asyncio

import nltk
from nonebot import require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as localstore

data_dir = localstore.get_plugin_data_dir()

_NLTK_RESOURCES: dict[str, str] = {
    "cmudict": "corpora/cmudict",
    "averaged_perceptron_tagger": "taggers/averaged_perceptron_tagger",
    "punkt": "tokenizers/punkt",
    "punkt_tab": "tokenizers/punkt_tab",
}


class NLTKDataHandler:
    def __init__(self) -> None:
        self.nltk_data_dir = str(data_dir / "nltk_data")
        nltk.data.path.insert(0, str(self.nltk_data_dir))

    @staticmethod
    def _check_resource_local(resource_path: str) -> bool:
        try:
            nltk.data.find(resource_path)
            return True
        except LookupError:
            return False

    def _ensure_nltk_resources_sync(self) -> tuple[bool, bool, bool, bool, str]:
        results: list[bool] = []
        for name, path in _NLTK_RESOURCES.items():
            if self._check_resource_local(path):
                results.append(True)
            else:
                status = nltk.download(
                    name,
                    download_dir=str(self.nltk_data_dir),
                    quiet=True,
                )
                results.append(status)
        return (
            results[0],
            results[1],
            results[2],
            results[3],
            self.nltk_data_dir,
        )

    async def ensure_nltk_resources(self) -> tuple[bool, bool, bool, bool, str]:
        return await asyncio.to_thread(self._ensure_nltk_resources_sync)


nltk_data = NLTKDataHandler()

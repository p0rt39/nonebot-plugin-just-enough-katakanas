import asyncio

import nltk
import nonebot_plugin_localstore as localstore
from nonebot import require

require("nonebot_plugin_localstore")
data_dir = localstore.get_plugin_data_dir()


class NLTKDataHandler:
    def __init__(self) -> None:
        self.nltk_data_dir = str(data_dir / "nltk_data")
        nltk.data.path.insert(0, str(self.nltk_data_dir))

    def _ensure_nltk_resources_sync(self) -> tuple[bool, bool, bool, bool, str]:
        cmudict_status = nltk.download(
            "cmudict",
            download_dir=str(self.nltk_data_dir),
            quiet=True,
        )
        tagger_status = nltk.download(
            "averaged_perceptron_tagger",
            download_dir=str(self.nltk_data_dir),
            quiet=True,
        )
        punkt_status = nltk.download(
            "punkt",
            download_dir=str(self.nltk_data_dir),
            quiet=True,
        )
        punkt_tab_status = nltk.download(
            "punkt_tab",
            download_dir=str(self.nltk_data_dir),
            quiet=True,
        )

        return (
            cmudict_status,
            tagger_status,
            punkt_status,
            punkt_tab_status,
            self.nltk_data_dir,
        )

    async def ensure_nltk_resources(self) -> tuple[bool, bool, bool, bool, str]:
        return await asyncio.to_thread(self._ensure_nltk_resources_sync)


nltk_data = NLTKDataHandler()

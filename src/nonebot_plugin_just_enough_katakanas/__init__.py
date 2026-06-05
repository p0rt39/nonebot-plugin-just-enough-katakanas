from nonebot import logger, require, get_driver, on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message

from .data_handler.dictionary import ktkndict
from .engines.eng2ktkn_engine import eng2ktkn_engine
from .data_handler.nltk_data_handler import nltk_data

require("nonebot_plugin_localstore")


__plugin_meta__ = PluginMetadata(
    name="Just Enough Katakanas",
    description="A plugin to convert English text to Katakana.\n"
    "Supports both dictionary-based and phonetic conversion methods.",
    usage=(
        "/ktkn <English text> - "
        "Convert the provided English text(word or sentence) to Katakana.\n"
        "/ktknstatus - "
        "Check the status of the plugin's dictionary and conversion functionality."
    ),
    type="application",
    homepage="https://github.com/p0rt39/nonebot-plugin-just-enough-katakanas",
    config=None,  # WIP so NO configuration options yet.
    supported_adapters=None,  # WIP so NO adapter-specific features yet.
    extra={"author": "p0rt39 YuibataMiraa@gmail.com"},
)

ktkn = on_command("ktkn", aliases={"eng2ktkn"}, priority=5)
ktknstatus = on_command("ktknstatus", aliases={"eng2ktknstatus"}, priority=4)
ktknhelp = on_command("ktknhelp", aliases={"eng2ktknhelp"}, priority=4)

plugin_enabled = False
dict_enabled = False

driver = get_driver()


@driver.on_startup
async def _startup_initialization() -> None:
    global plugin_enabled

    logger.info(
        "Just Enough Katakanas is verifying resources."
        "During this session, the functions will be temporarily unavailable."
    )
    try:
        logger.info(
            "Checking NLTK resources..."
            "If got stuck here, please check network connection to Github."
        )
        nltk_status = await nltk_data.ensure_nltk_resources()
        # This would wait for nltk data to be verified
        logger.info(
            "NLTK resources status: "
            f"cmudict={nltk_status[0]}, "
            f"tagger={nltk_status[1]}, "
            f"punkt={nltk_status[2]}, "
            f"punkt_tab={nltk_status[3]}, "
            f"data_dir={nltk_status[4]}"
        )
        if not all(nltk_status[::3]):
            logger.error("One or more NLTK resources failed to download.")
            plugin_enabled = False
    except Exception:
        logger.error("Failed to ensure NLTK resources during startup.")
        plugin_enabled = False
        # This plugin won't work properly without ensuring NLTK resource

    try:
        eng2ktkn_engine.get_g2p()
        logger.info("Verified NLTK resources within engine.")
        plugin_enabled = True
    except Exception:
        logger.error("Failed to verify NLTK resources within engine.")
        plugin_enabled = False

    global dict_enabled

    if ktkndict.check_dictionary():  # Check if dictionary exists
        logger.info("Dictionary is present. Loading into engine...")
        try:
            eng2ktkn_engine.ktkn_dict = ktkndict.load_dictionary()
            logger.info("Dictionary loaded successfully.")
            dict_enabled = True
        except Exception:
            logger.error("Failed to refresh eng2ktkn_engine dictionary after check.")
        return

    logger.warning("Dictionary database not found. Attempting to download...")
    if await ktkndict.ensure_dictionary():
        logger.info("Dictionary downloaded successfully. Loading into engine...")
        try:
            eng2ktkn_engine.ktkn_dict = ktkndict.load_dictionary()
            logger.info("Dictionary loaded successfully.")
            dict_enabled = True
        except Exception:
            logger.error(
                "Failed to load dictionary into engine after download."
                "Dictionary-based conversion will be unavailable."
            )
            dict_enabled = False

    if not plugin_enabled:
        logger.critical("Just Enough Katakanas DISABLED due to NLTK_data Failure.")
    if plugin_enabled:
        logger.info("Just Enough Katakanas is good to go!")


@ktknstatus.handle()
async def handle_ktkn_status() -> None:
    if not plugin_enabled:
        await ktknstatus.finish()
    test_word = "test"
    test_sentence = "The quick brown fox jumps over the lazy dog.".strip()

    converted_word = eng2ktkn_engine.english_to_katakana(test_word)
    converted_sentence = eng2ktkn_engine.english_to_katakana(test_sentence)

    word_test_flag = bool(converted_word)
    sentence_test_flag = bool(converted_sentence)

    # Only checks if conversion returns a non-empty result,
    # not the correctness of the conversion itself
    # Built-in test and debug is WIP
    result_message = (
        f"Dictionary: {'enabled' if dict_enabled else 'disabled'}.\n"
        + f"Word conversion test: {'passed' if word_test_flag else 'failed'}.\n"
        + f"Sentence conversion test: {'passed' if sentence_test_flag else 'failed'}."
    )

    await ktknstatus.finish(result_message)


@ktknhelp.handle()
async def handle_ktkn_help() -> None:
    if not plugin_enabled:
        await ktknhelp.finish()
    help_message = (
        "/ktkn <English text> - "
        "Convert the provided English text (word or sentence) to Katakana.\n"
        "/ktknstatus - "
        "Check the status of the plugin's dictionary and conversion functionality.\n"
        "/ktknhelp - "
        "Show this help message."
    )
    await ktknhelp.finish(help_message)


@ktkn.handle()
async def handle_ktkn_command(args: Message = CommandArg()) -> None:
    if not plugin_enabled:
        await ktkn.finish()
    original_text = args.extract_plain_text().strip()

    if original_text:
        word_count = len(eng2ktkn_engine.extract_words(original_text))
        conversion_source, converted_list = eng2ktkn_engine.english_to_katakana(
            original_text
        )
        # The eng2ktkn_engine will return conversion_source
        # to indicate the source of the results
        # Possible values: "dictionary", "phonetic", "passthrough"

        if word_count <= 1 and conversion_source == "dictionary":
            result = "Dictionary lookup result(s):\n"
            result += "\n".join(converted_list)
            logger.debug(f"Dictionary lookup result(s): {converted_list}")
            await ktkn.finish(result)

        if (
            word_count <= 1
            and conversion_source == "phonetic"
            and len(converted_list) == 1
        ):
            result = "Phonetic converted result:\n"
            result += converted_list[0]
            logger.debug(f"Phonetic converted result: {converted_list[0]}")
            await ktkn.finish(result)

        if (
            word_count <= 1
            and conversion_source == "passthrough"
            and len(converted_list) == 1
        ):
            logger.warning("Illegal input. Ignored.")
            await ktkn.finish()  # Illegal input, won't return

        # if word_count > 1, the matcher will strip and convert words separately
        # In this case, the conversion_source will be ignored
        sentence_output = "\n".join(
            f"{item}" for index, item in enumerate(converted_list, 1)
        )

        logger.debug(f"Sentence conversion result: {sentence_output}")
        await ktkn.finish(sentence_output)
    else:
        logger.debug("No input provided for conversion.")
        await ktkn.finish("Please provide the English line to convert to Katakana.")
        # Won't wait for further input

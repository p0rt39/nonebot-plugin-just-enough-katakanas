from nonebot import logger, on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.adapters import Message

from .dictionary import database
from .eng2ktkn_engine import engine

__plugin_meta__ = PluginMetadata(
    name="Just Enough Katakanas",
    description="A plugin to convert English text to Katakana."
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

dict_enabled = False
if database.create_connection():  # Check if database connection is established
    logger.info("Dictionary database initialized successfully.")

    dict_enabled = True
else:
    logger.warning(
        "Dictionary database not found. Dictionary features will be disabled."
    )  # Fall back to phonetic conversion only


@ktknstatus.handle()
async def handle_ktkn_status() -> None:
    test_word = "test"
    test_sentence = "The quick brown fox jumps over the lazy dog.".strip()

    converted_word = engine.english_to_katakana(test_word)
    converted_sentence = engine.english_to_katakana(test_sentence)

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
    help_message = (
        "/ktkn <English text> - "
        "Convert the provided English text (word or sentence) to Katakana.\n"
        "/ktknstatus - "
        "Check the status of the plugin's dictionary and conversion functionality.\n"
        "/ktknhelp - "
        "Show this help message.\n"
    )
    await ktknhelp.finish(help_message)


@ktkn.handle()
async def handle_ktkn_command(args: Message = CommandArg()) -> None:
    original_text = args.extract_plain_text().strip()

    if original_text:
        word_count = len(engine.extract_words(original_text))
        conversion_source, converted_list = engine.english_to_katakana(original_text)
        # The engine will return conversion_source to indicate the source of the results
        # Possible values: "dictionary", "phonetic", "passthrough"

        if word_count <= 1 and conversion_source == "dictionary":
            result = "Dictionary lookup result(s):\n"
            result += "\n".join(converted_list)
            logger.debug("Dictionary lookup success.")
            await ktkn.finish(result)

        if (
            word_count <= 1
            and conversion_source == "phonetic"
            and len(converted_list) == 1
        ):
            result = "Phonetic converted result:\n"
            result += converted_list[0]
            logger.debug("Phonetic converted success.")
            await ktkn.finish(result)

        if (
            word_count <= 1
            and conversion_source == "passthrough"
            and len(converted_list) == 1
        ):
            logger.warning("Illegal input. Ignored.")
            await ktkn.finish()  # Illegal input, won't return

        # if word_count > 1, the matcher will strip and convert words seperately
        # In this case, the conversion_source will be ignored
        sentence_output = "\n".join(
            f"{item}" for index, item in enumerate(converted_list, 1)
        )

        logger.debug("Sentence conversion result: %s", sentence_output)
        await ktkn.finish(sentence_output)
    else:
        logger.debug("No input provided for conversion.")
        await ktkn.finish("Please provide the English line to convert to Katakana.")
        # Won't wait for further input.

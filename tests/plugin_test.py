import pytest
from fake import fake_group_message_event_v11
from nonebug import App


@pytest.mark.asyncio
async def test_ktkn_empty(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    event = fake_group_message_event_v11(message="/ktkn")
    try:
        from nonebot_plugin_just_enough_katakanas import ktkn  # type:ignore
    except ImportError:
        pytest.skip("nonebot_plugin_just_enough_katakanas.ktkn not found")

    async with app.test_matcher(ktkn) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "Please provide the English line to convert to Katakana.",
            result=None,
            bot=bot,
        )
        ctx.should_finished()


@pytest.mark.asyncio
async def test_ktkn_dict(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    event = fake_group_message_event_v11(message="/ktkn test")
    try:
        from nonebot_plugin_just_enough_katakanas import ktkn  # type:ignore
    except ImportError:
        pytest.skip("nonebot_plugin_just_enough_katakanas.ktkn not found")

    async with app.test_matcher(ktkn) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event, "Dictionary lookup result(s):\nテスト", result=None, bot=bot
        )
        ctx.should_finished()


@pytest.mark.asyncio
async def test_ktkn_sentence(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    event = fake_group_message_event_v11(
        message="/ktkn A quick brown fox jumps over the lazy dog."
    )
    try:
        from nonebot_plugin_just_enough_katakanas import ktkn  # type:ignore
    except ImportError:
        pytest.skip("nonebot_plugin_just_enough_katakanas.ktkn not found")

    async with app.test_matcher(ktkn) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event,
            "アー クイック ブラウン フォックス "
            "ジャンプス オーバー イー レージー ドッグ.",
            result=None,
            bot=bot,
        )
        ctx.should_finished()


@pytest.mark.asyncio
async def test_ktkn_phonetic(app: App):
    import nonebot
    from nonebot.adapters.onebot.v11 import Bot
    from nonebot.adapters.onebot.v11 import Adapter as OnebotV11Adapter

    event = fake_group_message_event_v11(message="/ktkn ssvgg")
    try:
        from nonebot_plugin_just_enough_katakanas import ktkn  # type:ignore
    except ImportError:
        pytest.skip("nonebot_plugin_just_enough_katakanas.ktkn not found")

    async with app.test_matcher(ktkn) as ctx:
        adapter = nonebot.get_adapter(OnebotV11Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_call_send(
            event, "Phonetic converted result:\nセブグ", result=None, bot=bot
        )
        ctx.should_finished()

from os import getenv

import requests
from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from notifiers import get_notifier

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")
IMGFLIP_API_URL = "https://api.imgflip.com"

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix="!", case_insensitive=True, intents=intents
)


class MemeGenerator:
    def __init__(self) -> None:
        # Sem môžete pridať vlastné atribúty.
        pass

    def list_memes(self) -> str:
        # TODO: Implementujte túto metódu
        # Tip 1: Prečítajte si dokumentáciu imgflip API.
        # Tip 2: Pomocou modulu requests vytvorte GET požiadavku na
        #        endpoint https://api.imgflip.com/get_memes.
        # Tip 3: Preskúmajte, ako vyzerá odpoveď API (response.json()).
        return ""

    def make_meme(
        self, template_id: int, top_text: str, bottom_text: str
    ) -> str:
        # TODO: Implementujte túto metódu
        # Tip 1: Pomocou modulu requests vytvorte POST požiadavku na
        #        endpoint https://api.imgflip.com/caption_image.
        # Tip 2: Použite parameter `params` na vloženie parametrov.
        # Tip 3: Preskúmajte, ako vyzerá odpoveď API (response.json()).

        # Vráťte URL vygenerovaného meme.
        return ""


class MentionsNotifier:
    def __init__(self) -> None:
        # Sem môžete pridať vlastné atribúty.
        pass

    def subscribe(self, user_id: int, email: str) -> None:
        # TODO: Implementujte túto metódu.
        pass

    def unsubscribe(self, user_id: int) -> None:
        # TODO: Implementujte túto metódu.
        pass

    def notify_about_mention(self, user_id: int, msg_content: str) -> None:
        # TODO: Implementujte túto metódu.
        pass


class Hangman:
    # TODO: Využite túto triedu pri implementácii hry hangman,
    #       vytvorenie atribútov a metód je na vás.
    pass


# --------- LEVEL 1 ----------
meme_generator = MemeGenerator()


@bot.command(name="list_memes")
async def list_memes(ctx: Context) -> None:
    meme_list = meme_generator.list_memes()
    # TODO: Poslať meme_list do kanála.


@bot.command(name="make_meme")
async def make_meme(
    ctx: Context, template_id: int, top_text: str, bottom_text: str
) -> None:
    meme_url = meme_generator.make_meme(template_id, top_text, bottom_text)
    # TODO: Poslať meme_url do kanála.


# --------- LEVEL 2 ----------
mentions_notifier = MentionsNotifier()


@bot.command(name="subscribe")
async def subscribe(ctx: Context, email: str) -> None:
    mentions_notifier.subscribe(ctx.author.id, email)


@bot.command(name="unsubscribe")
async def unsubscribe(ctx: Context) -> None:
    mentions_notifier.unsubscribe(ctx.author.id)


@bot.event
async def on_message(message: Message) -> None:
    # TODO: upravte túto funkciu tak, aby v prípade označenia používateľa
    #       v správe `message` mu bolo poslané oznámenie.

    # Nasledujúci riadok nemodifikujte, inak príkazy bota nebudú fungovať.
    await bot.process_commands(message)


# --------- LEVEL 3 ----------
hangman = Hangman()


@bot.command(name="play_hangman")
async def play_hangman(ctx: Context) -> None:
    # TODO: Implementujte tento príkaz s využitím triedy Hangman.
    pass


@bot.command(name="guess")
async def guess(ctx: Context, letter: str) -> None:
    # TODO: Implementujte tento príkaz s využitím triedy Hangman.
    pass


bot.run(TOKEN)

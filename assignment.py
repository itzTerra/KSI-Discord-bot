from os import getenv

import requests
from discord import Intents, Message
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
from notifiers import get_notifier
from typing import List, Dict
from random import choice

load_dotenv()
TOKEN = getenv("DISCORD_TOKEN")
IMGFLIP_API_URL = "https://api.imgflip.com"

IMGFLIP_USERNAME = getenv("IMGFLIP_USERNAME")
IMGFLIP_PASSWORD = getenv("IMGFLIP_PASSWORD")

EMAIL_USERNAME = getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD")

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
        response = requests.get(IMGFLIP_API_URL + "/get_memes").json()
        if not response["success"]:
            return ":exclamation: " + response["error_message"]

        memes = response["data"]["memes"][:25]
        meme_list = [f'{meme["id"]:<9} {meme["name"]}' for meme in memes]
        return "\n".join(meme_list)

    def make_meme(
        self, template_id: int, top_text: str, bottom_text: str
    ) -> str:
        data = {
            "template_id": template_id,
            "username": IMGFLIP_USERNAME,
            "password": IMGFLIP_PASSWORD,
            "text0": top_text,
            "text1": bottom_text
        }

        response = requests.post(
            IMGFLIP_API_URL + "/caption_image", data=data
        ).json()
        if not response["success"]:
            return ":exclamation: " + response["error_message"]

        return response["data"]["url"]


class MentionsNotifier:
    def __init__(self) -> None:
        self.subscribed_users = {}
        self.__mailer = get_notifier("email")
        self.__email_settings = {
            "host": "ksi2022smtp.iamroot.eu",
            "port": 465,
            "ssl": True,
            "username": EMAIL_USERNAME,
            "password": EMAIL_PASSWORD,
            "from": EMAIL_USERNAME,
        }

    def subscribe(self, user_id: int, email: str) -> None:
        self.subscribed_users[user_id] = email

    def unsubscribe(self, user_id: int) -> None:
        self.subscribed_users.pop(user_id, None)

    def notify_about_mention(self, user_id: int, msg_content: str) -> None:
        self.__mailer.notify(
            **self.__email_settings,
            to=self.subscribed_users[user_id],
            subject="Discord Mention",
            message=msg_content,
        )


class HangmanGame:
    def __init__(self, player_name: str, word: str) -> None:
        self._player = player_name
        self.guesses: List[str] = []
        self.lives = 7
        self.word = word

        self._word_display = " ".join("-" * len(self.word))
        self.missing_letters = len(self.word)

        self.msg_instance = None

    def update_word_display(self) -> None:
        word_info = []
        missing_letters = 0
        for char in self.word:
            if char in self.guesses:
                word_info.append(char)
            else:
                word_info.append("-")
                missing_letters += 1

        self._word_display = " ".join(word_info)
        self.missing_letters = missing_letters

    def get_game_info(self) -> str:
        return (
            "**Hangman**\n"
            f"Player: {self._player}\n"
            f"Guesses: {', '.join(self.guesses)}\n"
            f"Lives: {self.lives}\n"
            f"Word: {self._word_display}"
        )


class Hangman:
    def __init__(self) -> None:
        with open("words.txt") as file:
            words = []
            for line in file.readlines():
                words.append(line.strip().upper())
        self._words = words
        self._active_games: Dict[int, HangmanGame] = {}

    def start_game(self, user_id: int, user_name: str) -> HangmanGame:
        new_game = HangmanGame(user_name, choice(self._words))
        self._active_games[user_id] = new_game
        return new_game

    def guess(self, user_id: int, letter: str) -> str:
        game = self._active_games[user_id]
        status_message = ""

        if len(letter) > 1 or not letter.isalpha():
            status_message = "Enter only 1 letter at a time."
        elif letter in game.guesses:
            status_message = "You already guessed that."
        else:
            game.guesses.append(letter)

            if letter in game.word:
                game.update_word_display()

                if (game.missing_letters > 0):
                    status_message = "Correct guess."
                else:
                    status_message = "You won!"
                    self._end_game(user_id)
            else:
                game.lives -= 1

                if (game.lives > 0):
                    status_message = "Wrong guess."
                else:
                    word = game.word.lower()
                    status_message = f"You lost! The word was: {word}"
                    self._end_game(user_id)

        return game.get_game_info() + "\n" + status_message

    def get_game(self, user_id: int) -> HangmanGame | None:
        return self._active_games.get(user_id, None)

    def _end_game(self, user_id: int) -> None:
        self._active_games.pop(user_id)


# --------- LEVEL 1 ----------
meme_generator = MemeGenerator()


@bot.command(name="list_memes")
async def list_memes(ctx: Context) -> None:
    meme_list = meme_generator.list_memes()
    await ctx.send("**Memes**\n" + f"```{meme_list}```")


@bot.command(name="make_meme")
async def make_meme(
    ctx: Context, template_id: int, top_text: str, bottom_text: str
) -> None:
    meme_url = meme_generator.make_meme(template_id, top_text, bottom_text)
    await ctx.send(meme_url)


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
    notif_message = f"Someone mentioned you in channel {message.jump_url}"
    for user in message.mentions:
        if user.id in mentions_notifier.subscribed_users:
            mentions_notifier.notify_about_mention(user.id, notif_message)

    # Nasledujúci riadok nemodifikujte, inak príkazy bota nebudú fungovať.
    await bot.process_commands(message)


# --------- LEVEL 3 ----------
hangman = Hangman()


@bot.command(name="play_hangman")
async def play_hangman(ctx: Context) -> None:
    msg = await ctx.send("Starting a new game...")
    game = hangman.start_game(ctx.author.id, ctx.author.display_name)

    game.msg_instance = await msg.edit(content=game.get_game_info())


@bot.command(name="guess")
async def guess(ctx: Context, letter: str) -> None:
    game = hangman.get_game(ctx.author.id)
    if game:
        game_info = hangman.guess(ctx.author.id, letter.upper())
        game.msg_instance = await game.msg_instance.edit(content=game_info)
        await ctx.message.delete()
    else:
        await ctx.send("You have to start a new game first.")


bot.run(TOKEN)

import os
from typing import Optional, Dict

import aiohttp
import discord
from discord import app_commands, ui
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # необязательно: мгновенная синхронизация команд на одном сервере
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")  # Server-side key: https://developers.faceit.com
VERIFY_URL = os.getenv("VERIFY_URL")  # куда ведёт кнопка-ссылка; по умолчанию — профиль игрока на FACEIT

FACEIT_ORANGE = discord.Colour(0xFF5500)
ASSETS = os.path.join(os.path.dirname(__file__), "assets")
GAMES = ("cs2", "csgo")  # в каком порядке искать статистику игрока

LANGUAGES = {
    "en": {"label": "English", "emoji": "🇬🇧"},
    "ru": {"label": "Русский", "emoji": "🇷🇺"},
    "uk": {"label": "Українська", "emoji": "🇺🇦"},
    "pl": {"label": "Polski", "emoji": "🇵🇱"},
    "de": {"label": "Deutsch", "emoji": "🇩🇪"},
    "tr": {"label": "Türkçe", "emoji": "🇹🇷"},
}

TEXTS = {
    "en": {
        "modal_title": "FACEIT verification",
        "nick_label": "Your FACEIT nickname",
        "nick_placeholder": "e.g. s1mple",
        "not_found": "❌ FACEIT profile **{nick}** was not found. Check the nickname and choose your language again.",
        "api_error": "⚠️ Could not reach FACEIT right now. Please try again later.",
        "title": "FACEIT verification for {nick}",
        "level": "Level",
        "kd": "K/D",
        "description": (
            "To start the match you need to confirm your FACEIT account.\n\n"
            "To continue the verification process, use the button below"
        ),
        "button": "Go to FACEIT verification",
    },
    "ru": {
        "modal_title": "Верификация FACEIT",
        "nick_label": "Ваш никнейм FACEIT",
        "nick_placeholder": "например, s1mple",
        "not_found": "❌ Профиль FACEIT **{nick}** не найден. Проверьте никнейм и выберите язык ещё раз.",
        "api_error": "⚠️ Не удалось связаться с FACEIT. Попробуйте позже.",
        "title": "Верификация FACEIT для {nick}",
        "level": "Уровень",
        "kd": "K/D",
        "description": (
            "Для начала матча необходимо подтвердить вашу учетную запись FACEIT.\n\n"
            "Для того чтобы продолжить процесс верификации, используйте кнопку ниже"
        ),
        "button": "Перейти к верификации FACEIT",
    },
    "uk": {
        "modal_title": "Верифікація FACEIT",
        "nick_label": "Ваш нікнейм FACEIT",
        "nick_placeholder": "наприклад, s1mple",
        "not_found": "❌ Профіль FACEIT **{nick}** не знайдено. Перевірте нікнейм і виберіть мову ще раз.",
        "api_error": "⚠️ Не вдалося зв'язатися з FACEIT. Спробуйте пізніше.",
        "title": "Верифікація FACEIT для {nick}",
        "level": "Рівень",
        "kd": "K/D",
        "description": (
            "Для початку матчу необхідно підтвердити ваш обліковий запис FACEIT.\n\n"
            "Щоб продовжити процес верифікації, скористайтеся кнопкою нижче"
        ),
        "button": "Перейти до верифікації FACEIT",
    },
    "pl": {
        "modal_title": "Weryfikacja FACEIT",
        "nick_label": "Twój nick FACEIT",
        "nick_placeholder": "np. s1mple",
        "not_found": "❌ Nie znaleziono profilu FACEIT **{nick}**. Sprawdź nick i wybierz język ponownie.",
        "api_error": "⚠️ Nie udało się połączyć z FACEIT. Spróbuj ponownie później.",
        "title": "Weryfikacja FACEIT dla {nick}",
        "level": "Poziom",
        "kd": "K/D",
        "description": (
            "Aby rozpocząć mecz, musisz potwierdzić swoje konto FACEIT.\n\n"
            "Aby kontynuować weryfikację, użyj przycisku poniżej"
        ),
        "button": "Przejdź do weryfikacji FACEIT",
    },
    "de": {
        "modal_title": "FACEIT-Verifizierung",
        "nick_label": "Dein FACEIT-Nickname",
        "nick_placeholder": "z. B. s1mple",
        "not_found": "❌ FACEIT-Profil **{nick}** wurde nicht gefunden. Prüfe den Nickname und wähle die Sprache erneut.",
        "api_error": "⚠️ FACEIT ist gerade nicht erreichbar. Bitte versuche es später erneut.",
        "title": "FACEIT-Verifizierung für {nick}",
        "level": "Level",
        "kd": "K/D",
        "description": (
            "Um das Match zu starten, musst du dein FACEIT-Konto bestätigen.\n\n"
            "Um die Verifizierung fortzusetzen, nutze die Schaltfläche unten"
        ),
        "button": "Zur FACEIT-Verifizierung",
    },
    "tr": {
        "modal_title": "FACEIT doğrulaması",
        "nick_label": "FACEIT kullanıcı adınız",
        "nick_placeholder": "örn. s1mple",
        "not_found": "❌ **{nick}** FACEIT profili bulunamadı. Kullanıcı adını kontrol edip dili tekrar seçin.",
        "api_error": "⚠️ FACEIT'e şu anda ulaşılamıyor. Lütfen daha sonra tekrar deneyin.",
        "title": "{nick} için FACEIT doğrulaması",
        "level": "Seviye",
        "kd": "K/D",
        "description": (
            "Maça başlamak için FACEIT hesabınızı doğrulamanız gerekir.\n\n"
            "Doğrulamaya devam etmek için aşağıdaki düğmeyi kullanın"
        ),
        "button": "FACEIT doğrulamasına git",
    },
}


# Эмодзи уровней "1lvl".."10lvl": {1: "<:1lvl:123>", ...}; заполняется при старте бота.
LEVEL_EMOJIS: Dict[int, str] = {}


async def load_level_emojis(client: discord.Client) -> None:
    """Ищет эмодзи вида '<N>lvl' среди эмодзи серверов и эмодзи самого приложения."""
    found = {}
    candidates = list(client.emojis)
    try:
        candidates += await client.fetch_application_emojis()
    except discord.HTTPException as e:
        print(f"Не удалось получить эмодзи приложения: {e}")
    for emoji in candidates:
        name = emoji.name.lower()
        if name.endswith("lvl") and name[:-3].isdigit():
            found[int(name[:-3])] = str(emoji)
    LEVEL_EMOJIS.clear()
    LEVEL_EMOJIS.update(found)
    missing = [n for n in range(1, 11) if n not in found]
    print(f"Эмодзи уровней найдено: {len(found)}/10" + (f", нет: {missing}" if missing else ""))


class FaceitError(Exception):
    """FACEIT API недоступен или вернул ошибку."""


async def fetch_player(nickname: str) -> Optional[dict]:
    """Возвращает данные игрока или None, если такого профиля нет."""
    if not FACEIT_API_KEY:
        raise FaceitError("FACEIT_API_KEY is not set")

    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    timeout = aiohttp.ClientTimeout(total=10)
    base = "https://open.faceit.com/data/v4"

    try:
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            async with session.get(f"{base}/players", params={"nickname": nickname}) as resp:
                if resp.status == 404:
                    return None
                if resp.status != 200:
                    raise FaceitError(f"players lookup returned {resp.status}")
                player = await resp.json()

            game = next((g for g in GAMES if g in player.get("games", {})), None)
            info = player["games"][game] if game else {}
            kd = None
            if game:
                url = f"{base}/players/{player['player_id']}/stats/{game}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        kd = (await resp.json()).get("lifetime", {}).get("Average K/D Ratio")
    except aiohttp.ClientError as e:
        raise FaceitError(str(e)) from e

    return {
        "nickname": player["nickname"],
        "avatar": player.get("avatar") or None,
        "url": player.get("faceit_url", "").replace("{lang}", "en") or None,
        "level": info.get("skill_level"),
        "elo": info.get("faceit_elo"),
        "kd": kd,
    }


def logo_file() -> discord.File:
    return discord.File(os.path.join(ASSETS, "logo.png"), filename="logo.png")


def banner_file() -> discord.File:
    return discord.File(os.path.join(ASSETS, "banner.webp"), filename="banner.webp")


def header() -> ui.Section:
    """Заголовок с логотипом справа."""
    return ui.Section(
        "# FACEIT Status BOT",
        "-# FACEIT Verification System",
        accessory=ui.Thumbnail("attachment://logo.png"),
    )


def result_message(lang: str, player: dict) -> tuple[discord.Embed, ui.View]:
    t = TEXTS[lang]
    embed = discord.Embed(
        title=f"⚠️ {t['title'].format(nick=player['nickname'])}",
        description=f"\n{t['description']}",
        color=FACEIT_ORANGE,
    )
    level = player["level"]
    level_text = LEVEL_EMOJIS.get(level) or str(level or "—")  # нет эмодзи — показываем число
    embed.add_field(name=t["level"], value=level_text, inline=True)
    embed.add_field(name="ELO", value=str(player["elo"] or "—"), inline=True)
    embed.add_field(name=t["kd"], value=str(player["kd"] or "—"), inline=True)
    if player["avatar"]:
        embed.set_thumbnail(url=player["avatar"])
    embed.set_image(url="attachment://banner.webp")
    embed.set_footer(text="FACEIT Verification System", icon_url="attachment://logo.png")

    view = ui.View(timeout=None)
    link = VERIFY_URL or player["url"]
    if link:
        view.add_item(ui.Button(style=discord.ButtonStyle.link, label=t["button"], url=link, emoji="🔗"))
    return embed, view


class NicknameModal(ui.Modal):
    def __init__(self, lang: str):
        t = TEXTS[lang]
        super().__init__(title=t["modal_title"])
        self.lang = lang
        self.nickname = ui.TextInput(
            label=t["nick_label"],
            placeholder=t["nick_placeholder"],
            min_length=2,
            max_length=32,
        )
        self.add_item(self.nickname)

    async def on_submit(self, interaction: discord.Interaction):
        t = TEXTS[self.lang]
        nick = self.nickname.value.strip()
        # Запрос к API может занять больше 3 секунд — сначала подтверждаем получение.
        await interaction.response.defer()

        try:
            player = await fetch_player(nick)
        except FaceitError as e:
            print(f"FACEIT error for {nick!r}: {e}")
            await interaction.followup.send(t["api_error"])
            return

        if player is None:
            await interaction.followup.send(t["not_found"].format(nick=discord.utils.escape_markdown(nick)))
            return

        embed, view = result_message(self.lang, player)
        await interaction.followup.send(embed=embed, view=view, files=[logo_file(), banner_file()])


class LanguageRow(ui.ActionRow):
    @ui.select(
        custom_id="faceit:language",
        placeholder="Select language...",
        options=[
            discord.SelectOption(label=v["label"], value=k, emoji=v["emoji"])
            for k, v in LANGUAGES.items()
        ],
    )
    async def pick(self, interaction: discord.Interaction, select: ui.Select):
        await interaction.response.send_modal(NicknameModal(select.values[0]))


class LanguageView(ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)  # постоянное меню, работает и после перезапуска бота
        self.add_item(
            ui.Container(
                header(),
                ui.Separator(),
                ui.TextDisplay("### 🌐 Please select your language"),
                LanguageRow(),
                accent_colour=FACEIT_ORANGE,
            )
        )


class VerifBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_view(LanguageView())
        
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user} ({self.user.id})")
        await load_level_emojis(self)
        if not FACEIT_API_KEY:
            print("WARNING: FACEIT_API_KEY не задан — проверка никнеймов работать не будет.")


bot = VerifBot()


@bot.tree.command(name="verif", description="Отправить пользователю FACEIT-верификацию в личные сообщения")
@app_commands.describe(member="Кому отправить верификацию")
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def verif(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        await interaction.response.send_message("Нельзя отправить верификацию боту.", ephemeral=True)
        return

    try:
        await member.send(view=LanguageView(), file=logo_file())
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Не удалось написать {member.mention}: у него закрыты личные сообщения.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(f"Верификация отправлена {member.mention} в личку ✅", ephemeral=True)


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Не задан DISCORD_TOKEN. Скопируйте .env.example в .env и вставьте токен.")
    bot.run(TOKEN)

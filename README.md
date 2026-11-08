# NEXPLAIN AI Assistant

The Discord learning assistant for the NEXPLAIN community.

**Understand. Build. Innovate.**

This first version uses Discord slash commands and an OpenAI-compatible chat-completions API. It does not read ordinary channel messages, and it does not require Discord's privileged Message Content intent.

## Commands in this version

- `/ask` — ask an AI, machine learning, deep learning, LLM, or AI engineering question.
- `/explain` — get a beginner-friendly explanation of a concept.
- `/debug` — get help understanding code and errors.
- `/quiz` — generate a five-question quiz on a topic.

Commands have per-user cooldowns. The bot avoids automatically pinging users or roles in generated responses.

## Requirements

- Python 3.10 or newer
- A Discord application with a bot user
- An API key and model from an OpenAI-compatible AI provider

## Run locally

1. Clone this repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`.
5. Fill in the real `DISCORD_BOT_TOKEN`, `AI_API_KEY`, `AI_BASE_URL`, and `AI_MODEL`.
6. Start the bot:

   ```bash
   python bot.py
   ```

The bot logs in and synchronizes its global slash commands. Discord can take a little time to display newly registered global commands.

## Discord setup

In the Discord Developer Portal:

1. Open the NEXPLAIN AI Assistant application.
2. Under **Bot**, keep Presence Intent, Server Members Intent, and Message Content Intent disabled.
3. Under **OAuth2 → URL Generator**, select the `bot` and `applications.commands` scopes.
4. Grant only the permissions the bot needs to reply in channels, including Send Messages and Embed Links if desired.

The bot uses application commands. It does not need the privileged Message Content intent.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `DISCORD_BOT_TOKEN` | Secret token for the Discord bot user |
| `AI_API_KEY` | Secret key for the AI provider |
| `AI_BASE_URL` | Optional OpenAI-compatible API base URL |
| `AI_MODEL` | Model identifier supported by the provider |
| `LOG_LEVEL` | Logging level, defaults to INFO |

Never commit real tokens or API keys. If a secret is exposed, revoke or rotate it immediately.

## Deployment

This repository includes a `Procfile` with a worker command. Deploy it as a persistent background worker on a hosting provider that supports long-running Python processes. Add the environment variables through the provider's secret/environment settings; do not upload the local `.env` file.

A Discord bot must remain running to respond to interactions. A short-lived web request or a sleeping web service is not sufficient.

## Current scope and next steps

This is the first working foundation, not the finished NEXPLAIN knowledge assistant. It currently answers from the configured model's general knowledge. It is not yet connected to NEXPLAIN video transcripts, curated resources, project repositories, or a retrieval-augmented knowledge base.

Planned improvements:
- NEXPLAIN-specific knowledge retrieval (RAG)
- Learning paths and guided study plans
- Weekly challenges and submission feedback
- Better observability, tests, and abuse protection
- Optional channel-specific behaviour and moderator controls

import os

from openai import AsyncOpenAI


class AIConfigurationError(Exception):
    """Raised when required AI provider settings are missing."""


class AIRequestError(Exception):
    """Raised when the configured AI provider cannot return a response."""


SYSTEM_PROMPTS = {
    "ask": """You are the NEXPLAIN AI Learning Assistant.
NEXPLAIN's promise is: Understand. Build. Innovate.
Help community members learn artificial intelligence, machine learning, deep learning,
generative AI, LLMs, AI engineering, agents, and applied AI.
Be accurate, welcoming, practical, and clear. Adapt to the learner's level.
Explain uncertainty honestly. Do not invent sources, package behaviour, or results.
When useful, give a small practical example. Encourage responsible AI development.""",
    "explain": """You are the NEXPLAIN AI Learning Assistant and an excellent technical teacher.
Explain the requested concept in plain language first, then build up the technical detail.
Use a small example or analogy where it genuinely helps. Define unfamiliar terms.
For code topics, show a concise example and explain what it demonstrates.
Do not assume the learner already knows advanced mathematics or jargon.
Be accurate, structured, encouraging, and honest about uncertainty.""",
    "debug": """You are the NEXPLAIN AI Learning Assistant helping a developer debug code.
First identify what the error most likely means. Then explain the likely cause,
give a concrete fix, and show corrected code only where enough context is available.
If important information is missing, state exactly what is needed instead of guessing.
Never claim code was executed or tested unless it actually was.
Remind users to remove API keys, passwords, tokens, and personal data before sharing code.""",
    "quiz": """You are the NEXPLAIN AI Learning Assistant.
Create a short learning quiz about the topic requested.
Give 5 questions, progressing from beginner to intermediate unless the user specifies a level.
Use multiple-choice questions with four options each. Do not reveal the answers immediately.
Ask the learner to reply with their choices, then offer to mark and explain them.
Keep the questions technically correct and focused on understanding, not trivia.""",
}


class AIClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("AI_API_KEY")
        self.base_url = os.getenv("AI_BASE_URL") or None
        self.model = os.getenv("AI_MODEL")

    async def respond(self, task: str, user_text: str) -> str:
        if not self.api_key or not self.model:
            raise AIConfigurationError("AI_API_KEY and AI_MODEL are required.")

        prompt = SYSTEM_PROMPTS.get(task, SYSTEM_PROMPTS["ask"])
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=45.0,
            max_retries=1,
        )

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_text},
                ],
                temperature=0.4,
                max_tokens=900,
            )
            content = response.choices[0].message.content
            if not content:
                raise AIRequestError("The provider returned an empty response.")
            return content
        except AIConfigurationError:
            raise
        except Exception as exc:
            raise AIRequestError("AI provider request failed.") from exc
        finally:
            await client.close()

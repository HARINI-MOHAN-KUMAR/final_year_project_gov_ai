"""
Pluggable LLM provider layer for GovGuide AI.
Supports: Gemini API, OpenAI, Anthropic Claude, and Mock (no API key needed).
Provider is selected via LLM_PROVIDER environment variable.
"""

import logging
from typing import List, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are GovGuide Bot, an AI assistant specializing in Indian government welfare schemes.
Your role is to help citizens understand government schemes, check their eligibility, and guide them through the application process.

RULES:
1. Always respond based on the provided context. If the answer is not in the context, say "I don't have enough information about that."
2. Never make up scheme details, deadlines, or benefit amounts.
3. Explain eligibility in simple, plain language.
4. Always include a disclaimer that this is advisory only and users should verify on official portals.
5. If the user asks in Tamil or Hindi, respond in that language.
6. Ask follow-up questions if you need more profile information to assess eligibility.
7. Be empathetic and helpful – many users may not be familiar with government processes.

DISCLAIMER (always include at the end): ⚠️ This is an advisory service only, not an official government portal. Please verify all information on official government websites before applying.
"""


# ── Mock Provider ────────────────────────────────────────────────────────────

class MockLLMProvider:
    """Fallback mock LLM that works without any API key by extracting answers from scheme context."""

    async def chat(self, messages: List[Dict], context: str = "") -> str:
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        query_lower = last_user_msg.lower()
        extracted_info = ""

        if context:
            # Format the scheme knowledge from context cleanly
            blocks = context.strip().split("\n\n")
            if blocks:
                primary = blocks[0]
                extracted_info = f"📌 **Key Information from Scheme Records:**\n\n{primary}\n\n"

        return (
            f"Namaste! 🙏 Here is the information regarding your query:\n\n"
            f"{extracted_info}"
            f"💡 **Advisory Summary:**\n"
            f"Eligibility, income ceilings, and benefits depend on your specific household demographic profile (caste category, state of residence, and land holding).\n\n"
            f"You can verify your eligibility directly on our **'Check Eligibility'** tab or on the official government portal.\n\n"
            f"⚠️ *Disclaimer: This is an AI advisory service for information purposes only. Always verify rules on official government portals (pmayg.nic.in, myscheme.gov.in) before applying.*"
        )


# ── Gemini Provider ──────────────────────────────────────────────────────────

class GeminiProvider:
    def __init__(self):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini provider initialized")
        except Exception as e:
            logger.error(f"Gemini init failed: {e}")
            self._model = None

    async def chat(self, messages: List[Dict], context: str = "") -> str:
        if self._model is None:
            return MockLLMProvider().chat.__func__(MockLLMProvider(), messages, context)

        try:
            import asyncio
            # Build prompt with RAG context
            user_msg = messages[-1]["content"] if messages else ""
            prompt = f"{SYSTEM_PROMPT}\n\nContext from knowledge base:\n{context}\n\nUser: {user_msg}"
            response = await asyncio.to_thread(self._model.generate_content, prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return f"I encountered an error processing your request. Please try again. (Error: {str(e)[:100]})"


# ── OpenAI Provider ──────────────────────────────────────────────────────────

class OpenAIProvider:
    def __init__(self):
        try:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self._model = settings.OPENAI_MODEL
            logger.info("OpenAI provider initialized")
        except Exception as e:
            logger.error(f"OpenAI init failed: {e}")
            self._client = None

    async def chat(self, messages: List[Dict], context: str = "") -> str:
        if self._client is None:
            return await MockLLMProvider().chat(messages, context)

        try:
            system_with_ctx = SYSTEM_PROMPT
            if context:
                system_with_ctx += f"\n\nRelevant scheme information:\n{context}"

            api_messages = [{"role": "system", "content": system_with_ctx}] + messages
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=api_messages,
                max_tokens=800,
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"I encountered an error. Please try again. (Error: {str(e)[:100]})"


# ── Anthropic Provider ───────────────────────────────────────────────────────

class AnthropicProvider:
    def __init__(self):
        try:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self._model = settings.ANTHROPIC_MODEL
            logger.info("Anthropic provider initialized")
        except Exception as e:
            logger.error(f"Anthropic init failed: {e}")
            self._client = None

    async def chat(self, messages: List[Dict], context: str = "") -> str:
        if self._client is None:
            return await MockLLMProvider().chat(messages, context)

        try:
            system_with_ctx = SYSTEM_PROMPT
            if context:
                system_with_ctx += f"\n\nRelevant scheme information:\n{context}"

            response = await self._client.messages.create(
                model=self._model,
                max_tokens=800,
                system=system_with_ctx,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"I encountered an error. Please try again. (Error: {str(e)[:100]})"


# ── Provider Factory ─────────────────────────────────────────────────────────

_llm_provider = None


def get_llm_provider():
    """Return the configured LLM provider singleton."""
    global _llm_provider
    if _llm_provider is not None:
        return _llm_provider

    provider = settings.LLM_PROVIDER.lower()

    if provider == "gemini" and settings.GEMINI_API_KEY:
        _llm_provider = GeminiProvider()
    elif provider == "openai" and settings.OPENAI_API_KEY:
        _llm_provider = OpenAIProvider()
    elif provider == "anthropic" and settings.ANTHROPIC_API_KEY:
        _llm_provider = AnthropicProvider()
    else:
        logger.info("No LLM API key configured – using mock provider.")
        _llm_provider = MockLLMProvider()

    return _llm_provider

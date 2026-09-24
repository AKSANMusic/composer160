"""LLM Intent Interpreter for COMPOSER-160.

Translates vague user intent, lyrics, or mood requests into structured
160-parameter vectors using the Google GenAI SDK.
"""

import asyncio
import json
import os
import re
from typing import Any

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None  # type: ignore[assignment]
    types = None  # type: ignore[assignment]

from composer160.core.parameters import PARAMETER_REGISTRY
from composer160.core.types import Tier
from composer160.core.vector import ParameterVector
from composer160.presets.aksan import aksan_preset


class Interpreter:
    """Interprets natural language musical requests into ParameterVector overrides."""

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        preset: ParameterVector | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the Gemini client and base preset.

        Args:
            model_name: Gemini model identifier (default: "gemini-2.5-flash").
            preset: Base vector to clone and apply overrides onto (default: AKSAN preset).
            api_key: Optional explicit Gemini API key; falls back to GEMINI_API_KEY env var.
        """
        self.model_name = model_name
        self.base_preset = preset or aksan_preset()
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        self._client: Any = None
        if genai is not None:
            try:
                if self.api_key:
                    self._client = genai.Client(api_key=self.api_key)
                else:
                    self._client = genai.Client()
            except Exception:
                self._client = None

    def _build_system_prompt(self) -> str:
        """Create a prompt summarizing T1 and key T2 parameters from PARAMETER_REGISTRY."""
        param_lines: list[str] = []
        for pid in sorted(PARAMETER_REGISTRY):
            defn = PARAMETER_REGISTRY[pid]
            if defn.tier in (Tier.T1, Tier.T2):
                val_str = f"options: {list(defn.values)}" if defn.values else f"type: {defn.param_type.name}"
                if defn.unit:
                    val_str += f" ({defn.unit})"
                param_lines.append(f"- ID {pid}: {defn.name} [{defn.tier.name}] ({val_str})")

        catalog_text = "\n".join(param_lines)

        return (
            "You are COMPOSER-160, an advanced musical direction engine for the AKSAN project.\n"
            "Your aesthetic identity is 'Melankolik Asi' (Melancholic Rebellious) — a fusion of alternative music, "
            "Anatolian melodies, and Persian poetry depth, cinematic and dark (#050508 minimalist brutalism).\n\n"
            "Your task is to analyze the user's musical request and determine parameter overrides for the track.\n"
            "Below is the controlled parameter catalog (T1 and T2 parameters):\n\n"
            f"{catalog_text}\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Output ONLY a valid JSON object mapping string parameter IDs to their selected values (e.g., {\"1\": \"A\", \"8\": 86, \"100\": \"Melancholy\"}).\n"
            "2. Do NOT wrap in markdown explanation or conversational filler.\n"
            "3. Only include parameters that you want to set or override based on the user's intent. All other parameters will retain their canonical AKSAN preset defaults.\n"
            "4. Ensure musical consistency (e.g. Atonal tonality forbids modes/cadences; Modal tonality requires #3 Mode; BPM must be an integer).\n"
        )

    async def get_overrides(self, user_request: str) -> dict[int, Any]:
        """Call the LLM and return raw parameter ID overrides."""
        if not self._client:
            raise RuntimeError(
                "Gemini client is not initialized. Ensure google-genai is installed and "
                "GEMINI_API_KEY environment variable is set."
            )

        system_instruction = self._build_system_prompt()

        response = await self._client.aio.models.generate_content(
            model=self.model_name,
            contents=user_request,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        response_text = response.text or ""
        parsed = self._parse_json_response(response_text)
        overrides: dict[int, Any] = {}
        for key, value in parsed.items():
            try:
                pid = int(key)
                if 1 <= pid <= 160:
                    overrides[pid] = value
            except (ValueError, TypeError):
                continue
        return overrides

    async def interpret(
        self,
        user_request: str,
        base_vector: ParameterVector | None = None,
    ) -> ParameterVector:
        """Call the LLM with system prompt and user request to produce an overridden ParameterVector."""
        overrides = await self.get_overrides(user_request)

        base = base_vector or self.base_preset
        vec = base.copy()
        for pid, value in overrides.items():
            vec.set(pid, value, assumed=False)

        return vec

    def interpret_sync(
        self,
        user_request: str,
        base_vector: ParameterVector | None = None,
    ) -> ParameterVector:
        """Synchronously execute the LLM interpretation."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(
                    asyncio.run, self.interpret(user_request, base_vector)
                ).result()
        else:
            return asyncio.run(self.interpret(user_request, base_vector))

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """Robustly extract and parse JSON from LLM output."""
        cleaned = text.strip()
        # Strip markdown fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        # Find enclosing JSON object
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict):
                return data
            return {}
        except json.JSONDecodeError:
            return {}

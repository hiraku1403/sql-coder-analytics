from typing import Any

from google import genai

from app.ai.llm import LLMProvider
from app.ai.prompts import (
    build_analysis_prompt,
    build_chart_planner_prompt,
    build_sql_correction_prompt,
    build_sql_prompt,
)
from app.core.config import GEMINI_API_KEY


class GeminiProvider(LLMProvider):
    """
    LLM provider implementation using Google Gemini.
    """

    def __init__(self) -> None:

        if not GEMINI_API_KEY:

            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    # =========================================================
    # SQL GENERATION
    # =========================================================

    def generate_sql(
        self,
        question: str,
        schema: str,
    ) -> str:
        """
        Generates SQL from a natural language question.

        The provider receives the question and schema separately
        and builds the final prompt internally.
        """

        prompt = build_sql_prompt(
            question=question,
            schema=schema,
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text.strip()

    # =========================================================
    # SQL CORRECTION
    # =========================================================

    def correct_sql(
        self,
        question: str,
        schema: str,
        sql: str,
        error: str,
    ) -> str:
        """
        Corrects SQL based on a database execution error.
        """

        prompt = build_sql_correction_prompt(
            question=question,
            schema=schema,
            sql=sql,
            error=error,
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty correction."
            )

        return response.text.strip()

    # =========================================================
    # CHART PLANNING
    # =========================================================

    def generate_chart_plan(
        self,
        question: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> str:
        """
        Generates a structured visualization plan
        based on the query result.
        """

        prompt = build_chart_planner_prompt(
            question=question,
            columns=columns,
            rows=rows,
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty chart plan."
            )

        return response.text.strip()

    # =========================================================
    # BUSINESS ANALYSIS
    # =========================================================

    def generate_analysis(
        self,
        question: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> str:
        """
        Generates analytical insights from query results.
        """

        prompt = build_analysis_prompt(
            question=question,
            columns=columns,
            rows=rows,
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        if not response.text:

            raise RuntimeError(
                "Gemini returned an empty analysis."
            )

        return response.text.strip()
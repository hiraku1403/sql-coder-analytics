from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """
    Interface for LLM providers.
    """

    @abstractmethod
    def generate_sql(
        self,
        question: str,
        schema: str,
    ) -> str:
        """
        Generate SQL from a natural language question.
        """
        raise NotImplementedError

    @abstractmethod
    def correct_sql(
        self,
        question: str,
        schema: str,
        sql: str,
        error: str,
    ) -> str:
        """
        Correct a SQL query based on a database error.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_chart_plan(
        self,
        question: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> str:
        """
        Generate a visualization plan.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_analysis(
        self,
        question: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> str:
        """
        Generate analytical insights from query results.
        """
        raise NotImplementedError
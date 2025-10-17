"""HTTP client for communicating with the backend API."""

from __future__ import annotations

import logging
from typing import Any

import httpx


class BackendClient:
    """Client for interacting with the backend REST API."""

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        """
        Initialize the backend client.

        Args:
            base_url: Base URL of the backend API (e.g., http://localhost:8000)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def create_message(self, user_id: int, role: str, content: str) -> dict[str, Any]:
        """
        Create a new message in the conversation history.

        Args:
            user_id: Telegram user ID
            role: Message role (user, assistant, system)
            content: Message content

        Returns:
            Created message data with ID

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/v1/messages"
        payload = {"user_id": user_id, "role": role, "content": content}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
            except httpx.HTTPError as e:
                logging.error(f"Failed to create message: {e}")
                raise

    async def get_conversation_history(self, user_id: int) -> list[dict[str, Any]]:
        """
        Get conversation history for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            List of messages (role, content, created_at, length)

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/v1/conversations/{user_id}/messages"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                result: list[dict[str, Any]] = response.json()
                return result
            except httpx.HTTPError as e:
                logging.error(f"Failed to get conversation history: {e}")
                raise

    async def clear_conversation_history(self, user_id: int) -> None:
        """
        Clear (soft delete) all messages for a user.

        Args:
            user_id: Telegram user ID

        Raises:
            httpx.HTTPError: If the API request fails
        """
        url = f"{self.base_url}/api/v1/conversations/{user_id}/messages"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.delete(url)
                response.raise_for_status()
            except httpx.HTTPError as e:
                logging.error(f"Failed to clear conversation history: {e}")
                raise

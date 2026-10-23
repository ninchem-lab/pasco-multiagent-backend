"""Custom football tools for the tools agent."""

import os
import re

import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from tavily import TavilyClient


HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like "
        "Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9",
}


def _find_marca_player_url(player_name: str) -> str | None:
    """Search for a player's Marca profile URL using Tavily.

    Args:
        player_name: Full name of the player.

    Returns:
        The Marca player profile URL or None if not found.
    """
    client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))
    results = client.search(
        query=f"{player_name} ficha jugador site:marca.com/resultados/futbol/jugadores",
        max_results=3,
    )
    for result in results.get("results", []):
        url = result.get("url", "")
        if "marca.com/resultados/futbol/jugadores" in url and "/ficha/" in url:
            return url
    return None


COMPETITIONS: set[str] = {
    "LALIGA EA Sports",
    "Champions League",
    "Copa del Rey",
    "Supercopa de España",
    "Premier League",
    "Bundesliga",
    "Serie A",
    "Ligue 1",
}


def _parse_basic_info(lines: list[str]) -> dict[str, str]:
    """Extract basic player info from page text lines.

    Args:
        lines: Cleaned text lines from the Marca player page.

    Returns:
        A dictionary with name, position, age, physical, and birth keys.
    """
    data: dict[str, str] = {}
    for i, line in enumerate(lines):
        if re.match(r"\d+ años", line) and i >= 2:
            data["name"] = lines[i - 2]
            data["position"] = lines[i - 1]
            data["age"] = line
        if "cm," in line and "kg" in line:
            data["physical"] = line
        if "Nacimiento:" in line and i + 1 < len(lines):
            data["birth"] = lines[i + 1]
    return data


def _parse_competition_stats(lines: list[str], i: int) -> str | None:
    """Extract stats for a single competition block starting at index i.

    Args:
        lines: Cleaned text lines from the Marca player page.
        i: Index of the competition name line.

    Returns:
        A formatted stats string or None if parsing fails.
    """

    try:
        if lines[i + 1] != "Partidos":
            return None
        # Partidos / N / De / N / Titular / N / De / N / Goles / N / Tarjetas / N
        games, starts, goals, cards = (
            lines[i + 2],
            lines[i + 6],
            lines[i + 10],
            lines[i + 14],
        )
        return (
            f"{lines[i]}: {games} games, {starts} starts, {goals} goals, {cards} cards"
        )
    except IndexError:
        return None


def _scrape_marca_player(url: str) -> dict[str, str]:
    """Scrape player profile data from a Marca player page.

    Args:
        url: The Marca player profile URL.

    Returns:
        A dictionary with player info and stats.
    """

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    lines = [
        line.strip()
        for line in soup.get_text(separator="\n").splitlines()
        if line.strip()
    ]

    data = _parse_basic_info(lines)

    competitions = [
        stats
        for i, line in enumerate(lines)
        if line in COMPETITIONS
        if (stats := _parse_competition_stats(lines, i)) is not None
    ]
    data["stats"] = " | ".join(competitions) if competitions else "No stats found"
    return data


@tool
def get_player_profile(player_name: str) -> str:
    """Get a football player's profile and current season stats from Marca.

    Fetches real-time data including position, age, club, physical attributes, and
    per-competition statistics for the current season.

    Args:
        player_name: Full name of the player (e.g., "Jude Bellingham").

    Returns:
        A formatted string with the player's profile and stats.
    """

    url = _find_marca_player_url(player_name)
    if not url:
        return f"Could not find a Marca profile for {player_name}."

    try:
        data = _scrape_marca_player(url)
    except requests.RequestException as e:
        return f"Error fetching data for {player_name}: {e}"

    parts = [f"Player: {data.get('name', player_name)}"]
    if "position" in data:
        parts.append(f"Position: {data['position']}")
    if "age" in data:
        parts.append(f"Age: {data['age']}")
    if "physical" in data:
        parts.append(f"Physical: {data['physical']}")
    if "birth" in data:
        parts.append(f"Born: {data['birth']}")
    if "stats" in data:
        parts.append(f"Current season stats — {data['stats']}")

    return "\n".join(parts)

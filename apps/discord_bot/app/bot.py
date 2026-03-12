import asyncio
import os

import discord
import httpx
from discord import app_commands

API_URL = os.getenv("DISCORD_BOT_API_URL", "http://api-service:8000")
API_KEY = os.getenv("DISCORD_BOT_API_KEY", "external-dev-key")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "")


class TradechainBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        guild_obj = discord.Object(id=int(GUILD_ID)) if GUILD_ID else None

        @self.tree.command(name="task_create", description="Create a task in tradechain", guild=guild_obj)
        @app_commands.describe(title="Task title", chain_type="Workflow chain type")
        async def task_create(interaction: discord.Interaction, title: str, chain_type: str = "major_task") -> None:
            await interaction.response.defer(thinking=True)
            payload = {
                "title": title,
                "type": chain_type,
                "source": "discord",
                "chain_type": chain_type,
                "priority": 50,
                "goal_json": {},
                "context_json": {},
                "created_by": str(interaction.user),
            }
            result = await call_api("POST", "/v1/tasks", payload)
            if "error" in result:
                await interaction.followup.send(f"create task failed: {result['error']}")
                return
            await interaction.followup.send(f"task created: `{result.get('id')}`")

        @self.tree.command(name="proposal_latest", description="Get latest proposal", guild=guild_obj)
        async def proposal_latest(interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)
            result = await call_api("GET", "/v1/proposals/latest")
            if "error" in result:
                await interaction.followup.send(f"query failed: {result['error']}")
                return
            await interaction.followup.send(
                "\n".join(
                    [
                        f"proposal: `{result.get('id')}`",
                        f"theme: {result.get('theme')}",
                        f"status: {result.get('status')}",
                        f"requires_human: {result.get('requires_human')}",
                    ]
                )
            )

        @self.tree.command(name="system_health", description="Check API service health", guild=guild_obj)
        async def system_health(interaction: discord.Interaction) -> None:
            await interaction.response.defer(thinking=True)
            result = await call_api("GET", "/healthz", auth=False)
            if "error" in result:
                await interaction.followup.send(f"health check failed: {result['error']}")
                return
            await interaction.followup.send(f"api-service health: `{result.get('status', 'unknown')}`")

        if guild_obj:
            await self.tree.sync(guild=guild_obj)
        else:
            await self.tree.sync()


async def call_api(method: str, path: str, payload: dict | None = None, auth: bool = True) -> dict:
    headers = {}
    if auth:
        headers["X-API-Key"] = API_KEY

    url = f"{API_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            if method == "POST":
                response = await client.post(url, json=payload or {}, headers=headers)
            else:
                response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def main() -> None:
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is empty. Set it in .env before running discord-bot profile.")

    client = TradechainBot()
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()

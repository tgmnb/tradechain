import asyncio
import os
import socket

import aiohttp
import discord
import httpx
from discord import app_commands

try:
    from aiohttp_socks import ProxyConnector
except ImportError:  # pragma: no cover - optional until dependency is installed in runtime image
    ProxyConnector = None

API_URL = os.getenv("DISCORD_BOT_API_URL", "http://api-service:8000")
API_KEY = os.getenv("DISCORD_BOT_API_KEY", "external-dev-key")
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
GUILD_ID = os.getenv("DISCORD_GUILD_ID", "")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")
DISCORD_PROXY_URL = os.getenv("DISCORD_PROXY_URL", "")
DISCORD_PROXY_USERNAME = os.getenv("DISCORD_PROXY_USERNAME", "")
DISCORD_PROXY_PASSWORD = os.getenv("DISCORD_PROXY_PASSWORD", "")
DISCORD_PROXY_FORCE_IPV4 = os.getenv("DISCORD_PROXY_FORCE_IPV4", "true").lower() in {"1", "true", "yes", "on"}
DISCORD_PROXY_DNS_CACHE_SECONDS = int(os.getenv("DISCORD_PROXY_DNS_CACHE_SECONDS", "300"))


def channel_object() -> discord.Object | None:
    return discord.Object(id=int(GUILD_ID)) if GUILD_ID else None


def allowed_channel_id() -> int | None:
    return int(CHANNEL_ID) if CHANNEL_ID else None


def as_embed(title: str, description: str, *, color: int) -> discord.Embed:
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="tradechain")
    return embed


def build_discord_connector(loop: asyncio.AbstractEventLoop) -> aiohttp.BaseConnector | None:
    family = socket.AF_INET if DISCORD_PROXY_FORCE_IPV4 else socket.AF_UNSPEC

    if not DISCORD_PROXY_URL:
        return aiohttp.TCPConnector(
            loop=loop,
            family=family,
            ttl_dns_cache=DISCORD_PROXY_DNS_CACHE_SECONDS,
            enable_cleanup_closed=True,
            limit=0,
        )

    if DISCORD_PROXY_URL.startswith(("socks5://", "socks4://")):
        if ProxyConnector is None:
            raise RuntimeError("aiohttp-socks is required for SOCKS proxy support")
        return ProxyConnector.from_url(DISCORD_PROXY_URL, loop=loop)

    if DISCORD_PROXY_URL.startswith(("http://", "https://")):
        return aiohttp.TCPConnector(
            loop=loop,
            family=family,
            ttl_dns_cache=DISCORD_PROXY_DNS_CACHE_SECONDS,
            enable_cleanup_closed=True,
            limit=0,
        )

    return None


class TradechainBot(discord.Client):
    def __init__(self, *, connector: aiohttp.BaseConnector | None) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True
        intents.message_content = True

        proxy_auth = None
        proxy_url = None
        if DISCORD_PROXY_USERNAME and DISCORD_PROXY_PASSWORD:
            proxy_auth = aiohttp.BasicAuth(DISCORD_PROXY_USERNAME, DISCORD_PROXY_PASSWORD)
        if DISCORD_PROXY_URL.startswith(("http://", "https://")):
            proxy_url = DISCORD_PROXY_URL

        super().__init__(
            intents=intents,
            connector=connector,
            proxy=proxy_url,
            proxy_auth=proxy_auth,
        )
        self.tree = app_commands.CommandTree(self)
        self.startup_notified = False

    async def setup_hook(self) -> None:
        guild_obj = channel_object()

        @self.tree.command(name="task_create", description="Create a task in tradechain", guild=guild_obj)
        @app_commands.describe(title="Task title", chain_type="Workflow chain type", goal="Optional goal or note")
        async def task_create(
            interaction: discord.Interaction,
            title: str,
            chain_type: str = "major_task",
            goal: str = "",
        ) -> None:
            if not await self.ensure_allowed_channel(interaction):
                return
            await interaction.response.defer(thinking=True)
            payload = {
                "title": title,
                "type": chain_type,
                "source": "discord",
                "chain_type": chain_type,
                "priority": 50,
                "goal_json": {"text": goal} if goal else {},
                "context_json": {"channel_id": str(interaction.channel_id)},
                "created_by": str(interaction.user),
            }
            result = await call_api("POST", "/v1/tasks", payload)
            if "error" in result:
                await interaction.followup.send(embed=as_embed("Task Create Failed", result["error"], color=0xC0392B))
                return
            await interaction.followup.send(
                embed=as_embed(
                    "Task Created",
                    "\n".join(
                        [
                            f"ID: `{result.get('id')}`",
                            f"Type: `{result.get('type')}`",
                            f"Chain: `{result.get('chain_type')}`",
                            f"Status: `{result.get('status')}`",
                        ]
                    ),
                    color=0x1F8B4C,
                )
            )

        @self.tree.command(name="proposal_latest", description="Get latest proposal", guild=guild_obj)
        async def proposal_latest(interaction: discord.Interaction) -> None:
            if not await self.ensure_allowed_channel(interaction):
                return
            await interaction.response.defer(thinking=True)
            result = await call_api("GET", "/v1/proposals/latest")
            if "error" in result:
                await interaction.followup.send(embed=as_embed("Proposal Query Failed", result["error"], color=0xC0392B))
                return
            await interaction.followup.send(
                embed=as_embed(
                    "Latest Proposal",
                    "\n".join(
                        [
                            f"ID: `{result.get('id')}`",
                            f"Theme: {result.get('theme')}",
                            f"Status: `{result.get('status')}`",
                            f"Action: `{result.get('recommended_action')}`",
                            f"Requires Human: `{result.get('requires_human')}`",
                        ]
                    ),
                    color=0x2E86C1,
                )
            )

        @self.tree.command(name="intel_update", description="Run the intel-update workflow", guild=guild_obj)
        async def intel_update(interaction: discord.Interaction) -> None:
            if not await self.ensure_allowed_channel(interaction):
                return
            await interaction.response.defer(thinking=True)
            headers = {
                "X-Request-ID": f"discord-{interaction.id}",
                "X-Chain-Type": "intel_update",
                "X-Actor": str(interaction.user),
            }
            result = await call_api("POST", "/v1/workflows/intel-update/run", {}, extra_headers=headers)
            if "error" in result:
                await interaction.followup.send(embed=as_embed("Workflow Failed", result["error"], color=0xC0392B))
                return
            await interaction.followup.send(
                embed=as_embed(
                    "Intel Update Complete",
                    "\n".join(
                        [
                            f"Status: `{result.get('status')}`",
                            f"Ingested: `{result.get('ingested')}`",
                            f"Created Events: `{result.get('created_events')}`",
                            f"Created Proposals: `{result.get('created_proposals')}`",
                        ]
                    ),
                    color=0x8E44AD,
                )
            )

        @self.tree.command(name="system_health", description="Check API service health", guild=guild_obj)
        async def system_health(interaction: discord.Interaction) -> None:
            if not await self.ensure_allowed_channel(interaction):
                return
            await interaction.response.defer(thinking=True)
            result = await call_api("GET", "/healthz", auth=False)
            if "error" in result:
                await interaction.followup.send(embed=as_embed("Health Check Failed", result["error"], color=0xC0392B))
                return
            await interaction.followup.send(
                embed=as_embed(
                    "System Health",
                    f"api-service health: `{result.get('status', 'unknown')}`",
                    color=0x1F8B4C,
                )
            )

        @self.tree.command(name="ask", description="Send a natural language request to the tradechain agent", guild=guild_obj)
        @app_commands.describe(message="What you want the agent to do")
        async def ask(interaction: discord.Interaction, message: str) -> None:
            if not await self.ensure_allowed_channel(interaction):
                return
            await interaction.response.defer(thinking=True)
            result = await self.run_agent_message(
                text=message,
                user_name=str(interaction.user),
                user_id=str(interaction.user.id),
                channel_id=str(interaction.channel_id),
                guild_id=str(interaction.guild_id) if interaction.guild_id else None,
            )
            await self.send_agent_result(interaction.followup.send, result)

        if guild_obj:
            await self.tree.sync(guild=guild_obj)
        else:
            await self.tree.sync()

    async def on_ready(self) -> None:
        if self.startup_notified:
            return
        self.startup_notified = True
        channel_id = allowed_channel_id()
        if channel_id:
            try:
                channel = self.get_channel(channel_id) or await self.fetch_channel(channel_id)
                if hasattr(channel, "send"):
                    await channel.send(
                        embed=as_embed(
                            "Tradechain Bot Online",
                            "Commands are live for this channel.\n"
                            "Use `/system_health`, `/proposal_latest`, `/intel_update`, `/task_create`, `/ask`.\n"
                            "Plain messages in this channel also route into the top-level agent.",
                            color=0x1F8B4C,
                        )
                    )
            except Exception:
                pass

    async def ensure_allowed_channel(self, interaction: discord.Interaction) -> bool:
        channel_id = allowed_channel_id()
        if not channel_id or interaction.channel_id == channel_id:
            return True

        await interaction.response.send_message(
            embed=as_embed(
                "Wrong Channel",
                f"Use this bot in <#{channel_id}>.",
                color=0xF39C12,
            ),
            ephemeral=True,
        )
        return False

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        channel_id = allowed_channel_id()
        if channel_id and message.channel.id != channel_id:
            return
        if message.content.startswith("/"):
            return

        async with message.channel.typing():
            result = await self.run_agent_message(
                text=message.content,
                user_name=str(message.author),
                user_id=str(message.author.id),
                channel_id=str(message.channel.id),
                guild_id=str(message.guild.id) if message.guild else None,
            )
        await message.reply(embed=embed_from_agent_result(result), mention_author=False)

    async def run_agent_message(
        self,
        *,
        text: str,
        user_name: str,
        user_id: str,
        channel_id: str,
        guild_id: str | None,
    ) -> dict:
        return await call_api(
            "POST",
            "/v1/agent/discord-message",
            {
                "text": text,
                "user_name": user_name,
                "user_id": user_id,
                "channel_id": channel_id,
                "guild_id": guild_id,
            },
        )

    async def send_agent_result(self, sender, result: dict) -> None:
        if "error" in result:
            await sender(embed=as_embed("Agent Request Failed", result["error"], color=0xC0392B))
            return
        await sender(embed=embed_from_agent_result(result))


def embed_from_agent_result(result: dict) -> discord.Embed:
    route = result.get("route", "agent")
    summary = result.get("summary", "No summary returned.")
    color = 0x1F8B4C if route in {"health", "proposal_latest", "intel_update"} else 0x2E86C1
    embed = as_embed(f"Agent Route: {route}", summary, color=color)

    proposal = result.get("proposal") or {}
    if proposal:
        embed.add_field(name="Theme", value=str(proposal.get("theme", "-"))[:1024], inline=False)
        embed.add_field(name="Action", value=str(proposal.get("recommended_action", "-")), inline=True)
        embed.add_field(name="Requires Human", value=str(proposal.get("requires_human", False)), inline=True)

    task = result.get("task") or {}
    if task:
        embed.add_field(name="Task ID", value=str(task.get("id", "-")), inline=False)

    workflow = result.get("workflow") or {}
    if workflow:
        embed.add_field(
            name="Workflow",
            value="\n".join(
                [
                    f"status: `{workflow.get('status')}`",
                    f"ingested: `{workflow.get('ingested')}`",
                    f"proposals: `{workflow.get('created_proposals')}`",
                ]
            ),
            inline=False,
        )
    elif route in {"help", "chat"}:
        embed.add_field(
            name="Dispatch",
            value="Handled directly by the politburo agent. No downstream workflow was activated.",
            inline=False,
        )
    return embed


async def call_api(
    method: str,
    path: str,
    payload: dict | None = None,
    auth: bool = True,
    extra_headers: dict[str, str] | None = None,
) -> dict:
    headers = {}
    if auth:
        headers["X-API-Key"] = API_KEY
    if extra_headers:
        headers.update(extra_headers)

    url = f"{API_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=90.0, trust_env=False) as client:
            if method == "POST":
                response = await client.post(url, json=payload or {}, headers=headers)
            else:
                response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.content else {}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def main() -> None:
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_BOT_TOKEN is empty. Set it in .env before running discord-bot profile.")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    connector = build_discord_connector(loop)
    client = TradechainBot(connector=connector)
    try:
        loop.run_until_complete(client.start(DISCORD_TOKEN))
    finally:
        loop.run_until_complete(client.close())
        loop.close()


if __name__ == "__main__":
    main()

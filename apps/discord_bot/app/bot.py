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
    if not DISCORD_PROXY_URL:
        return aiohttp.TCPConnector(
            loop=loop,
            family=socket.AF_INET if DISCORD_PROXY_FORCE_IPV4 else socket.AF_UNSPEC,
            ttl_dns_cache=DISCORD_PROXY_DNS_CACHE_SECONDS,
            enable_cleanup_closed=True,
            limit=0,
        )

    if DISCORD_PROXY_URL.startswith(("socks5://", "socks4://")):
        if ProxyConnector is None:
            raise RuntimeError("aiohttp-socks is required for SOCKS proxy support")
        return ProxyConnector.from_url(DISCORD_PROXY_URL, loop=loop)

    if DISCORD_PROXY_URL.startswith(("http://", "https://")):
        # Clash-style HTTP proxies are more stable here when the Discord client
        # avoids IPv6/happy-eyeballs churn and keeps DNS/socket reuse predictable.
        return aiohttp.TCPConnector(
            loop=loop,
            family=socket.AF_INET if DISCORD_PROXY_FORCE_IPV4 else socket.AF_UNSPEC,
            ttl_dns_cache=DISCORD_PROXY_DNS_CACHE_SECONDS,
            enable_cleanup_closed=True,
            limit=0,
        )

    return None


class TradechainBot(discord.Client):
    def __init__(self, *, connector: aiohttp.BaseConnector | None) -> None:
        intents = discord.Intents.default()
        intents.guilds = True
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
                            "Commands are live for this channel.\nUse `/system_health`, `/proposal_latest`, `/intel_update`, `/task_create`.",
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

        content = (message.content or "").strip()
        if not content:
            return

        mentioned = self.user in message.mentions if self.user else False
        normalized = content.lower()
        if mentioned and self.user:
            normalized = normalized.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "").strip()

        if not mentioned and not normalized.startswith(("tc ", "tradechain ")):
            return

        if normalized.startswith("tc "):
            normalized = normalized[3:].strip()
        elif normalized.startswith("tradechain "):
            normalized = normalized[len("tradechain "):].strip()

        if normalized in {"", "help", "?", "菜单", "命令"}:
            await message.reply(
                "可用消息命令：`help`、`health`、`proposal latest`、`intel update`。\n"
                "也可以继续用斜杠命令：`/system_health`、`/proposal_latest`、`/intel_update`、`/task_create`。",
                mention_author=False,
            )
            return

        if normalized in {"health", "healthz", "status"}:
            result = await call_api("GET", "/healthz", auth=False)
            if "error" in result:
                await message.reply(f"health check failed: {result['error']}", mention_author=False)
                return
            await message.reply(f"api-service health: `{result.get('status', 'unknown')}`", mention_author=False)
            return

        if normalized in {"proposal latest", "latest proposal", "latest"}:
            result = await call_api("GET", "/v1/proposals/latest")
            if "error" in result:
                await message.reply(f"proposal query failed: {result['error']}", mention_author=False)
                return
            await message.reply(
                "\n".join(
                    [
                        f"ID: `{result.get('id')}`",
                        f"Theme: {result.get('theme')}",
                        f"Status: `{result.get('status')}`",
                        f"Action: `{result.get('recommended_action')}`",
                        f"Requires Human: `{result.get('requires_human')}`",
                    ]
                ),
                mention_author=False,
            )
            return

        if normalized in {"intel update", "intel", "run intel"}:
            headers = {
                "X-Request-ID": f"discord-message-{message.id}",
                "X-Chain-Type": "intel_update",
                "X-Actor": str(message.author),
            }
            result = await call_api("POST", "/v1/workflows/intel-update/run", {}, extra_headers=headers)
            if "error" in result:
                await message.reply(f"workflow failed: {result['error']}", mention_author=False)
                return
            await message.reply(
                "\n".join(
                    [
                        f"Status: `{result.get('status')}`",
                        f"Ingested: `{result.get('ingested')}`",
                        f"Created Events: `{result.get('created_events')}`",
                        f"Created Proposals: `{result.get('created_proposals')}`",
                    ]
                ),
                mention_author=False,
            )
            return

        await message.reply(
            "没识别这条消息。试试 `@bot help`、`@bot health`、`@bot proposal latest`、`@bot intel update`。",
            mention_author=False,
        )


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
        async with httpx.AsyncClient(timeout=20.0, trust_env=False) as client:
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

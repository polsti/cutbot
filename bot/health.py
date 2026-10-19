"""Tiny HTTP server that runs next to the bot.

Render's free Web Service sleeps after ~15 min without incoming HTTP
traffic, and a polling bot never receives any. An external pinger
(UptimeRobot) hits /health every few minutes so the service stays awake.
"""

from aiohttp import web


async def health(_: web.Request) -> web.Response:
    return web.Response(text="ok")


async def start_health_server(port: int) -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, host="0.0.0.0", port=port).start()
    return runner

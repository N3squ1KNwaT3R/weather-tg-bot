import asyncio
import os
import sys
from datetime import datetime
from websocket_client import LogsWebSocketClient
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from collections import deque

console = Console()


class AdminDashboard:
    def __init__(self):
        self.logs = deque(maxlen=50)
        self.stats = {
            "total_events": 0,
            "info": 0,
            "warning": 0,
            "error": 0,
            "unique_users": set()
        }
        self.running = True
        self.connected = False

    def add_log(self, log_entry: dict):
        """Добавляет новый лог и обновляет статистику"""
        self.logs.append(log_entry)
        self.stats["total_events"] += 1

        level = log_entry.get("level", "info")
        self.stats[level] = self.stats.get(level, 0) + 1

        user_id = log_entry.get("user_id")
        if user_id:
            self.stats["unique_users"].add(user_id)

    def generate_layout(self) -> Layout:
        """Генерирует layout для отображения"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="stats", size=8),
            Layout(name="logs"),
            Layout(name="footer", size=3)
        )

        # Header с индикатором подключения
        status = "🟢 Connected" if self.connected else "🔴 Connecting..."
        header_text = Text(
            f"🌤️  Weather Bot Admin Dashboard [{status}]",
            style="bold cyan",
            justify="center"
        )
        layout["header"].update(Panel(header_text))

        # Stats
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column(style="bold yellow")
        stats_table.add_column(style="bold green")

        stats_table.add_row("📊 Total Events:", str(self.stats["total_events"]))
        stats_table.add_row("👥 Unique Users:", str(len(self.stats["unique_users"])))
        stats_table.add_row("ℹ️  Info:", str(self.stats["info"]))
        stats_table.add_row("⚠️  Warning:", str(self.stats.get("warning", 0)))
        stats_table.add_row("❌ Error:", str(self.stats.get("error", 0)))

        layout["stats"].update(Panel(stats_table, title="Statistics", border_style="blue"))

        # Logs
        if not self.connected and len(self.logs) == 0:
            waiting_text = Text(
                "Waiting for backend connection...\n"
                "Make sure backend service is running",
                style="dim yellow",
                justify="center"
            )
            layout["logs"].update(Panel(waiting_text, title="Recent Activity", border_style="yellow"))
        else:
            logs_table = Table(show_header=True, header_style="bold magenta", show_lines=False)
            logs_table.add_column("Time", style="dim", width=19)
            logs_table.add_column("User", style="cyan", width=20)
            logs_table.add_column("Action", style="green", width=25)
            logs_table.add_column("Details", style="yellow", no_wrap=False)

            if len(self.logs) == 0:
                logs_table.add_row("", "", "No activity yet", "")
            else:
                for log in reversed(list(self.logs)):
                    timestamp = log.get("timestamp", "")
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime("%H:%M:%S")
                    except:
                        time_str = timestamp[:8] if timestamp else ""

                    username = log.get("username", "Unknown")
                    user_id = log.get("user_id", "")
                    user_str = f"{username} ({user_id})"

                    action = log.get("action", "")
                    details = log.get("details", {})
                    details_str = ", ".join([f"{k}: {v}" for k, v in details.items()]) if details else ""

                    level = log.get("level", "info")
                    style = "white"
                    if level == "error":
                        style = "bold red"
                    elif level == "warning":
                        style = "bold yellow"

                    logs_table.add_row(
                        time_str,
                        user_str,
                        action,
                        details_str[:40],
                        style=style
                    )

            layout["logs"].update(Panel(logs_table, title="Recent Activity", border_style="green"))

        # Footer
        footer_text = Text("Press Ctrl+C to exit", style="dim italic", justify="center")
        layout["footer"].update(Panel(footer_text))

        return layout


async def main():
    websocket_url = os.getenv("WEBSOCKET_URL", "ws://backend:8000/ws/logs")

    dashboard = AdminDashboard()
    ws_client = LogsWebSocketClient(websocket_url)

    async def on_log_received(log_entry: dict):
        """Callback при получении нового лога"""
        dashboard.add_log(log_entry)

    ws_client.on_log_received = on_log_received

    try:
        # Запускаем WebSocket клиент в фоне
        ws_task = asyncio.create_task(ws_client.connect())

        # Даем время на подключение
        await asyncio.sleep(1)

        # Запускаем Live display
        with Live(
                dashboard.generate_layout(),
                refresh_per_second=1,
                console=console,
                screen=True,
                transient=False
        ) as live:
            while dashboard.running:
                dashboard.connected = ws_client.connected
                live.update(dashboard.generate_layout())
                await asyncio.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        await ws_client.close()
        try:
            ws_task.cancel()
            await ws_task
        except:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import typer
from dotenv import load_dotenv, set_key
from rich.console import Console
from rich.table import Table

from .client import EightSleepClient, EightSleepError

PKG_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = PKG_DIR / ".env"
if not ENV_PATH.exists():
    ENV_PATH = PKG_DIR.parent / ".env"
load_dotenv(ENV_PATH)

console = Console()
app = typer.Typer(
    help="Eight Sleep CLI",
    pretty_exceptions_show_locals=False,
)
sleep_app = typer.Typer(help="Sleep data and trends")
temp_app = typer.Typer(help="Temperature control")
alarm_app = typer.Typer(help="Alarm management")
base_app = typer.Typer(help="Adjustable base control")
speaker_app = typer.Typer(help="Speaker/audio control")
app.add_typer(sleep_app, name="sleep")
app.add_typer(temp_app, name="temp")
app.add_typer(alarm_app, name="alarm")
app.add_typer(base_app, name="base")
app.add_typer(speaker_app, name="speaker")


def _client() -> EightSleepClient:
    token = os.environ.get("EIGHT_SLEEP_TOKEN", "")
    user_id = os.environ.get("EIGHT_SLEEP_USER_ID", "")
    if not token or not user_id:
        raise typer.BadParameter("Not authenticated. Run: eight auth")
    return EightSleepClient(token, user_id)


def _device_id() -> str:
    did = os.environ.get("EIGHT_SLEEP_DEVICE_ID", "")
    if not did:
        client = _client()
        me = client.me()
        did = me["user"]["devices"][0]
        set_key(str(ENV_PATH), "EIGHT_SLEEP_DEVICE_ID", did)
        os.environ["EIGHT_SLEEP_DEVICE_ID"] = did
    return did


def _print_json(data: dict) -> None:
    console.print_json(json.dumps(data, default=str))


def _date_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%d")


def _fmt_duration(seconds: int | None) -> str:
    if seconds is None:
        return "-"
    h, m = divmod(seconds // 60, 60)
    return f"{h}h {m}m"


# ── Auth ──

@app.command()
def auth(
    email: str = typer.Option(None, "--email", "-e", help="Eight Sleep email"),
    password: str = typer.Option(None, "--password", "-p", help="Eight Sleep password"),
    token: str = typer.Option(None, "--token", "-t", help="Set bearer token directly"),
    user_id: str = typer.Option(None, "--user-id", "-u", help="Set user ID directly (use with --token)"),
) -> None:
    """Authenticate with Eight Sleep. Saves token to .env."""
    if token:
        if not user_id:
            raise typer.BadParameter("--user-id is required when using --token")
        set_key(str(ENV_PATH), "EIGHT_SLEEP_TOKEN", token)
        set_key(str(ENV_PATH), "EIGHT_SLEEP_USER_ID", user_id)
        console.print(f"[green]Token saved.[/green] User ID: {user_id}")
        return

    if not email:
        email = typer.prompt("Email")
    if not password:
        password = typer.prompt("Password", hide_input=True)

    result = EightSleepClient.authenticate(email, password)
    set_key(str(ENV_PATH), "EIGHT_SLEEP_TOKEN", result["access_token"])
    set_key(str(ENV_PATH), "EIGHT_SLEEP_USER_ID", result["user_id"])
    console.print(f"[green]Authenticated.[/green] User ID: {result['user_id']}")
    console.print(f"Token expires in {result['expires_in'] // 3600}h")


@app.command()
def whoami(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show authenticated user and device info."""
    client = _client()
    me = client.me()
    user = me["user"]

    if as_json:
        _print_json(me)
        return

    console.print(f"User ID:  {user['userId']}")
    console.print(f"Email:    {user.get('email', '-')}")
    console.print(f"Name:     {user.get('firstName', '')} {user.get('lastName', '')}")
    console.print(f"Devices:  {', '.join(user.get('devices', []))}")
    side = user.get("currentDevice", {}).get("side", "-")
    console.print(f"Side:     {side}")


@app.command()
def device(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show device details."""
    client = _client()
    did = _device_id()
    data = client.device(did)
    result = data["result"]

    if as_json:
        _print_json(data)
        return

    console.print(f"Device ID:    {did}")
    console.print(f"Features:     {', '.join(result.get('features', []))}")
    console.print(f"Has Water:    {result.get('hasWater')}")
    console.print(f"Needs Prime:  {result.get('needsPriming')}")
    console.print(f"Is Priming:   {result.get('priming')}")
    console.print(f"Left User:    {result.get('leftUserId', '-')}")
    console.print(f"Right User:   {result.get('rightUserId', '-')}")


# ── Sleep Data ──

@sleep_app.command("last")
def sleep_last(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show last night's sleep data."""
    client = _client()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    data = client.trends(_date_str(yesterday), _date_str(today))

    if as_json:
        _print_json(data)
        return

    days = data.get("days", [])
    if not days:
        console.print("[yellow]No sleep data for last night.[/yellow]")
        return

    _print_sleep_day(days[-1])


@sleep_app.command("today")
def sleep_today(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show today's sleep data (current/most recent session)."""
    client = _client()
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    data = client.trends(_date_str(today), _date_str(tomorrow))

    if as_json:
        _print_json(data)
        return

    days = data.get("days", [])
    if not days:
        console.print("[yellow]No sleep data for today.[/yellow]")
        return

    _print_sleep_day(days[-1])


@sleep_app.command("range")
def sleep_range(
    start: str = typer.Argument(..., help="Start date (YYYY-MM-DD)"),
    end: str = typer.Argument(None, help="End date (YYYY-MM-DD), defaults to today"),
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show sleep data for a date range."""
    client = _client()
    if end is None:
        end = _date_str(datetime.now())
    data = client.trends(start, end)

    if as_json:
        _print_json(data)
        return

    days = data.get("days", [])
    if not days:
        console.print("[yellow]No sleep data for this range.[/yellow]")
        return

    table = Table(title=f"Sleep: {start} to {end}")
    table.add_column("Date", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Duration", justify="right")
    table.add_column("Deep", justify="right", style="green")
    table.add_column("REM", justify="right", style="blue")
    table.add_column("Light", justify="right")
    table.add_column("Awake", justify="right", style="red")
    table.add_column("HR", justify="right")
    table.add_column("HRV", justify="right")
    table.add_column("Breath", justify="right")
    table.add_column("T&T", justify="right")

    for day in days:
        score = day.get("score")
        sleep_dur = day.get("sleepDuration")
        deep = day.get("deepDuration")
        rem = day.get("remDuration")
        light = day.get("lightDuration")
        presence = day.get("presenceDuration")
        awake = (presence - sleep_dur) if presence and sleep_dur else None
        qs = day.get("sleepQualityScore", {})
        hr = qs.get("heartRate", {}).get("average")
        hrv = qs.get("hrv", {}).get("current")
        breath = qs.get("respiratoryRate", {}).get("average")
        tnt = day.get("tnt")

        table.add_row(
            day.get("day", "-"),
            str(score) if score else "-",
            _fmt_duration(sleep_dur),
            _fmt_duration(deep),
            _fmt_duration(rem),
            _fmt_duration(light),
            _fmt_duration(awake),
            f"{hr:.0f}" if hr else "-",
            f"{hrv:.0f}" if hrv else "-",
            f"{breath:.1f}" if breath else "-",
            str(tnt) if tnt is not None else "-",
        )

    console.print(table)


@sleep_app.command("week")
def sleep_week(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show sleep data for the last 7 days."""
    end = _date_str(datetime.now())
    start = _date_str(datetime.now() - timedelta(days=7))
    sleep_range(start, end, as_json)


def _print_sleep_day(day: dict) -> None:
    score = day.get("score")
    sleep_dur = day.get("sleepDuration")
    deep = day.get("deepDuration")
    rem = day.get("remDuration")
    light = day.get("lightDuration")
    presence = day.get("presenceDuration")
    awake = (presence - sleep_dur) if presence and sleep_dur else None
    qs = day.get("sleepQualityScore", {})
    hr = qs.get("heartRate", {}).get("average")
    hrv = qs.get("hrv", {}).get("current")
    breath = qs.get("respiratoryRate", {}).get("average")
    tnt = day.get("tnt")
    bed_temp = qs.get("tempBedC", {}).get("average")
    room_temp = qs.get("tempRoomC", {}).get("average")

    score_color = "green" if score and score >= 80 else "yellow" if score and score >= 60 else "red"

    console.print(f"\n[bold]{day.get('day', 'Unknown')}[/bold]")
    console.print(f"  Sleep Score:    [{score_color}]{score or '-'}[/{score_color}]")
    console.print(f"  In Bed:         {day.get('presenceStart', '-')} to {day.get('presenceEnd', '-')}")
    console.print()
    console.print(f"  Total Sleep:    {_fmt_duration(sleep_dur)}")
    console.print(f"  [green]Deep:           {_fmt_duration(deep)}[/green]")
    console.print(f"  [blue]REM:            {_fmt_duration(rem)}[/blue]")
    console.print(f"  Light:          {_fmt_duration(light)}")
    console.print(f"  [red]Awake:          {_fmt_duration(awake)}[/red]")
    console.print()
    console.print(f"  Heart Rate:     {f'{hr:.0f} bpm' if hr else '-'}")
    console.print(f"  HRV:            {f'{hrv:.0f} ms' if hrv else '-'}")
    console.print(f"  Breath Rate:    {f'{breath:.1f}/min' if breath else '-'}")
    console.print(f"  Toss & Turns:   {tnt if tnt is not None else '-'}")
    console.print(f"  Bed Temp:       {f'{bed_temp:.1f}C' if bed_temp else '-'}")
    console.print(f"  Room Temp:      {f'{room_temp:.1f}C' if room_temp else '-'}")

    # Sleep stage breakdown as percentages
    if sleep_dur and sleep_dur > 0:
        console.print()
        deep_pct = (deep / sleep_dur * 100) if deep else 0
        rem_pct = (rem / sleep_dur * 100) if rem else 0
        light_pct = (light / sleep_dur * 100) if light else 0
        deep_color = "green" if deep_pct >= 15 else "yellow" if deep_pct >= 10 else "red"
        console.print(f"  Stage %:  [{deep_color}]Deep {deep_pct:.0f}%[/{deep_color}]  |  [blue]REM {rem_pct:.0f}%[/blue]  |  Light {light_pct:.0f}%")


# ── Temperature ──

@temp_app.command("status")
def temp_status(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show current temperature settings."""
    client = _client()
    data = client.temperature()

    if as_json:
        _print_json(data)
        return

    state = data.get("currentState", {}).get("type", "-")
    level = data.get("currentLevel", "-")
    device_level = data.get("currentDeviceLevel", "-")
    smart = data.get("smart", {})

    state_color = "green" if state == "smart" else "red" if state == "off" else "yellow"
    console.print(f"  State:          [{state_color}]{state}[/{state_color}]")
    console.print(f"  Current Level:  {level}")
    console.print(f"  Device Level:   {device_level}")
    if smart:
        console.print(f"  Autopilot:")
        console.print(f"    Bed Time:     {smart.get('bedTimeLevel', '-')}")
        console.print(f"    Initial:      {smart.get('initialSleepLevel', '-')}")
        console.print(f"    Final:        {smart.get('finalSleepLevel', '-')}")


@temp_app.command("set")
def temp_set(
    level: int = typer.Argument(..., help="Temperature level (-100 to 100)"),
    duration: int = typer.Option(0, "--duration", "-d", help="Duration in minutes (0 = indefinite)"),
) -> None:
    """Set bed temperature level."""
    client = _client()
    client.turn_on()
    if duration > 0:
        client.set_temperature_timed(level, duration * 60)
        console.print(f"[green]Temperature set to {level} for {duration}m[/green]")
    else:
        client.set_temperature(level)
        console.print(f"[green]Temperature set to {level}[/green]")


@temp_app.command("on")
def temp_on() -> None:
    """Turn on autopilot (smart mode)."""
    client = _client()
    client.turn_on()
    console.print("[green]Autopilot on[/green]")


@temp_app.command("off")
def temp_off() -> None:
    """Turn off temperature control."""
    client = _client()
    client.turn_off()
    console.print("[red]Temperature off[/red]")


@temp_app.command("stage")
def temp_stage(
    stage: str = typer.Argument(..., help="Sleep stage: bedtime, initial, final"),
    level: int = typer.Argument(..., help="Temperature level (-100 to 100)"),
) -> None:
    """Set autopilot temperature for a sleep stage."""
    stage_map = {
        "bedtime": "bedTimeLevel",
        "initial": "initialSleepLevel",
        "final": "finalSleepLevel",
    }
    key = stage_map.get(stage.lower())
    if not key:
        raise typer.BadParameter(f"Invalid stage. Use: {', '.join(stage_map.keys())}")
    client = _client()
    client.set_smart_stage_temp(key, level)
    console.print(f"[green]{stage} temperature set to {level}[/green]")


# ── Alarms ──

@alarm_app.command("list")
def alarm_list(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """List all alarms."""
    client = _client()
    data = client.alarms()

    if as_json:
        _print_json(data)
        return

    alarms = data.get("alarms", [])
    if not alarms:
        console.print("[yellow]No alarms configured.[/yellow]")
        return

    table = Table(title="Alarms")
    table.add_column("ID", style="dim", max_width=12)
    table.add_column("Time", style="cyan")
    table.add_column("Enabled")
    table.add_column("Repeat")
    table.add_column("Vibration")
    table.add_column("Thermal")
    table.add_column("Next", style="dim")

    for a in alarms:
        enabled = "[green]yes[/green]" if a.get("enabled") else "[red]no[/red]"
        repeat = a.get("repeat", {})
        if repeat.get("enabled"):
            days = [d[:3] for d, v in repeat.get("weekDays", {}).items() if v]
            repeat_str = ", ".join(days) if days else "daily"
        else:
            repeat_str = "once"
        vib = a.get("vibration", {})
        vib_str = f"L{vib.get('powerLevel', '-')}" if vib.get("enabled") else "off"
        therm = a.get("thermal", {})
        therm_str = str(therm.get("level", "-")) if therm.get("enabled") else "off"

        table.add_row(
            a["id"][:12],
            a.get("time", "-"),
            enabled,
            repeat_str,
            vib_str,
            therm_str,
            a.get("nextTimestamp", "-")[:19] if a.get("nextTimestamp") else "-",
        )

    console.print(table)

    rec = data.get("recommendedAlarm", {})
    if rec.get("nextTimestamp"):
        console.print(f"\nRecommended alarm: {rec.get('time', '-')} (next: {rec['nextTimestamp'][:19]})")


@alarm_app.command("create")
def alarm_create(
    time: str = typer.Argument(..., help="Alarm time (HH:MM:SS)"),
    no_vibration: bool = typer.Option(False, "--no-vibration", help="Disable vibration"),
    no_thermal: bool = typer.Option(False, "--no-thermal", help="Disable thermal alarm"),
    thermal_level: int = typer.Option(0, "--thermal-level", help="Thermal level for alarm"),
) -> None:
    """Create a new alarm."""
    client = _client()
    client.create_alarm(time, vibration=not no_vibration, thermal=not no_thermal, thermal_level=thermal_level)
    console.print(f"[green]Alarm created at {time}[/green]")


@alarm_app.command("enable")
def alarm_enable(alarm_id: str = typer.Argument(..., help="Alarm ID")) -> None:
    """Enable an alarm."""
    client = _client()
    client.set_alarm_enabled(alarm_id, True)
    console.print(f"[green]Alarm {alarm_id[:12]} enabled[/green]")


@alarm_app.command("disable")
def alarm_disable(alarm_id: str = typer.Argument(..., help="Alarm ID")) -> None:
    """Disable an alarm."""
    client = _client()
    client.set_alarm_enabled(alarm_id, False)
    console.print(f"[red]Alarm {alarm_id[:12]} disabled[/red]")


@alarm_app.command("snooze")
def alarm_snooze(
    alarm_id: str = typer.Argument(..., help="Alarm ID"),
    minutes: int = typer.Option(9, "--minutes", "-m", help="Snooze minutes"),
) -> None:
    """Snooze an alarm."""
    client = _client()
    client.snooze_alarm(alarm_id, minutes)
    console.print(f"[yellow]Snoozed for {minutes}m[/yellow]")


@alarm_app.command("dismiss")
def alarm_dismiss(alarm_id: str = typer.Argument(..., help="Alarm ID")) -> None:
    """Dismiss an alarm."""
    client = _client()
    client.dismiss_alarm(alarm_id)
    console.print(f"Alarm dismissed")


# ── Base ──

@base_app.command("status")
def base_status(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show adjustable base status."""
    client = _client()
    data = client.base()
    if as_json:
        _print_json(data)
        return
    for side in ("left", "right"):
        s = data.get(side, {})
        if not s:
            continue
        console.print(f"\n[bold]{side.title()} Side[/bold]")
        console.print(f"  Torso:    {s.get('torso', {}).get('currentAngle', 0)}deg")
        console.print(f"  Leg:      {s.get('leg', {}).get('currentAngle', 0)}deg")
        preset = s.get("preset", {}).get("name")
        if preset:
            console.print(f"  Preset:   {preset}")
        console.print(f"  Snore:    {s.get('inSnoreMitigation', False)}")


@base_app.command("set")
def base_set(
    torso: int = typer.Option(0, "--torso", "-t", help="Torso angle"),
    leg: int = typer.Option(0, "--leg", "-l", help="Leg angle"),
) -> None:
    """Set base angles."""
    client = _client()
    did = _device_id()
    client.set_base_angle(did, leg=leg, torso=torso)
    console.print(f"[green]Base set: torso={torso}deg, leg={leg}deg[/green]")


@base_app.command("flat")
def base_flat() -> None:
    """Set base to flat position."""
    client = _client()
    did = _device_id()
    client.set_base_angle(did, leg=0, torso=0)
    console.print("[green]Base set to flat[/green]")


# ── Speaker ──

@speaker_app.command("status")
def speaker_status(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show speaker/player status."""
    client = _client()
    data = client.player_state()
    if as_json:
        _print_json(data)
    else:
        console.print_json(json.dumps(data, default=str))


@speaker_app.command("tracks")
def speaker_tracks(
    as_json: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """List available audio tracks."""
    client = _client()
    data = client.audio_tracks()

    if as_json:
        _print_json(data)
        return

    tracks = data.get("tracks", [])
    table = Table(title="Audio Tracks")
    table.add_column("ID", style="dim", max_width=20)
    table.add_column("Name", style="cyan")
    table.add_column("Category")

    for t in tracks:
        table.add_row(t.get("id", "-")[:20], t.get("name", "-"), t.get("category", "-"))

    console.print(table)


@speaker_app.command("play")
def speaker_play() -> None:
    """Resume playback."""
    _client().set_player_state("Playing")
    console.print("[green]Playing[/green]")


@speaker_app.command("pause")
def speaker_pause() -> None:
    """Pause playback."""
    _client().set_player_state("Paused")
    console.print("[yellow]Paused[/yellow]")


@speaker_app.command("volume")
def speaker_volume(level: int = typer.Argument(..., help="Volume 0-100")) -> None:
    """Set speaker volume."""
    _client().set_player_volume(max(0, min(100, level)))
    console.print(f"[green]Volume set to {level}[/green]")


@speaker_app.command("track")
def speaker_track(track_id: str = typer.Argument(..., help="Track ID")) -> None:
    """Play a specific track."""
    _client().set_player_track(track_id)
    console.print(f"[green]Playing track {track_id}[/green]")


# ── Away Mode ──

@app.command()
def away(
    action: str = typer.Argument(..., help="'start' or 'end'"),
) -> None:
    """Start or end away mode."""
    client = _client()
    client.set_away(action)
    console.print(f"[green]Away mode: {action}[/green]")


# ── Prime ──

@app.command()
def prime() -> None:
    """Start a pod priming cycle."""
    client = _client()
    did = _device_id()
    client.prime(did)
    console.print("[green]Priming started[/green]")


@app.callback()
def main() -> None:
    pass


if __name__ == "__main__":
    app()

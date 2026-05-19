from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import requests

AUTH_URL = "https://auth-api.8slp.net/v1/tokens"
CLIENT_API = "https://client-api.8slp.net/v1"
APP_API = "https://app-api.8slp.net"

KNOWN_CLIENT_ID = "0894c7f33bb94800a03f1f4df13a4f38"
KNOWN_CLIENT_SECRET = "f0954a3ed5763ba3d06834c73731a32f15f168f47d4f164751275def86db0c76"


class EightSleepError(Exception):
    pass


class EightSleepClient:
    def __init__(self, token: str, user_id: str) -> None:
        self.token = token
        self.user_id = user_id
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "EightSleepCLI/0.1.0",
        }

    @staticmethod
    def authenticate(email: str, password: str) -> dict[str, str]:
        resp = requests.post(
            AUTH_URL,
            json={
                "client_id": KNOWN_CLIENT_ID,
                "client_secret": KNOWN_CLIENT_SECRET,
                "grant_type": "password",
                "username": email,
                "password": password,
            },
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            raise EightSleepError(f"Auth failed ({resp.status_code}): {resp.text}")
        data = resp.json()
        return {
            "access_token": data["access_token"],
            "user_id": data["userId"],
            "expires_in": data["expires_in"],
        }

    def _get(self, url: str, params: dict | None = None) -> Any:
        resp = requests.get(url, headers=self._headers, params=params)
        if resp.status_code == 401:
            raise EightSleepError("Token expired. Run: eight auth")
        if resp.status_code >= 400:
            raise EightSleepError(f"GET {url} failed ({resp.status_code}): {resp.text}")
        return resp.json()

    def _put(self, url: str, data: dict | None = None) -> Any:
        resp = requests.put(url, headers=self._headers, json=data)
        if resp.status_code == 401:
            raise EightSleepError("Token expired. Run: eight auth")
        if resp.status_code >= 400:
            raise EightSleepError(f"PUT {url} failed ({resp.status_code}): {resp.text}")
        if resp.headers.get("content-length") == "0":
            return {}
        return resp.json()

    def _post(self, url: str, data: dict | None = None) -> Any:
        resp = requests.post(url, headers=self._headers, json=data)
        if resp.status_code == 401:
            raise EightSleepError("Token expired. Run: eight auth")
        if resp.status_code >= 400:
            raise EightSleepError(f"POST {url} failed ({resp.status_code}): {resp.text}")
        return resp.json()

    # ── User & Device ──

    def me(self) -> dict:
        return self._get(f"{CLIENT_API}/users/me")

    def device(self, device_id: str) -> dict:
        return self._get(f"{CLIENT_API}/devices/{device_id}")

    def household(self) -> dict:
        return self._get(f"{APP_API}/v1/household/users/{self.user_id}/summary")

    # ── Sleep Data ──

    def trends(self, from_date: str, to_date: str, tz: str = "America/Los_Angeles") -> dict:
        return self._get(
            f"{CLIENT_API}/users/{self.user_id}/trends",
            params={
                "tz": tz,
                "from": from_date,
                "to": to_date,
                "include-main": "false",
                "include-all-sessions": "true",
                "model-version": "v2",
            },
        )

    # ── Temperature ──

    def temperature(self) -> dict:
        return self._get(f"{APP_API}/v1/users/{self.user_id}/temperature")

    def set_temperature(self, level: int) -> dict:
        level = max(-100, min(100, level))
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/temperature",
            {"currentLevel": level},
        )

    def set_temperature_timed(self, level: int, duration_seconds: int) -> dict:
        level = max(-100, min(100, level))
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/temperature",
            {"timeBased": {"level": level, "durationSeconds": duration_seconds}},
        )

    def set_smart_stage_temp(self, stage: str, level: int) -> dict:
        valid = ("bedTimeLevel", "initialSleepLevel", "finalSleepLevel")
        if stage not in valid:
            raise EightSleepError(f"Invalid stage: {stage}. Must be one of {valid}")
        level = max(-100, min(100, level))
        data = self.temperature()
        smart = data.get("smart", {})
        smart[stage] = level
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/temperature",
            {"smart": smart},
        )

    def turn_on(self) -> dict:
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/temperature",
            {"currentState": {"type": "smart"}},
        )

    def turn_off(self) -> dict:
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/temperature",
            {"currentState": {"type": "off"}},
        )

    # ── Alarms ──

    def alarms(self) -> dict:
        return self._get(f"{APP_API}/v2/users/{self.user_id}/alarms")

    def set_alarm_enabled(self, alarm_id: str, enabled: bool) -> dict:
        alarms = self.alarms()
        alarm = next((a for a in alarms.get("alarms", []) if a["id"] == alarm_id), None)
        if not alarm:
            raise EightSleepError(f"Alarm {alarm_id} not found")
        data = dict(alarm)
        data["enabled"] = enabled
        for key in ("nextTimestamp", "startTimestamp", "endTimestamp", "dismissedUntil", "snoozedUntil"):
            data.pop(key, None)
        return self._put(f"{APP_API}/v1/users/{self.user_id}/alarms/{alarm_id}", data)

    def create_alarm(self, time: str, vibration: bool = True, thermal: bool = True, thermal_level: int = 0) -> dict:
        return self._post(
            f"{APP_API}/v1/users/{self.user_id}/alarms",
            {
                "time": time,
                "enabled": True,
                "vibration": {"enabled": vibration, "powerLevel": 50, "pattern": "RISE"},
                "thermal": {"enabled": thermal, "level": thermal_level},
            },
        )

    def snooze_alarm(self, alarm_id: str, minutes: int = 9) -> dict:
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/alarms/{alarm_id}/snooze",
            {"snoozeMinutes": minutes, "ignoreDeviceErrors": False},
        )

    def dismiss_alarm(self, alarm_id: str) -> dict:
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/alarms/{alarm_id}/dismiss",
            {"ignoreDeviceErrors": False},
        )

    # ── Base ──

    def base(self) -> dict:
        return self._get(f"{APP_API}/v1/users/{self.user_id}/base")

    def set_base_angle(self, device_id: str, leg: int = 0, torso: int = 0) -> dict:
        return self._post(
            f"{APP_API}/v1/users/{self.user_id}/base/angle?ignoreDeviceErrors=false",
            {
                "deviceId": device_id,
                "deviceOnline": True,
                "legAngle": leg,
                "torsoAngle": torso,
                "enableOfflineMode": False,
            },
        )

    # ── Away Mode ──

    def set_away(self, action: str) -> dict:
        if action not in ("start", "end"):
            raise EightSleepError(f"Invalid action: {action}. Must be 'start' or 'end'")
        now = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/away-mode",
            {"awayPeriod": {action: now}},
        )

    # ── Audio/Speaker ──

    def player_state(self) -> dict:
        return self._get(f"{APP_API}/v1/users/{self.user_id}/audio/player")

    def audio_tracks(self) -> dict:
        return self._get(f"{APP_API}/v1/users/{self.user_id}/audio/tracks")

    def set_player_state(self, state: str) -> dict:
        return self._put(f"{APP_API}/v1/users/{self.user_id}/audio/player/state", {"state": state})

    def set_player_volume(self, volume: int) -> dict:
        return self._put(f"{APP_API}/v1/users/{self.user_id}/audio/player/volume", {"volume": volume})

    def set_player_track(self, track_id: str) -> dict:
        return self._put(
            f"{APP_API}/v1/users/{self.user_id}/audio/player/currentTrack",
            {"id": track_id, "stopCriteria": "ManualStop"},
        )

    # ── Priming ──

    def prime(self, device_id: str) -> dict:
        return self._post(
            f"{APP_API}/v1/devices/{device_id}/priming/tasks",
            {"notifications": {"users": [self.user_id], "meta": "rePriming"}},
        )

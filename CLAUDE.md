# Eight Sleep CLI

CLI for the Eight Sleep Pod API. Wraps sleep data, temperature control, alarms, adjustable base, and speaker endpoints.

## Quick Reference

```bash
# Auth (token from Proxyman or email/password)
eight auth --token "eyJ..." --user-id "abc123"
eight auth --email you@email.com --password yourpass

# Sleep data
eight sleep last              # last night
eight sleep today             # current session
eight sleep week              # 7-day overview
eight sleep range 2024-01-01 2024-01-31 [--json]

# Temperature
eight temp status             # current state + autopilot levels
eight temp set -40            # manual level (-100 to 100)
eight temp set -50 -d 60      # timed (minutes)
eight temp on                 # enable autopilot
eight temp off                # disable
eight temp stage bedtime -20  # autopilot stage: bedtime, initial, final

# Alarms
eight alarm list
eight alarm create 07:00:00
eight alarm enable|disable ALARM_ID
eight alarm snooze ALARM_ID [-m 9]
eight alarm dismiss ALARM_ID

# Base
eight base status
eight base set --torso 20 --leg 10
eight base flat

# Speaker
eight speaker status|tracks|play|pause
eight speaker volume 50
eight speaker track TRACK_ID

# Other
eight whoami                  # user info + side
eight device                  # device details
eight away start|end
eight prime
```

## Architecture

- `client.py` - API client. Three base URLs: auth-api, client-api, app-api (all at 8slp.net). Handles token refresh on 401.
- `cli.py` - Typer CLI. Loads token from `.env`, organizes commands into subgroups (sleep, temp, alarm, base, speaker).

## API Endpoints

| Endpoint | Base | Description |
|----------|------|-------------|
| `POST /v1/tokens` | auth-api | OAuth2 password grant |
| `GET /v1/users/me` | client-api | User profile + device list |
| `GET /v1/devices/{id}` | client-api | Device info, sides, features |
| `GET /v1/users/{id}/trends` | client-api | Sleep data (main data endpoint) |
| `GET/PUT /v1/users/{id}/temperature` | app-api | Temperature state + control |
| `GET /v2/users/{id}/alarms` | app-api | List alarms |
| `POST /v1/users/{id}/alarms` | app-api | Create alarm |
| `PUT /v1/users/{id}/alarms/{id}` | app-api | Update alarm |
| `GET /v1/users/{id}/base` | app-api | Adjustable base |
| `GET /v1/users/{id}/audio/player` | app-api | Speaker state |

## Environment

Token + user ID stored in `.env` (local directory or parent). Auto-set by `eight auth`.

```
EIGHT_SLEEP_TOKEN=eyJ...
EIGHT_SLEEP_USER_ID=abc123
EIGHT_SLEEP_DEVICE_ID=def456   # auto-detected on first use
```

## Sleep Data Fields

The trends endpoint returns per-night data:
- `score` (0-100), `sleepDuration`, `presenceDuration` (seconds)
- `deepDuration`, `remDuration`, `lightDuration` (seconds)
- `presenceStart`, `presenceEnd` (UTC timestamps)
- `tnt` (toss & turns count)
- `sleepQualityScore.heartRate.average`, `.hrv.current`, `.respiratoryRate.average`
- `sleepQualityScore.tempBedC.average`, `.tempRoomC.average`
- `sessions[].stages[]` (sleep stage timeline)
- `sessions[].timeseries.heartRate` (time series `[[ts, val], ...]`)

## Temperature Scale

-100 to +100 (not -10 to +10). Three autopilot stages:
- `bedTimeLevel` - when you get in bed
- `initialSleepLevel` - deep sleep phase (first half)
- `finalSleepLevel` - REM phase (second half)

## Skills

Read `skills/` for research-backed protocols:
- `sleep-optimization.md` - deep sleep science, metric targets, bedtime timing research
- `temperature-protocol.md` - temperature settings for different goals with cited papers
- `blood-sleep-connections.md` - how sleep metrics relate to blood markers

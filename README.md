# Eight Sleep CLI

A command-line interface for the Eight Sleep Pod API. Query sleep data, control bed temperature, manage alarms, and more.

Built by reverse-engineering the Eight Sleep iOS app's API calls.

## Features

- **Sleep data**: last night, today, weekly trends, custom date ranges with deep/REM/light breakdown
- **Temperature control**: set levels, autopilot on/off, per-stage smart temperature
- **Alarms**: list, create, enable/disable, snooze, dismiss
- **Adjustable base**: angles, presets, flat
- **Speaker**: play/pause, volume, track selection
- **Away mode & priming**

## Install

```bash
pip install -e .
```

## Authentication

The Eight Sleep API doesn't have a public auth flow. You need to capture a bearer token from the iOS/Android app using a network proxy.

### Option A: Capture token via Proxyman (recommended)

1. **Install Proxyman** on your iPhone: [proxyman.io/ios](https://proxyman.io/ios)

2. **Set up HTTPS decryption**:
   - Open Proxyman on your iPhone
   - Follow the in-app setup to install the Proxyman CA certificate
   - Go to Settings > General > About > Certificate Trust Settings and enable trust for Proxyman CA

3. **Capture the token**:
   - Start recording in Proxyman
   - Open the Eight Sleep app and navigate around (pull down to refresh sleep data)
   - In Proxyman, look for requests to `client-api.8slp.net`
   - Tap any request and look at the request headers
   - Copy the `Authorization: Bearer eyJ...` value (everything after "Bearer ")

4. **Get your user ID**:
   - In the same captured request, look at the URL path
   - It will contain `/users/{userId}/` - that's your user ID
   - Or decode the JWT token - the `sub` field is your auth user ID

5. **Save credentials**:
   ```bash
   eight auth --token "eyJ..." --user-id "your-user-id"
   ```

### Option B: Capture via Proxyman on Mac

1. Install [Proxyman for Mac](https://proxyman.io)
2. Enable iOS device proxying (Proxyman > Certificate > Install on iOS > Remote Device)
3. Configure your iPhone's WiFi proxy to point at your Mac's IP on port 9090
4. Install and trust the Proxyman CA certificate on your iPhone
5. Open the Eight Sleep app and refresh
6. Filter requests by `8slp.net` in Proxyman
7. Right-click any request > Copy as cURL
8. Extract the Bearer token and user ID from the curl command

### Option C: Email/password auth

If you have your Eight Sleep email and password:

```bash
eight auth --email you@email.com --password yourpassword
```

This uses Eight Sleep's OAuth2 endpoint directly. The token expires after ~24 hours.

### Finding the right user ID

Eight Sleep beds have two sides. After auth, verify you're looking at the correct side:

```bash
eight whoami    # shows your user ID and side (left/right)
eight device    # shows leftUserId and rightUserId
```

If you need the other side's data, re-auth with their user ID:

```bash
eight auth --token "same-token" --user-id "other-side-user-id"
```

## Usage

### Sleep Data

```bash
eight sleep last              # last night's sleep
eight sleep today             # current/most recent session
eight sleep week              # last 7 days
eight sleep range 2024-01-01 2024-01-31   # custom range

# JSON output for piping/scripting
eight sleep last --json
eight sleep week --json
```

Sleep data includes: sleep score, deep/REM/light/awake durations, heart rate, HRV, respiratory rate, bed temperature, room temperature, toss & turns, presence start/end.

### Temperature Control

```bash
eight temp status             # current temperature settings
eight temp set -30            # set level (-100 to 100)
eight temp set -50 -d 60      # set level for 60 minutes
eight temp on                 # turn on autopilot
eight temp off                # turn off

# Set per-stage autopilot temperatures
eight temp stage bedtime -20
eight temp stage initial -40
eight temp stage final 10
```

### Alarms

```bash
eight alarm list              # list all alarms
eight alarm create 07:00:00   # create alarm at 7am
eight alarm enable ALARM_ID
eight alarm disable ALARM_ID
eight alarm snooze ALARM_ID --minutes 9
eight alarm dismiss ALARM_ID
```

### Adjustable Base

```bash
eight base status
eight base set --torso 20 --leg 10
eight base flat
```

### Speaker

```bash
eight speaker status
eight speaker tracks
eight speaker play
eight speaker pause
eight speaker volume 50
eight speaker track TRACK_ID
```

### Other

```bash
eight whoami                  # authenticated user info
eight device                  # device details (model, firmware, sides)
eight away start              # start away mode
eight away end                # end away mode
eight prime                   # start priming cycle
```

### JSON Output

All commands support `--json` for structured output:

```bash
eight sleep week --json | jq '.days[] | {day, score, deepDuration}'
```

## API Reference

Three base URLs:
- **Auth**: `https://auth-api.8slp.net/v1`
- **Client API**: `https://client-api.8slp.net/v1`
- **App API**: `https://app-api.8slp.net/`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/tokens` (auth) | POST | OAuth2 password grant |
| `/v1/users/me` | GET | Authenticated user info |
| `/v1/devices/{id}` | GET | Device info (sides, features) |
| `/v1/users/{id}/trends` | GET | Sleep data (the main endpoint) |
| `/v1/users/{id}/temperature` (app) | GET/PUT | Temperature control |
| `/v2/users/{id}/alarms` (app) | GET | List alarms |
| `/v1/users/{id}/alarms` (app) | POST | Create alarm |
| `/v1/users/{id}/base` (app) | GET | Base status |
| `/v1/users/{id}/audio/player` (app) | GET | Speaker status |

### Trends Query Parameters

```
tz=America/Los_Angeles
from=2024-01-01
to=2024-01-07
include-all-sessions=true
include-main=false
model-version=v2
```

### Trends Response Fields

```
score                                    # sleep score (0-100)
sleepDuration                            # total sleep seconds
deepDuration / remDuration / lightDuration   # stage durations
presenceStart / presenceEnd              # bed entry/exit (UTC)
tnt                                      # toss & turns count
sleepQualityScore.heartRate.average      # avg HR during sleep
sleepQualityScore.hrv.current            # HRV
sleepQualityScore.respiratoryRate.average # breath rate
sleepQualityScore.tempBedC.average       # bed temperature
sleepQualityScore.tempRoomC.average      # room temperature
sessions[].stages[]                      # sleep stage timeline
sessions[].timeseries.heartRate          # HR time series [[ts, val], ...]
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `EIGHT_SLEEP_TOKEN` | Bearer token from auth |
| `EIGHT_SLEEP_USER_ID` | Your user ID |
| `EIGHT_SLEEP_DEVICE_ID` | Device ID (auto-detected) |

Stored in `.env` in the CLI directory or parent directory.

## Acknowledgments

API structure derived from [lukas-clarke/eight_sleep](https://github.com/lukas-clarke/eight_sleep) (Home Assistant integration).

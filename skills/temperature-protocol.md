# Eight Sleep Temperature Protocol Skill

Use when configuring Eight Sleep temperature settings, troubleshooting sleep quality via temperature adjustments, or explaining the science of thermoregulation and sleep.

## Eight Sleep CLI Temperature Commands

```bash
eight temp status                    # current state, levels, autopilot settings
eight temp set -40                   # manual level (-100 to 100)
eight temp set -50 --duration 60     # timed (minutes)
eight temp on                        # enable autopilot (smart mode)
eight temp off                       # turn off temperature control

# Per-stage autopilot (the main optimization lever)
eight temp stage bedtime -20         # when you get in bed
eight temp stage initial -50         # deep sleep phase (first half)
eight temp stage final 10            # REM phase (second half)
```

## The Science

### Why Temperature Matters for Sleep

1. **Sleep onset requires a 2-3F core temperature drop.** The body does this via peripheral vasodilation (hands/feet warm up, dumping heat). A cool mattress surface accelerates this.

2. **Deep sleep (N3/SWS) is enhanced by body cooling.** The brain's thermostat lowers its setpoint during NREM. External cooling supports this descent, increasing time in N3.

3. **REM sleep suspends thermoregulation.** During REM, you can't shiver or sweat. If the environment is too cold, the body exits REM to protect core temp. Warming the second half of the night protects REM.

### Key Papers

**Moyen et al. 2024** - "Sleeping for One Week on a Temperature-Controlled Mattress Cover Improves Sleep and Cardiovascular Recovery" (Bioengineering, n=54, 300+ nights)
- Cooler first-half temps: **+14 min deep sleep (+22%, p=0.003)** in men
- Cooler first-half temps: **+9 min REM (+25%, p=0.033)** in women
- Pod ON vs OFF: **sleeping HR decreased 2%, HRV increased 7%**
- This is Eight Sleep's own clinical study (conflict of interest noted)

**Herberger et al. 2024** - "Enhanced conductive body heat loss during sleep increases slow-wave sleep and calms the heart" (Scientific Reports, n=72)
- N3 increased by **+7.5 min per 7.5-hour night**
- Heart rate decreased by **-2.36 bpm**
- Aggressive cooling decreased REM in the second half (important: don't overcool late at night)

**Raymann et al. 2008** - "Skin deep: enhanced sleep depth by cutaneous temperature manipulation" (Brain)
- 0.4C skin temp manipulation nearly **doubled slow-wave sleep from 8% to 14%** in elderly
- Even tiny temperature changes measurably affect sleep architecture

**Haghayegh et al. 2022** - "Novel temperature-controlled sleep system to improve sleep" (J Sleep Research, n=11)
- Dual-zone cooled mattress: participants fell asleep **58% faster**
- Mechanism: cervical spine warming → peripheral vasodilation → core temp drop

**Krauchi et al. 1999** - "Warm feet promote the rapid onset of sleep" (Nature)
- Sleep onset latency determined by distal-proximal skin temperature gradient
- Warm feet = faster heat loss from core = faster sleep onset

**Siegel et al. 2022** - "REM sleep and body temperature" (Lancet Neurology)
- Cross-species: lower body temp = more REM sleep
- REM functions as a "thermostatically controlled brain heater"
- Too-cold environments suppress REM because the brain exits REM to thermoregulate

## Recommended Configurations

### For maximizing deep sleep (primary goal)

```bash
eight temp stage bedtime -30     # cool to initiate sleep onset
eight temp stage initial -50     # aggressive cooling for first half
eight temp stage final 0         # neutral for second half (protect REM)
```

Pair with: room temp 65-67F, no heavy blankets, socks on (warm feet → vasodilation → core cooling).

### For sleep onset problems (can't fall asleep)

```bash
eight temp stage bedtime -40     # aggressive pre-cooling
eight temp stage initial -30     # moderate sustained cool
eight temp stage final 10        # slight warmth for natural waking
```

The bed pre-cools ~45 min before scheduled bedtime. Combined with no screens 1h before bed and magnesium glycinate 400mg.

### For REM optimization (already getting good deep sleep)

```bash
eight temp stage bedtime -20     # moderate cool
eight temp stage initial -30     # moderate cool
eight temp stage final 15        # warm for REM-dominant second half
```

Note: warming too aggressively in final stage can cause night sweats and awakenings.

### For someone going to bed at 3am (circadian mismatch)

```bash
eight temp stage bedtime -40     # compensate for delayed melatonin
eight temp stage initial -50     # maximize whatever deep sleep you get
eight temp stage final -10       # stay cool (cortisol surge at 5-8am)
```

At 3am bedtime, cortisol starts rising only 2-3 hours into sleep. Keeping the bed cool through the morning helps maintain sleep continuity against the cortisol surge.

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Can't fall asleep | Bed not cool enough at bedtime | Lower bedtime stage by 10 |
| Waking at 3-4am | Bed too cold in second half | Raise final stage by 10-15 |
| Low deep sleep | Initial stage not cool enough | Lower initial stage by 10-20 |
| Low REM | Final stage too cold | Raise final stage to 0 or slightly positive |
| Night sweats | Final stage too warm | Lower final stage by 10 |
| Waking up cold | Final/wake stage too low | Raise to +10 or +20 |

## Monitoring Impact

After changing temperature settings, give it 3-5 nights to stabilize. Then compare:

```bash
# Get last 14 days of data
eight sleep range $(date -v-14d +%Y-%m-%d) $(date +%Y-%m-%d) --json | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for d in data['days']:
    deep = d.get('deepDuration', 0) or 0
    print(f\"{d['day']}  Deep: {deep//60}m  Score: {d.get('score',0)}\")
"
```

## When to Reference This Skill

- User asks about Eight Sleep temperature settings
- Sleep data shows low deep sleep or poor sleep onset
- Correlating temperature changes with sleep quality changes
- Setting up autopilot for the first time
- Troubleshooting sleep quality issues that may be temperature-related

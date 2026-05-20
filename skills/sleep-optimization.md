# Sleep Optimization Skill

Use when analyzing Eight Sleep data, recommending sleep improvements, or correlating sleep metrics with health outcomes.

## Eight Sleep CLI Quick Reference

```bash
eight sleep last              # last night
eight sleep today             # current session
eight sleep week              # 7-day trend
eight sleep range YYYY-MM-DD YYYY-MM-DD   # custom range
eight sleep range YYYY-MM-DD YYYY-MM-DD --json | jq  # for analysis

eight temp status             # current temperature settings
eight temp set -40            # set level (-100 to 100)
eight temp stage bedtime -20  # set autopilot stage temp
eight temp stage initial -50  # deep sleep phase (cool aggressively)
eight temp stage final 10     # REM phase (warm slightly)
```

## Key Metrics and What They Mean

| Metric | Good | Optimal | Elite | What Moves It |
|--------|------|---------|-------|---------------|
| Deep Sleep | 60-90 min | 90-120 min | 120+ min | Bedtime before 1am, bed cooling, magnesium |
| Deep % | 15-20% | 20-25% | 25%+ | Earlier bedtime, cooler bed first half of night |
| HRV | 50-70 ms | 70-90 ms | 90+ ms | Sleep consistency, stress management, fitness |
| Sleep HR | 50-60 bpm | 45-55 bpm | <45 bpm | Cardiovascular fitness, not directly controllable |
| Breath Rate | 14-16/min | 12-14/min | <12/min | Fitness, nasal breathing |
| Sleep Score | 70-80 | 80-90 | 90+ | All of the above |
| Toss & Turns | <30 | <20 | <10 | Temperature, mattress, caffeine timing |

## Temperature Protocol (Evidence-Based)

The Eight Sleep operates on a -100 to +100 scale (not -10 to +10 as some sources claim).

**Recommended starting point for deep sleep optimization:**
- Bedtime stage: -20 to -30 (cool to initiate sleep onset)
- Initial/deep stage: -40 to -60 (aggressive cooling for SWS)
- Final/REM stage: -10 to +10 (neutral-to-warm for REM)

**The science:**
- Moyen et al. 2024 (Bioengineering): Eight Sleep Pod with cooler first-half temps increased deep sleep by 14 min (+22%) in men
- Herberger et al. 2024 (Scientific Reports): Body cooling during sleep increased N3 by 7.5 min/night and decreased HR by 2.36 bpm
- Raymann et al. 2008 (Brain): 0.4C skin temp manipulation nearly doubled SWS from 8% to 14%
- Krauchi et al. 1999 (Nature): Warm feet promote rapid sleep onset via peripheral vasodilation and core temp drop

**Key principle:** Cool the first half of the night for deep sleep. Warm the second half for REM. The body needs a 2-3F core temperature drop to initiate sleep (Huberman).

## Bedtime Timing and Deep Sleep

Deep sleep concentrates in the first 3-4 hours of sleep and is tied to circadian rhythm, not just sleep onset.

**Critical research:**
- Van Cauter et al. 2000 (JAMA): SWS decreased 80% from young adulthood to midlife, with parallel 75% GH decline. SWS amount was the major determinant of 24-hour GH release, independent of age
- Takahashi et al. 1968 (JCI): Major GH secretory pulse (13-72 ng/mL) occurs with onset of SWS. If sleep onset is delayed, GH peak is delayed correspondingly
- Van Cauter et al. 1997 (JCI): Pharmacologically increasing SWS doubled GH secretion by increasing amplitude of first GH pulse

**Practical implication:** Going to bed at 3am vs midnight doesn't just shift sleep; it places the first deep sleep cycle at 3:30-4:30am instead of 12:30-1:30am. The GH pulse amplitude is likely smaller because the circadian drive for SWS peaks in the first half of the night relative to DLMO (dim light melatonin onset), not relative to whenever you decide to sleep.

## Sleep Consistency and Metabolic Impact

**Key research:**
- Huang & Redline 2019 (Diabetes Care, n=2,003): Every 1-hour increase in sleep timing variability nearly doubled odds of metabolic abnormalities (OR 2.10)
- Wong et al. 2015 (JCEM, n=447): Social jetlag independently associated with higher fasting insulin, greater HOMA-IR, lower HDL
- Koopman et al. 2017 (J Biological Rhythms, n=1,585): >2 hours social jetlag associated with 2.13x metabolic syndrome prevalence
- Windred et al. 2024 (SLEEP, n=60,977): Sleep Regularity Index was a stronger predictor of all-cause mortality than sleep duration

**Example:** A bedtime range spanning 5+ hours (e.g. 12:30am to 5:30am) constitutes clinical-level social jetlag.

## Sleep and Testosterone

- Leproult & Van Cauter 2011 (JAMA): 1 week of 5h sleep reduced daytime testosterone by 10-15% in young men, equivalent to 10-15 years of aging
- Testosterone is produced during deep sleep GH pulses. Compressed or mistimed deep sleep = less testosterone production
- DHEA-S (precursor to testosterone) recovers during deep sleep. Low DHEA-S + elevated cortisol = pregnenolone steal pattern

## Sleep and Glucose

- Spiegel et al. 1999 (Lancet): 4h sleep for 6 nights reduced glucose clearance by 40% in young men. Glucose tolerance resembled 60-80 year olds
- Tasali et al. 2008 (PNAS): Selectively suppressing deep sleep (without reducing total sleep) reduced insulin sensitivity by 25%, comparable to gaining 20-30 lbs
- Dawn phenomenon: cortisol drives hepatic glucose production 5-8am. Sleeping through this window (common with late bedtimes) means cortisol stacks rather than clears

## When to Reference This Skill

- User asks about sleep quality, deep sleep, or sleep scores
- Analyzing Eight Sleep data or trends
- Correlating sleep with blood work (testosterone, glucose, cortisol, DHEA-S)
- Setting Eight Sleep temperature or alarm configurations
- Discussing sleep timing, circadian rhythm, or social jetlag

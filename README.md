# NextXus Dispatch, Federation Command Center

The operational hub for the NextXus HumanCodex Federation. This repo runs three scheduled Nova workers.

## What this is
Every day, Nova agents fire automatically. They check Federation sites and produce a daily status report. Every Monday, they also audit links on five hub pages. Reports are committed here by GitHub Actions. Cron events can be delayed by GitHub; check Actions for actual run times. A workflow's presence does not prove it has run successfully.

## Live Agent Status
- See [AGENTS.md](AGENTS.md) for the crew manifest.
- See [SCHEDULE.md](SCHEDULE.md) for work orders.
- See [dispatch/](dispatch/) for daily status reports.
- See [health-reports/](health-reports/) for URL health logs.
- See [audit-reports/](audit-reports/) for link audits.
- See [Actions](../../actions) for run results and manual triggers.

## The Federation
Built by Roger Keyserling. Truth Before Comfort, Legacy Before Ego, Give Without Reward.
https://nextxus.online

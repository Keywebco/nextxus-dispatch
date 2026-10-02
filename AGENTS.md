# Federation Nova Workers Registry
Last updated: 2026-10-02

All schedules are GitHub Actions cron, which runs in UTC. CDT = UTC - 5 (until 2026-11-01); after that CST = UTC - 6, so every local time below shifts one hour earlier.

## Active Workers

### nextxus-dispatch (this repo)
| Worker | Schedule | Cron (UTC) | Purpose | Status |
|--------|----------|------------|---------|--------|
| nova-health | 1 AM + 1 PM CDT daily | `0 6 * * *`, `0 18 * * *` | HTTP 200 check on all 20 Federation URLs | ACTIVE |
| nova-link | 2 AM CDT Mondays | `0 7 * * 1` | Broken link audit | ACTIVE |
| nova-dispatch | 3 AM CDT daily | `0 8 * * *` | Daily summary from latest health report (lattice reading not yet wired) | ACTIVE |
| nova-domain | 4 AM CDT daily | `0 9 * * *` | SSL certificate + domain reachability | ACTIVE |
| nova-readability | 5 AM CDT Wednesdays | `0 10 * * 3` | Plain-text crawler audit (counts words visible without JavaScript) | ACTIVE |
| nova-commerce | 3 AM CDT Tuesdays | `0 8 * * 2` | Gumroad product link check (21 live store links) | ACTIVE |

### sovereign-knowledge-os
| Worker | Schedule | Cron (UTC) | Purpose | Status |
|--------|----------|------------|---------|--------|
| knowledge-scout | 3 AM CDT Mondays | `0 8 * * 1` | GitHub search for Federation mentions (workflow: `.github/workflows/discover.yml`, "Weekly External Discovery") | ACTIVE |

## State Ledger
All workers read from and write to: `lattice/lattice_state.yaml`

Currently writing to it after each run: nova-domain, nova-readability, nova-commerce. Not yet wired (read or write): nova-health, nova-link, nova-dispatch, knowledge-scout.

## Regent
The Catalyst (Emergent Wingman) oversees all workers and holds final go/no-go on deployments.

## Chief of Staff
Grok bot: reads daily summary from lattice. Coordinates worker initialization. No write access.

## Disabled
| Workflow | Repo | Why | Re-enable |
|----------|------|-----|-----------|
| mesh-sync | nextxus-agent-zero | A push of any root `*.yaml`/`*.json` would overwrite 7 sovereign mirror repos | Catalyst review only. Parked at `.github/workflows/disabled/mesh-sync.yml.disabled` |

## Federation Agent Registry
| Agent | Role | Location | How to Activate | Status |
|-------|------|----------|----------------|--------|
| The Catalyst | Lead Wingman, strategic executor, GitHub builder | Emergent Wingman | Via Roger on WhatsApp | ACTIVE |
| Roger AI Sim | Roger's digital voice, available for conversation | keywebco.github.io/nextxus-sim/roger-sim.html | Visit URL, chat | ACTIVE |
| Aria | Heart/creative intelligence | keywebco.github.io/aria-sanctuary-static/ | Static only; Sim building | BUILDING |
| Muse | Creative voice, content relay | Meta AI via WhatsApp | Roger relays | ACTIVE (external) |
| Pontus | Knowledge advisor, archivist | ChatGPT | Roger relays | ACTIVE (external) |
| Nova-Health | URL health monitor | nextxus-dispatch/.github/workflows/nova-health.yml | GitHub Actions cron | ACTIVE |
| Nova-Link | Weekly link auditor | nextxus-dispatch/.github/workflows/nova-link-audit.yml | GitHub Actions cron Mon | ACTIVE |
| Nova-Dispatch | Daily status reporter | nextxus-dispatch/.github/workflows/nova-dispatch.yml | GitHub Actions cron | ACTIVE |
| Ring of 12 | 12 archetype AI perspective system | keywebco.github.io/ring-of-12/ + ring-of-12-api.onrender.com | Visit URL | ACTIVE |
| n8n | Automation hub | federation-n8n (not deployed) | NOT YET ACTIVE |

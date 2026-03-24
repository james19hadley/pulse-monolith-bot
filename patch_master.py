with open("docs/sprints/00_SPRINTS_MASTER.md", "r") as f:
    text = f.read()

text = text.replace("| [Sprint 14](14_PRODUCTION_DEPLOYMENT.md) | Deployment to VPS | 🟡 Active |", "| [Sprint 14](14_PRODUCTION_DEPLOYMENT.md) | Deployment to VPS | 🟢 Completed |\\n| [Sprint 15](15_PRODUCTION_RESILIENCE.md) | Production Resilience (Webhooks & Backups) | 🟢 Completed |\\n| [Sprint 16](16_UX_ONBOARDING_KEYBOARDS.md) | UX Overhaul, Onboarding & Keyboards | 🟡 Active |\\n| [Sprint 17](17_ADMIN_WEB_DASHBOARD.md) | Admin Web Dashboard & Telemetry | ⚪ Draft |")

with open("docs/sprints/00_SPRINTS_MASTER.md", "w") as f:
    f.write(text)

#!/usr/bin/env python3
"""
CEO Briefing Generator Script
Aggregates data from Odoo and vault to generate weekly business briefing

Usage:
    python generate_briefing.py --vault /path/to/vault
"""

import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

load_dotenv()


def get_odoo_client():
    """Get Odoo client if available"""
    try:
        from mcp_servers.odoo-mcp.odoo_client import OdooClient
        return OdooClient()
    except:
        try:
            # Alternative import path
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "odoo_client",
                Path(__file__).parent.parent.parent.parent.parent / "mcp_servers" / "odoo-mcp" / "odoo_client.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.OdooClient()
        except Exception as e:
            print(f"⚠️ Odoo not available: {e}")
            return None


def get_week_range():
    """Get start and end of current week"""
    today = date.today()
    start = today - timedelta(days=today.weekday())  # Monday
    end = today  # Today
    return start.isoformat(), end.isoformat()


def count_done_tasks(vault_path: Path, start_date: str) -> list:
    """Count tasks completed this week"""
    done_folder = vault_path / 'Done'
    tasks = []

    if not done_folder.exists():
        return tasks

    for file in done_folder.glob('*.md'):
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime.strftime('%Y-%m-%d') >= start_date:
            tasks.append(file.stem)

    return tasks


def get_pending_approvals(vault_path: Path) -> list:
    """Get pending approval items"""
    folder = vault_path / 'Pending_Approval'
    items = []

    if not folder.exists():
        return items

    for file in folder.glob('*.md'):
        items.append(file.stem)

    return items


def get_bottlenecks(vault_path: Path) -> list:
    """Get items stuck in progress"""
    folder = vault_path / 'In_Progress'
    bottlenecks = []

    if not folder.exists():
        return bottlenecks

    three_days_ago = datetime.now() - timedelta(days=3)

    for file in folder.glob('*.md'):
        created = datetime.fromtimestamp(file.stat().st_ctime)
        if created < three_days_ago:
            days = (datetime.now() - created).days
            bottlenecks.append({"name": file.stem, "days": days})

    return bottlenecks


def generate_briefing(vault_path: str) -> str:
    """Generate the full briefing with Odoo data"""
    vault = Path(vault_path)
    start_date, end_date = get_week_range()
    today = date.today()

    print("📊 Generating CEO Briefing...")

    # Get Odoo data
    odoo = get_odoo_client()
    if odoo:
        revenue = odoo.get_revenue_summary(start_date, end_date)
        unpaid = odoo.get_unpaid_invoices()
        overdue = odoo.get_overdue_invoices()
        odoo_ok = True
    else:
        revenue = {"total_invoiced": 0, "total_paid": 0, "total_pending": 0, "invoice_count": 0}
        unpaid = []
        overdue = []
        odoo_ok = False

    # Get vault data
    done_tasks = count_done_tasks(vault, start_date)
    pending = get_pending_approvals(vault)
    bottlenecks = get_bottlenecks(vault)

    # Generate briefing
    briefing = f"""---
generated: {datetime.now().isoformat()}
period: {start_date} to {end_date}
---

# 📋 Monday Morning CEO Briefing

**Week of {today.strftime('%B %d, %Y')}**

---

## 📈 Executive Summary

| Metric | Value |
|--------|-------|
| Revenue (Week) | Rs. {revenue['total_invoiced']:,.2f} |
| Collected | Rs. {revenue['total_paid']:,.2f} |
| Pending | Rs. {revenue['total_pending']:,.2f} |
| Tasks Completed | {len(done_tasks)} |
| Bottlenecks | {len(bottlenecks)} |
| Pending Approvals | {len(pending)} |

---

## 💰 Revenue & Invoicing

- **Total Invoiced**: Rs. {revenue['total_invoiced']:,.2f}
- **Total Collected**: Rs. {revenue['total_paid']:,.2f}
- **Outstanding**: Rs. {revenue['total_pending']:,.2f}
- **Invoice Count**: {revenue['invoice_count']}

"""

    # Unpaid invoices
    if unpaid:
        briefing += "### ⏳ Unpaid Invoices\n\n"
        for inv in unpaid[:5]:
            customer = inv.get('partner_id', [0, 'Unknown'])[1] if inv.get('partner_id') else 'Unknown'
            briefing += f"- {inv['name']} - {customer}: Rs. {inv['amount_residual']:,.2f}\n"
        briefing += "\n"

    # Overdue
    if overdue:
        briefing += "### 🚨 Overdue Invoices\n\n"
        for inv in overdue[:5]:
            customer = inv.get('partner_id', [0, 'Unknown'])[1] if inv.get('partner_id') else 'Unknown'
            briefing += f"- {inv['name']} - {customer}: Rs. {inv['amount_residual']:,.2f}\n"
        briefing += "\n"

    # Completed tasks
    briefing += "---\n\n## ✅ Completed Tasks\n\n"
    if done_tasks:
        for task in done_tasks[:10]:
            briefing += f"- [x] {task}\n"
    else:
        briefing += "- No tasks completed this week\n"

    # Bottlenecks
    briefing += "\n---\n\n## 🚧 Bottlenecks\n\n"
    if bottlenecks:
        for b in bottlenecks:
            briefing += f"- ⚠️ {b['name']} - stuck for {b['days']} days\n"
    else:
        briefing += "✅ No bottlenecks!\n"

    # Pending approvals
    briefing += "\n---\n\n## ⏳ Pending Approvals\n\n"
    if pending:
        for item in pending[:10]:
            briefing += f"- [ ] {item}\n"
    else:
        briefing += "✅ No pending approvals\n"

    # Recommendations
    briefing += "\n---\n\n## 🎯 Recommendations\n\n"
    if overdue:
        briefing += f"1. **Follow up on {len(overdue)} overdue invoices**\n"
    if bottlenecks:
        briefing += f"2. **Unblock {len(bottlenecks)} stuck tasks**\n"
    if pending:
        briefing += f"3. **Process {len(pending)} pending approvals**\n"
    if not overdue and not bottlenecks and not pending:
        briefing += "✅ All clear! Great work this week.\n"

    briefing += f"""
---

*Generated by AI Employee on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Odoo: {'✅ Connected' if odoo_ok else '❌ Offline'}*
"""

    return briefing


def main():
    parser = argparse.ArgumentParser(description='Generate CEO Briefing')
    parser.add_argument('--vault', help='Path to vault', default=os.getenv('VAULT_PATH', './vault'))
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--save', action='store_true', help='Save to vault/Briefings/')

    args = parser.parse_args()

    briefing = generate_briefing(args.vault)

    if args.save:
        vault = Path(args.vault)
        briefings_dir = vault / 'Briefings'
        briefings_dir.mkdir(parents=True, exist_ok=True)
        output = briefings_dir / f"{date.today().isoformat()}_CEO_Briefing.md"
        output.write_text(briefing, encoding='utf-8')
        print(f"✅ Saved: {output}")

    if args.output:
        Path(args.output).write_text(briefing, encoding='utf-8')
        print(f"✅ Saved: {args.output}")

    print(briefing)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Odoo XML-RPC Client
Connects to Odoo Community 19+ via XML-RPC API

Usage:
    from odoo_client import OdooClient
    client = OdooClient()
    invoices = client.get_invoices()
"""

import os
import xmlrpc.client
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class OdooClient:
    """Odoo XML-RPC API Client"""

    def __init__(self):
        self.url = os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = os.getenv("ODOO_DB", "ai_employee")
        self.username = os.getenv("ODOO_USERNAME")
        self.api_key = os.getenv("ODOO_API_KEY")
        self.uid = None

        if not self.username or not self.api_key:
            raise ValueError("ODOO_USERNAME and ODOO_API_KEY required in .env")

        # Setup XML-RPC endpoints
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

        # Authenticate on init
        self._authenticate()

    def _authenticate(self) -> int:
        """Authenticate and get user ID"""
        try:
            self.uid = self.common.authenticate(
                self.db,
                self.username,
                self.api_key,
                {}
            )

            if not self.uid:
                raise Exception("Authentication failed! Check credentials, database name, or API key.")

            print(f"✓ Odoo authenticated. UID: {self.uid}")
            return self.uid

        except Exception as e:
            raise Exception(f"Authentication failed: {e}")

    def _execute(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """Execute Odoo model method"""
        kwargs = kwargs or {}

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.api_key,
            model,
            method,
            args,
            kwargs
        )

    # ==================== CUSTOMERS ====================

    def get_customers(self, limit: int = 100) -> List[Dict]:
        """Get all customers"""
        customer_ids = self._execute(
            "res.partner",
            "search",
            [[["is_company", "=", False]]],
            {"limit": limit}
        )

        if not customer_ids:
            return []

        return self._execute(
            "res.partner",
            "read",
            [customer_ids],
            {"fields": ["id", "name", "email", "phone"]}
        )

    def create_customer(self, name: str, email: str = None, phone: str = None) -> int:
        """Create new customer"""
        data = {"name": name}
        if email:
            data["email"] = email
        if phone:
            data["phone"] = phone

        customer_id = self._execute("res.partner", "create", [data])
        print(f"✓ Customer created: {name} (ID: {customer_id})")
        return customer_id

    def find_customer_by_name(self, name: str) -> Optional[Dict]:
        """Find customer by name"""
        customer_ids = self._execute(
            "res.partner",
            "search",
            [[["name", "ilike", name]]],
            {"limit": 1}
        )

        if not customer_ids:
            return None

        customers = self._execute(
            "res.partner",
            "read",
            [customer_ids],
            {"fields": ["id", "name", "email", "phone"]}
        )
        return customers[0] if customers else None

    # ==================== INVOICES ====================

    def get_invoices(self, state: str = None, limit: int = 100) -> List[Dict]:
        """
        Get invoices
        state: 'draft', 'posted', 'cancel' or None for all
        """
        domain = [["move_type", "=", "out_invoice"]]
        if state:
            domain.append(["state", "=", state])

        invoice_ids = self._execute(
            "account.move",
            "search",
            [domain],
            {"limit": limit, "order": "invoice_date desc"}
        )

        if not invoice_ids:
            return []

        return self._execute(
            "account.move",
            "read",
            [invoice_ids],
            {"fields": [
                "id", "name", "partner_id", "invoice_date", "invoice_date_due",
                "amount_total", "amount_residual", "state", "payment_state"
            ]}
        )

    def create_invoice(
        self,
        customer_name: str,
        amount: float,
        description: str,
        due_date: str = None
    ) -> Dict:
        """
        Create a new invoice

        Args:
            customer_name: Customer name (will find or create)
            amount: Invoice amount
            description: Line item description
            due_date: Due date (YYYY-MM-DD) or None for today

        Returns:
            Invoice dict with id, name, amount, state
        """
        # Find or create customer
        customer = self.find_customer_by_name(customer_name)
        if not customer:
            customer_id = self.create_customer(customer_name)
        else:
            customer_id = customer["id"]

        # Prepare invoice data
        invoice_data = {
            "move_type": "out_invoice",
            "partner_id": customer_id,
            "invoice_date": date.today().isoformat(),
            "invoice_line_ids": [(0, 0, {
                "name": description,
                "quantity": 1,
                "price_unit": amount
            })]
        }

        if due_date:
            invoice_data["invoice_date_due"] = due_date

        # Create invoice
        invoice_id = self._execute("account.move", "create", [invoice_data])

        # Get invoice details
        invoice = self._execute(
            "account.move",
            "read",
            [[invoice_id]],
            {"fields": ["id", "name", "amount_total", "state"]}
        )[0]

        print(f"✓ Invoice created: {invoice['name']} - {amount}")
        return invoice

    def confirm_invoice(self, invoice_id: int) -> bool:
        """Confirm/Post a draft invoice"""
        self._execute("account.move", "action_post", [[invoice_id]])
        print(f"✓ Invoice {invoice_id} confirmed")
        return True

    def get_unpaid_invoices(self) -> List[Dict]:
        """Get all unpaid invoices"""
        invoice_ids = self._execute(
            "account.move",
            "search",
            [[
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]]
            ]]
        )

        if not invoice_ids:
            return []

        return self._execute(
            "account.move",
            "read",
            [invoice_ids],
            {"fields": [
                "id", "name", "partner_id", "invoice_date", "invoice_date_due",
                "amount_total", "amount_residual", "payment_state"
            ]}
        )

    # ==================== REPORTS ====================

    def get_revenue_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """
        Get revenue summary for date range

        Args:
            start_date: Start date (YYYY-MM-DD) or None for month start
            end_date: End date (YYYY-MM-DD) or None for today

        Returns:
            Dict with total_invoiced, total_paid, total_pending
        """
        if not start_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
        if not end_date:
            end_date = date.today().isoformat()

        # Get all posted invoices in range
        invoices = self._execute(
            "account.move",
            "search_read",
            [[
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["invoice_date", ">=", start_date],
                ["invoice_date", "<=", end_date]
            ]],
            {"fields": ["amount_total", "amount_residual", "payment_state"]}
        )

        total_invoiced = sum(inv["amount_total"] for inv in invoices)
        total_pending = sum(inv["amount_residual"] for inv in invoices)
        total_paid = total_invoiced - total_pending

        return {
            "period": f"{start_date} to {end_date}",
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "total_pending": total_pending,
            "invoice_count": len(invoices)
        }

    def get_overdue_invoices(self) -> List[Dict]:
        """Get all overdue invoices"""
        today = date.today().isoformat()

        invoice_ids = self._execute(
            "account.move",
            "search",
            [[
                ["move_type", "=", "out_invoice"],
                ["state", "=", "posted"],
                ["payment_state", "in", ["not_paid", "partial"]],
                ["invoice_date_due", "<", today]
            ]]
        )

        if not invoice_ids:
            return []

        return self._execute(
            "account.move",
            "read",
            [invoice_ids],
            {"fields": [
                "id", "name", "partner_id", "invoice_date_due",
                "amount_total", "amount_residual"
            ]}
        )


# ==================== CLI TESTING ====================

if __name__ == "__main__":
    print("Testing Odoo Client...")
    print("=" * 50)

    try:
        client = OdooClient()

        # Test: Get customers
        print("\n📋 Customers:")
        customers = client.get_customers(limit=5)
        if customers:
            for c in customers:
                print(f"  - {c['name']} ({c.get('email', 'no email')})")
        else:
            print("  (no customers yet)")

        # Test: Get invoices
        print("\n📄 Recent Invoices:")
        invoices = client.get_invoices(limit=5)
        if invoices:
            for inv in invoices:
                print(f"  - {inv['name']}: {inv['amount_total']} ({inv['state']})")
        else:
            print("  (no invoices yet)")

        # Test: Revenue summary
        print("\n💰 Revenue Summary (This Month):")
        summary = client.get_revenue_summary()
        print(f"  - Total Invoiced: {summary['total_invoiced']}")
        print(f"  - Total Paid: {summary['total_paid']}")
        print(f"  - Total Pending: {summary['total_pending']}")

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")

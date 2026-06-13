# property_management_solution/agreement.py (or utils.py)
import frappe

def billing_scheduler():
    agreements = frappe.get_all("Agreement", filters={"status": "Active"}, pluck="name")
    for name in agreements:
        try:
            doc = frappe.get_doc("Agreement", name)
            doc.generate_next_billing()
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"Billing Scheduler Failed for Agreement {name}")

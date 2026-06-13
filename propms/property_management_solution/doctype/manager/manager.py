# property_management_solution/doctype/manager/manager.py

import frappe
from frappe.model.document import Document
from frappe.utils import today, add_years

class Manager(Document):
    def before_insert(self):
        """Create User and Employee before Manager is inserted."""
        # --- 1. Ensure User exists ---
        if not self.email:
            frappe.throw("Email is required to create a User and Employee.")

        if frappe.db.exists("User", self.email):
            user = frappe.get_doc("User", self.email)
        else:
            user = frappe.new_doc("User")
            user.email = self.email
            user.first_name = self.first_name
            user.last_name = self.last_name
            user.enabled = 1
            user.send_welcome_email = 0

            # Assign roles BEFORE insert
            user.append("roles", {"role": "Property Manager"})

            user.insert(ignore_permissions=True) # Assign role if you have one

        # --- 2. Create Employee ---
        emp_name = frappe.db.exists("Employee", {"user_id": user.name})
        if emp_name:
            employee = frappe.get_doc("Employee", emp_name)
        else:
            employee = frappe.get_doc({
                "doctype": "Employee",
                "first_name": self.first_name,
                "last_name": self.last_name,
                "status": "Active",
                "user_id": user.name,
                "company": frappe.defaults.get_global_default("company"),
                "designation": self.designation or "Manager",

                # Required Fields with defaults
                "gender": self.gender or "Other",  # fallback value
                "date_of_birth": self.date_of_birth, 
                "date_of_joining": today()
            })
            employee.insert(ignore_permissions=True)

        # --- 3. Link Employee back to Manager doc ---
        self.employee_id = employee.name

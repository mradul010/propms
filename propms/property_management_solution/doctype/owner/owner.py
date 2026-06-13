# property_management_solution/doctype/owner/owner.py

import frappe
from frappe.model.document import Document

class Owner(Document):
    def before_insert(self):
        """Create a User and link it before the Owner is inserted."""
        if not self.user_id and self.email:
            # Check if user already exists
            if frappe.db.exists("User", self.email):
                self.user_id = self.email
            else:
                # Create new user
                user = frappe.new_doc("User")
                user.email = self.email
                user.first_name = self.first_name
                user.last_name = self.last_name
                user.user_name = (self.first_name or "") + "_" + (self.last_name or "")
                user.enabled = 1
                user.send_welcome_email = 0

                # ✅ Assign roles BEFORE insert (prevents "No Roles Specified" popup)
                user.append("roles", {"role": "Property Owner"})
                user.append("roles", {"role": "System Manager"})

                user.insert(ignore_permissions=True)

                # Link back to Owner
                self.user_id = user.name

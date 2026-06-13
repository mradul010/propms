import frappe
from frappe.utils import nowdate, now_datetime, today

@frappe.whitelist()
def send_billing_entry(docname):
    doc = frappe.get_doc("Agreement Billing Entry", docname)
    if doc.status not in ["Pending", "Sent"]:
        frappe.throw("Only Pending or Sent entries can be re-sent")
    # your email/notification logic here
    doc.status = "Sent"
    doc.save()
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def pay_billing_entry(docname):
    doc = frappe.get_doc("Agreement Billing Entry", docname)
    if doc.status in ["Paid", "Cancelled"]:
        frappe.throw("This entry cannot be paid")
    # your payment handling logic here
    doc.status = "Paid"
    doc.save()
    frappe.db.commit()
    return {"status": "ok"}

@frappe.whitelist()
def pay_billing_entry_with_invoice(billing_entry_name):
    billing = frappe.get_doc("Agreement Billing Entry", billing_entry_name)

    if billing.status == "Paid":
        frappe.throw("Billing Entry already paid.")

    agreement = frappe.get_doc("Agreement", billing.agreement)

    if not agreement.sales_order:
        frappe.throw("Sales Order not found for Agreement.")

    # 1️⃣ Create Sales Invoice (qty = 1)
    si = frappe.get_doc({
        "doctype": "Sales Invoice",
        "customer": billing.customer,
        "posting_date": today(),
        "due_date": billing.due_date,
        "items": [{
            "item_code": agreement.room,
            "qty": 1,
            "rate": billing.amount,
            "sales_order": agreement.sales_order
        }],
        "agreement": agreement.name,
        "agreement_billing_entry": billing.name
    })

    si.insert(ignore_permissions=True)
    si.submit()

    # 2️⃣ Create Payment Entry
    company = frappe.defaults.get_global_default("company")

# Accounts Receivable
    party_account = frappe.db.get_value(
        "Party Account",
        {"parent": billing.customer, "company": company},
        "account"
    ) or frappe.get_cached_value(
        "Company", company, "default_receivable_account"
    )

# Cash / Bank account from Mode of Payment
    paid_to_account = frappe.db.get_value(
        "Mode of Payment Account",
        {"parent": billing.mode_of_payment, "company": company},
        "default_account"
    )

    if not paid_to_account:
        frappe.throw(
            f"Default account not set for Mode of Payment {billing.mode_of_payment}"
        )

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.company = company

    pe.party_type = "Customer"
    pe.party = billing.customer

    pe.posting_date = today()
    pe.mode_of_payment = billing.mode_of_payment

# 🔑 MANDATORY ACCOUNTS
    pe.paid_from = party_account
    pe.paid_to = paid_to_account

# 🔑 MANDATORY AMOUNTS
    pe.paid_amount = billing.amount
    pe.received_amount = billing.amount

# Reference to Sales Invoice
    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": si.name,
        "allocated_amount": billing.amount
    })
    
    # 2.5️⃣ Insert Cheque History (ON PAYMENT)
    if billing.mode_of_payment == "Cheque":
        frappe.get_doc({
        "doctype": "Agreement Cheque History",
        "parent": agreement.name,
        "parenttype": "Agreement",
        "parentfield": "cheque_history",

        "billing_entry": billing.name,
        "cheque_no": billing.cheque_no,
        "cheque_date": billing.cheque_date,
        "presenting_date": today(),
        "amount": billing.amount,
        "status": "Deposited",  # 👈 IMPORTANT
        "payment_entry": pe.name,
        "remarks": "Cheque presented and payment recorded"
        }).insert(ignore_permissions=True)


# Cheque support
    if billing.mode_of_payment == "Cheque":
        pe.reference_no = billing.cheque_no
        pe.reference_date = billing.cheque_date

    pe.insert(ignore_permissions=True)
    pe.submit()
    
    

    # 3️⃣ Update Billing Entry
    frappe.db.set_value(
        "Agreement Billing Entry",
        billing.name,
        {
            "status": "Paid",
            "sales_invoice": si.name,
            "payment_entry": pe.name
        }
    )

    # 4️⃣ Update Payment Schedule row
    if billing.cheque_row_id:
        update_data = {
            "status": "Paid",
            "payment_entry": pe.name
        }

        if billing.mode_of_payment == "Cheque":
            update_data.update({
                "cheque_no": billing.cheque_no,
                "cheque_date": billing.cheque_date
            })

        frappe.db.set_value(
            "Agreement Payment Schedule",
            billing.cheque_row_id,
            update_data
        )


    return {
        "sales_invoice": si.name,
        "payment_entry": pe.name
    }


@frappe.whitelist()
def mark_cheque_bounced(billing_entry):

    be = frappe.get_doc("Agreement Billing Entry", billing_entry)

    if be.mode_of_payment != "Cheque":
        frappe.throw("Only Cheque payments allowed.")

    if be.status != "Paid":
        frappe.throw("Only Paid entries can be bounced.")

    if not be.payment_entry:
        frappe.throw("No Payment Entry linked.")

    # 1️⃣ Cancel Payment Entry
    pe = frappe.get_doc("Payment Entry", be.payment_entry)
    if pe.docstatus == 1:
        pe.cancel()

    # 2️⃣ Update Billing Entry
    be.db_set("status", "Overdue")
    be.db_set("payment_entry", None)

    # 3️⃣ Update Payment Schedule
    if be.cheque_row_id:
        frappe.db.set_value(
        "Agreement Payment Schedule",
        be.cheque_row_id,
        {
            "status": "Overdue",
            "payment_entry": None
        }
    )

    # 4️⃣ Insert history row (SAFE)
    frappe.get_doc({
        "doctype": "Agreement Cheque History",
        "parent": be.agreement,
        "parenttype": "Agreement",
        "parentfield": "cheque_history",

        "billing_entry": be.name,
        "cheque_no": be.cheque_no,
        "cheque_date": be.cheque_date,
        "presenting_date": frappe.utils.today(),
        "amount": be.amount,
        "status": "Bounced",
        "payment_entry": pe.name,
        "remarks": "Cheque bounced"
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    return "Cheque marked as Bounced and history recorded successfully."

# @frappe.whitelist()
# def pay_billing_with_cheque(billing_entry_name):

#     billing = frappe.get_doc("Agreement Billing Entry", billing_entry_name)
#     agreement = frappe.get_doc("Agreement", billing.agreement)

#     if billing.status == "Paid":
#         frappe.throw("Billing Entry is already paid.")

#     # Find next unused cheque
#     cheque_row = None
#     for row in agreement.cheque_schedule:
#         if row.status == "Draft":
#             cheque_row = row
#             break

#     if not cheque_row:
#         frappe.throw("No available cheque found for this Agreement.")

#     if not cheque_row.cheque_no:
#         frappe.throw("Cheque Number is required before payment.")
        
#     if not cheque_row.cheque_date:
#         frappe.throw("Cheque Date is required before payment.")

#     # Create Payment Entry using cheque data
#     pe = create_customer_direct_payment(
#         party=agreement.lease_customer,
#         mode_of_payment="Cheque",
#         paid_amount=cheque_row.amount,
#         reference_no=cheque_row.cheque_no,
#         posting_date=cheque_row.cheque_date,
#         reference_date=cheque_row.cheque_date
#     )

#     # Update Billing Entry
#     billing.status = "Paid"
#     billing.cheque_no = cheque_row.cheque_no
#     billing.cheque_date = cheque_row.cheque_date
#     billing.cheque_row_id = cheque_row.name
#     billing.payment_entry = pe["payment_entry"]
#     billing.save(ignore_permissions=True)

#     # Update Cheque Row (simple for now)
#     cheque_row.status = "Cleared"
#     cheque_row.payment_entry = pe["payment_entry"]
#     cheque_row.save(ignore_permissions=True)

#     return {
#         "payment_entry": pe["payment_entry"]
#     }

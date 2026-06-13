import frappe

@frappe.whitelist()
def calculate_distribution(docname):
    doc = frappe.get_doc("Electricity Billing Cycle", docname)

    if doc.status != "Draft":
        frappe.throw("Distribution already calculated.")

    if not doc.total_electricity_amount:
        frappe.throw("Total Electricity Amount is required.")

    doc.set("electricity_distribution", [])

    agreements = frappe.get_all(
        "Agreement",
        filters={
            "property": doc.property,
            "status": "Active"
        },
        fields=["name", "room"]
    )

    if not agreements:
        frappe.throw("No active agreements found for this property.")

    total_area = 0
    rows = []

    for ag in agreements:
        room_area = frappe.db.get_value(
            "Room",
            ag.room,
            "room_size"
        )

        if not room_area:
            frappe.throw(f"Room size is missing for Room {ag.room}")

        total_area += room_area

        rows.append({
            "agreement": ag.name,
            "room": ag.room,
            "room_area": room_area
        })

    doc.total_property_area_sqft = total_area
    if total_area <= 0:
        frappe.throw("Total room area is zero. Please fill room size for all rooms.")

    rate_per_sqft = doc.total_electricity_amount / total_area

    for row in rows:
        doc.append("electricity_distribution", {
            "agreement": row["agreement"],
            "room": row["room"],
            "room_area": row["room_area"],
            "calculated_amount": round(row["room_area"] * rate_per_sqft, 2),
            "period_start": doc.billing_month,
            "mode_of_payment": "Cash" ,
            "remark": "Electricity Bill",
        })

    doc.status = "Calculated"
    doc.save()


@frappe.whitelist()
def generate_electricity_charges(docname):
    doc = frappe.get_doc("Electricity Billing Cycle", docname)

    if doc.status != "Calculated":
        frappe.throw("Electricity charges already generated.")

    for row in doc.electricity_distribution:
        # 🔹 Get next idx safely
        max_idx = frappe.db.sql(
            """
            SELECT IFNULL(MAX(idx), 0)
            FROM `tabAgreement Payment Schedule`
            WHERE parent = %s
            """,
            row.agreement
        )[0][0]

        next_idx = max_idx + 1

        ps = frappe.get_doc({
            "doctype": "Agreement Payment Schedule",
            "parent": row.agreement,
            "parenttype": "Agreement",
            "parentfield": "payment_schedule",
            "idx": next_idx,                      # ✅ FIX
            "period_start": row.period_start,
            "amount": row.calculated_amount,
            "mode_of_payment": row.mode_of_payment,
            "hold_remark": row.remark,
            "status": "Draft"
        })

        ps.insert(ignore_permissions=True)

    doc.status = "Billed"
    doc.save(ignore_permissions=True)

import frappe

@frappe.whitelist()
def generate_key_money(agreement):
    ag = frappe.get_doc("Agreement", agreement)

    if ag.key_money_status != "Draft":
        frappe.throw("Key Money already generated.")

    if not ag.key_money_amount or ag.key_money_amount <= 0:
        frappe.throw("Key Money amount is required.")

    # 🔹 Get next idx safely
    max_idx = frappe.db.sql(
        """
        SELECT IFNULL(MAX(idx), 0)
        FROM `tabAgreement Payment Schedule`
        WHERE parent = %s
        """,
        agreement
    )[0][0]

    ps = frappe.get_doc({
        "doctype": "Agreement Payment Schedule",
        "parent": agreement,
        "parenttype": "Agreement",
        "parentfield": "payment_schedule",
        "idx": max_idx + 1,
        "period_start": ag.start_date,
        "amount": ag.key_money_amount,
        "mode_of_payment": "Cash",
        "hold_remark": "Key Money",
        "status": "Draft"
    })

    ps.insert(ignore_permissions=True)

    ag.db_set("key_money_status", "Billed")

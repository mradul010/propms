import frappe
from frappe import _
from frappe.utils import flt

@frappe.whitelist()
def create_item_for_room(room_name):
    if not room_name:
        return

    room = frappe.get_doc("Room", room_name)

    if not room.rent_amount or flt(room.rent_amount) <= 0:
        return

    item_code = room.name

    # Do not recreate if item already exists
    if frappe.db.exists("Item", item_code):
        return

    # Create Item
    item = frappe.get_doc({
        "doctype": "Item",
        "item_code": item_code,
        "item_name": item_code,
        "item_group": "Property",
        "stock_uom": "Nos",
        "is_stock_item": 0,
        "include_item_in_manufacturing": 0,
        "disabled": 0
    })

    item.insert(ignore_permissions=True)

    # Create Item Price (Standard ERPNext way)
    price = frappe.get_doc({
        "doctype": "Item Price",
        "item_code": item_code,
        "price_list": "Standard Selling",
        "price_list_rate": flt(room.rent_amount)
    })

    price.insert(ignore_permissions=True)

    frappe.db.commit()

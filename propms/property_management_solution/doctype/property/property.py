# -*- coding: utf-8 -*-
# Copyright (c) 2018, Aakvatech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.utils.nestedset import NestedSet
import frappe


class Property(NestedSet):
    nsm_parent_field = "parent_property"

    def on_trash(self, allow_root_deletion=True):
        super().on_trash(allow_root_deletion)
        
    def validate(self):
        self.update_room_counts()

    def update_room_counts(self):
        total = 0
        occupied = 0

        for row in self.room_details or []:
            total += 1
            if not row.is_available:
                occupied += 1

        self.total_rooms = total
        self.occupied_rooms = occupied

@frappe.whitelist()
def add_node():
    from frappe.desk.treeview import make_tree_args

    args = frappe.form_dict
    args = make_tree_args(**frappe.form_dict)

    if args["is_root"]:
        args["parent_property"] = None

    doc = frappe.get_doc(args)

    doc.save()

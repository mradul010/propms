// Copyright (c) 2025, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Room", {
  refresh: function (frm) {
    frm.trigger("sync_status_with_availability");
  },

  is_available: function (frm) {
    frm.trigger("sync_status_with_availability");
  },

  room_status: function (frm) {
    frm.trigger("sync_status_with_availability");
  },

  sync_status_with_availability: function (frm) {
    if (frm.doc.is_available) {
      if (frm.doc.room_status !== "Available") {
        frm.set_value("room_status", "Available");
      }
    } else {
      // if unchecked, force status away from "Available"
      if (frm.doc.room_status === "Available") {
        frm.set_value("room_status", "Occupied"); // 👈 default fallback
      }
    }
  },
});

frappe.ui.form.on("Room", {
  after_save(frm) {
    if (!frm.doc.name || !frm.doc.rent_amount) return;

    frappe.call({
      method: "propms.api.room.create_item_for_room",
      args: {
        room_name: frm.doc.name,
      },
      freeze: false,
    });
  },
});

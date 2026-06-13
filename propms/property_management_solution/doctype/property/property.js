// Copyright (c) 2018, Aakvatech and contributors
// For license information, please see license.txt

frappe.ui.form.on("Property", {
	refresh: function (frm) {
		frm.trigger("update_room_counts");
	},

	update_room_counts: function (frm) {
		let total = 0;
		let occupied = 0;

		(frm.doc.room_details || []).forEach(row => {
			total++;
			if (!row.is_available) {
				occupied++;
			}
		});

		frm.set_value("total_rooms", total);
		frm.set_value("occupied_rooms", occupied);
	}
});

// Trigger whenever room_details changes
frappe.ui.form.on("Room Items", {
	is_available: function (frm, cdt, cdn) {
		frm.trigger("update_room_counts");
	},
	room_name: function (frm, cdt, cdn) { // or any other field you want
		frm.trigger("update_room_counts");
	},
	room_items_add: function (frm, cdt, cdn) {
		frm.trigger("update_room_counts");
	},
	room_items_remove: function (frm, cdt, cdn) {
		frm.trigger("update_room_counts");
	},
	room_details_add: function (frm, cdt, cdn) {
		let row = frappe.get_doc(cdt, cdn);
		if (frm.doc.property_code) {
			row.property_code = frm.doc.property_code;
			frm.refresh_field("room_details");
		}
	}
});




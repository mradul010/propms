frappe.ui.form.on("Electricity Billing Cycle", {
  refresh(frm) {
    if (frm.doc.status === "Draft" && frm.doc.total_electricity_amount) {
      frm.add_custom_button("Calculate Distribution", () => {
        frappe.call({
          method: "propms.api.electricity.calculate_distribution",
          args: {
            docname: frm.doc.name,
          },
          callback() {
            frm.reload_doc();
          },
        });
      });
    }

    if (frm.doc.status === "Calculated") {
      frm.add_custom_button("Generate Electricity Charges", () => {
        frappe.call({
          method: "propms.api.electricity.generate_electricity_charges",
          args: {
            docname: frm.doc.name,
          },
          callback() {
            frm.reload_doc();
          },
        });
      });
    }
  },
});

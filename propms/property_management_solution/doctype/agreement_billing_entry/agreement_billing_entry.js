frappe.ui.form.on("Agreement Billing Entry", {
  refresh: function (frm) {
    if (frm.doc.__islocal) return;

    if (["Pending", "Sent", "Overdue"].includes(frm.doc.status)) {
      // Send Email
      frm.add_custom_button("Send Email", function () {
        frappe.call({
          method: "propms.api.billing.send_billing_entry",
          args: { docname: frm.doc.name },
          callback: function () {
            frappe.msgprint("Billing Entry Sent Successfully");
            frm.reload_doc();
          },
        });
      });

      // Paid Button
      frm.add_custom_button("Paid", function () {
        frappe.confirm(
          "This will create Sales Invoice and Payment Entry. Continue?",
          function () {
            frm.disable_save();

            frappe.call({
              method: "propms.api.billing.pay_billing_entry_with_invoice",
              args: {
                billing_entry_name: frm.doc.name,
              },
              freeze: true,
              freeze_message: "Processing Payment...",
              callback: function (r) {
                if (!r.exc) {
                  frappe.msgprint(
                    `<b>Sales Invoice:</b> ${r.message.sales_invoice}<br>
               <b>Payment Entry:</b> ${r.message.payment_entry}`
                  );
                  frm.reload_doc();
                }
              },
              always: function () {
                frm.enable_save();
              },
            });
          }
        );
      });
    }
  },
});

frappe.ui.form.on("Agreement Billing Entry", {
  refresh(frm) {
    if (frm.is_new()) return;

    // Show only for paid cheque entries
    if (
      frm.doc.mode_of_payment === "Cheque" &&
      frm.doc.status === "Paid" &&
      frm.doc.payment_entry
    ) {
      frm.add_custom_button("Mark Cheque as Bounced", () => {
        frappe.confirm(
          "This will cancel the Payment Entry and mark the cheque as bounced. Continue?",
          () => {
            frappe.call({
              method: "propms.api.billing.mark_cheque_bounced",
              args: {
                billing_entry: frm.doc.name,
              },
              freeze_message: "Processing cheque bounce...",
              callback: function (r) {
                if (!r.exc) {
                  frappe.msgprint({
                    title: "Cheque Bounced",
                    indicator: "orange",
                    message: r.message,
                  });
                  frm.reload_doc();
                }
              },
            });
          }
        );
      });
    }
  },
});

// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Navari eTims Registered Stock Movement", {
  refresh: function (frm) {
    frm.add_custom_button(
      __("Create Stock Entry"),
      function () {
        frappe.call({
          method:
            "kenya_compliance.kenya_compliance.apis.apis.create_stock_entry_from_stock_movement",
          args: {
            request_data: {
              name: frm.doc.name,
              branch_id: frm.doc.customer_branch_id,
              items: frm.doc.items,
            },
          },
          callback: (response) => {},
          error: (error) => {
            // Error Handling is Defered to the Server
          },
        });
      },
      __("eTims Actions")
    );
  },
});

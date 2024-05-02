// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

const doctypeName = "Navari eTims User";

frappe.ui.form.on(doctypeName, {
  refresh: async function (frm) {
    const companyName = frappe.boot.sysdefaults.company;

    if (!frm.is_new()) {
      frm.add_custom_button(
        __("Submit Branch User Details"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.save_branch_user_details",
            args: {
              request_data: {
                name: frm.doc.name,
                company_name: companyName,
                user_id: frm.doc.user_id,
                branch_id: frm.doc.custom_etims_branch_id,
                registration_id: frm.doc.owner,
                modifier_id: frm.doc.modified_by,
              },
            },
            callback: (response) => {
              frappe.msgprint("Request queued. Please check in later.");
            },
            error: (r) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );
    }
  },
});

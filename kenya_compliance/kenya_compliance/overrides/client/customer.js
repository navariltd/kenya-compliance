const doctype = "Customer";

frappe.ui.form.on(doctype, {
  refresh: async function (frm) {
    const companyName = frappe.boot.sysdefaults.company;

    if (!frm.is_new() && frm.doc.tax_id) {
      frm.add_custom_button(
        __("Perform Customer Search"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.perform_customer_search",
            args: {
              request_data: {
                name: frm.doc.name,
                tax_id: frm.doc.tax_id,
                company_name: companyName,
              },
            },
            callback: (response) => {
              frappe.msgprint("Search queued. Please check in later.");
            },
            error: (r) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );

      if (!frm.doc.custom_details_submitted_successfully) {
        frm.add_custom_button(
          __("Send Customer Details"),
          function () {
            frappe.call({
              method:
                "kenya_compliance.kenya_compliance.apis.apis.send_branch_customer_details",
              args: {
                request_data: {
                  name: frm.doc.name,
                  customer_pin: frm.doc.tax_id,
                  customer_name: frm.doc.customer_name,
                  company_name: companyName,
                  registration_id: frm.doc.owner,
                  modifier_id: frm.doc.modified_by,
                },
              },
              callback: (response) => {},
              error: (r) => {
                // Error Handling is Defered to the Server
              },
            });
          },
          __("eTims Actions")
        );
      }
    }

    if (
      frm.doc.custom_insurance_applicable &&
      !frm.doc.custom_insurance_details_submitted_successfully
    ) {
      frm.add_custom_button(
        __("Send Insurance Details"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.send_insurance_details",
            args: {
              request_data: {
                name: frm.doc.name,
                tax_id: frm.doc.tax_id,
                company_name: companyName,
                insurance_code: frm.doc.custom_insurance_code,
                insurance_name: frm.doc.custom_insurance_name,
                premium_rate: frm.doc.custom_premium_rate,
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

    // frm.fields_dict.items.grid.get_field("item_classification_code").get_query =
    //   function (doc, cdt, cdn) {
    //     // Adds a filter to the items item classification code based on item's description
    //     const itemDescription = locals[cdt][cdn].description;
    //     const descriptionText = parseItemDescriptionText(itemDescription);

    //     return {
    //       filters: [
    //         [
    //           "Navari KRA eTims Item Classification",
    //           "itemclsnm",
    //           "like",
    //           `%${descriptionText}%`,
    //         ],
    //       ],
    //     };
    //   };
  },
  customer_group: function (frm) {
    frappe.db.get_value(
      "Customer Group",
      {
        name: frm.doc.customer_group,
      },
      ["custom_insurance_applicable"],
      (response) => {
        const customerGroupInsuranceApplicable =
          response.custom_insurance_applicable;

        if (customerGroupInsuranceApplicable) {
          frappe.msgprint(
            `The Customer Group ${frm.doc.customer_group} has Insurance Applicable on. Please fill the relevant insurance fields under Tax tab`
          );
          frm.toggle_reqd("custom_insurance_code", true);
          frm.toggle_reqd("custom_insurance_name", true);
          frm.toggle_reqd("custom_premium_rate", true);

          frm.set_value("custom_insurance_applicable", 1);
        } else {
          frm.toggle_reqd("custom_insurance_code", false);
          frm.toggle_reqd("custom_insurance_name", false);
          frm.toggle_reqd("custom_premium_rate", false);

          frm.set_value("custom_insurance_applicable", 0);
        }
      }
    );
  },
});

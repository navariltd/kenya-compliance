const doctype = "Customer";

frappe.ui.form.on(doctype, {
  refresh: async function (frm) {
    if (!frm.is_new() && frm.doc.tax_id) {
      const companyName = frappe.boot.sysdefaults.company;
      const companyTaxIdResponse = await frappe.db.get_value(
        "Company",
        { name: frappe.boot.sysdefaults.company },
        ["tax_id"]
      );
      let companyTaxId = null;

      if (companyTaxIdResponse) {
        companyTaxId = companyTaxIdResponse.message?.tax_id;
      }

      frm.add_custom_button(
        __("Perform Customer Search"),
        function () {
          // call with all options
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.api.apis.perform_customer_search",
            args: {
              request_data: {
                document: frm.doc,
                company_tax_id: companyTaxId,
              },
            },
            callback: (r) => {
              // TODO: Apply an appropriate success handling strategy
              frappe.msgprint("Succeeded");
            },
            error: (r) => {
              // TODO: Apply an appropriate error handling strategy
            },
          });
        },
        __("eTims Actions")
      );
    }
    frm.fields_dict.items.grid.get_field("item_classification_code").get_query =
      function (doc, cdt, cdn) {
        // Adds a filter to the items item classification code based on item's description
        const itemDescription = locals[cdt][cdn].description;
        const descriptionText = parseItemDescriptionText(itemDescription);

        return {
          filters: [
            [
              "Navari KRA eTims Item Classification",
              "itemclsnm",
              "like",
              `%${descriptionText}%`,
            ],
          ],
        };
      };
  },
});

const doctype = "Customer";

frappe.ui.form.on(doctype, {
  refresh: async function (frm) {
    if (!frm.is_new() && frm.doc.tax_id) {
      const companyName = frappe.boot.sysdefaults.company;

      frm.add_custom_button(
        __("Perform Customer Search"),
        function () {
          // call with all options
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
              const customerSearchDetails = response?.message?.custList[0];
              frappe.msgprint("Search queued. Please check in later.");

              updateCustomerTaxDetails(frm, customerSearchDetails);
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
});

function updateCustomerTaxDetails(frm, customerSearchDetails) {
  frm.set_value("custom_is_validated", "1");
  frm.set_value("custom_tax_payers_name", customerSearchDetails.taxprNm);
  frm.set_value("custom_tax_payers_status", customerSearchDetails.taxprSttsCd);
  frm.set_value("custom_county_name", customerSearchDetails.prvncNm);
  frm.set_value("custom_subcounty_name", customerSearchDetails.dstrtNm);
  frm.set_value("custom_tax_locality_name", customerSearchDetails.sctrNm);
  frm.set_value("custom_location_name", customerSearchDetails.locDesc);
}

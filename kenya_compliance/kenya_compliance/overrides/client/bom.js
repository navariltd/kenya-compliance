const doctype = "BOM";

frappe.ui.form.on(doctype, {
  refresh: function (frm) {
    const companyName = frappe.boot.sysdefaults.company;
    let itemCode;
    frappe.db.get_value("Item", { name: frm.doc.item }, ["*"], (response) => {
      const series = frm.doc.idx.toString().padStart(7, 0);
      itemCode = `${response.custom_etims_country_of_origin_code}${response.custom_product_type}${response.custom_packaging_unit_code}${response.custom_unit_of_quantity_code}${series}`;

      console.log(response.custom_item_classification);
    });

    if (!frm.is_new()) {
      frm.add_custom_button(
        __("Submit Item Composition"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.submit_item_composition",
            args: {
              request_data: {
                name: frm.doc.name,
                company_name: companyName,
                item_name: frm.doc.item,
                quantity: frm.doc.quantity,
                registration_id: frm.doc.owner,
                item_code: itemCode,
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
  },
});

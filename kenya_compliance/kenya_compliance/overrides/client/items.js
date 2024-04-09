const itemDoctypName = "Item";

frappe.ui.form.on(itemDoctypName, {
  refresh: async function (frm) {
    const companyName = frappe.boot.sysdefaults.company;

    if (!frm.is_new()) {
      const series = frm.doc.idx.toString().padStart(7, 0);
      const itemCode = `${frm.doc.custom_etims_country_of_origin_code}${frm.doc.custom_product_type}${frm.doc.custom_packaging_unit_code}${frm.doc.custom_unit_of_quantity_code}${series}`;

      if (!frm.doc.custom_item_registered) {
        frm.add_custom_button(
          __("Register Item"),
          function () {
            // call with all options
            frappe.call({
              method:
                "kenya_compliance.kenya_compliance.apis.apis.perform_item_registration",
              args: {
                request_data: {
                  name: frm.doc.name,
                  company_name: companyName,
                  itemCd: itemCode,
                  itemClsCd: frm.doc.custom_item_classification,
                  itemTyCd: frm.doc.custom_product_type,
                  itemNm: frm.doc.item_name,
                  temStdNm: null,
                  orgnNatCd: "KE",
                  pkgUnitCd: frm.doc.custom_packaging_unit_code,
                  qtyUnitCd: frm.doc.custom_unit_of_quantity_code,
                  taxTyCd: "B" || frm.doc.custom_taxation_type,
                  btchNo: null,
                  bcd: null,
                  dftPrc: frm.doc.valuation_rate,
                  grpPrcL1: null,
                  grpPrcL2: null,
                  grpPrcL3: null,
                  grpPrcL4: null,
                  grpPrcL5: null,
                  addInfo: null,
                  sftyQty: null,
                  isrcAplcbYn: "Y",
                  useYn: "Y",
                  regrId: frm.doc.owner,
                  regrNm: frm.doc.owner,
                  modrId: frm.doc.modified_by,
                  modrNm: frm.doc.modified_by,
                },
              },
              callback: (response) => {
                frappe.msgprint(
                  "Item Registration Queued. Please check in later."
                );
              },
              error: (error) => {
                // Error Handling is Defered to the Server
              },
            });
          },
          __("eTims Actions")
        );
      }

      if (frm.doc.is_stock_item) {
        frm.add_custom_button(
          __("Submit Item Inventory"),
          function () {
            frappe.call({
              method:
                "kenya_compliance.kenya_compliance.apis.apis.submit_inventory",
              args: {
                request_data: {
                  company_name: companyName,
                  name: frm.doc.name,
                  itemName: frm.doc.item_code,
                  itemCd: itemCode,
                  registered_by: frm.doc.owner,
                  modified_by: frm.doc.modified_by,
                },
              },
              callback: (response) => {
                frappe.msgprint("Inventory submission queued.");
              },
              error: (error) => {
                // Error Handling is Defered to the Server
              },
            });
          },
          __("eTims Actions")
        );
      }
    }
  },
});

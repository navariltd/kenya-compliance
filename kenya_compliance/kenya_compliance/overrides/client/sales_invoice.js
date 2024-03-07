const doctype = "Sales Invoice";
const childDoctype = "Sales Invoice Item";

frappe.ui.form.on(doctype, {
  refresh: function (frm) {
    if (!frm.is_new() && frm.doc.tax_id) {
      frm.add_custom_button(
        __("Perform Customer Search"),
        function () {
          // call with all options
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.api.apis.perform_customer_search",
            args: {
              request_data: { document: frm.doc },
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
        __("KRA Actions")
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

function parseItemDescriptionText(description) {
  const temp = document.createElement("div");

  temp.innerHTML = description;
  const descriptionText = temp.textContent || temp.innerText;

  return descriptionText;
}

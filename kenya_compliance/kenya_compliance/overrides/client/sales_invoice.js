const doctype = "Sales Invoice";
const childDoctype = "Sales Invoice Item";

frappe.ui.form.on(doctype, {
  refresh: function (frm) {
    frm.fields_dict.items.grid.get_field("item_classification_code").get_query =
      function (doc, cdt, cdn) {
        const itemDescription = locals[cdt][cdn].description;
        const descriptionText = parseItemDescriptText(itemDescription);

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

frappe.ui.form.on(childDoctype, {
  item_classification_code: async function (frm, cdt, cdn) {
    const itemClassificationCode = locals[cdt][cdn].item_classification_code;

    if (itemClassificationCode) {
      const response = await frappe.db.get_value(
        "Navari KRA eTims Item Classification",
        { itemclscd: itemClassificationCode },
        ["*"]
      );

      frappe.model.set_value(
        cdt,
        cdn,
        "taxation_type",
        response.message?.taxtycd
      );
    }
  },
});

function parseItemDescriptText(description) {
  const temp = document.createElement("div");

  temp.innerHTML = description;
  const descriptionText = temp.textContent || temp.innerText;

  return descriptionText;
}

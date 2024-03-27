const doctypeName = "POS Invoice";
const childDoctypeName = `${doctypeName} Item`;

frappe.ui.form.on(childDoctypeName, {
  custom_item_classification: async function (frm, cdt, cdn) {
    const itemClassificationCode = locals[cdt][cdn].custom_item_classification;
  },
  custom_packaging_unit: async function (frm, cdt, cdn) {
    const packagingUnit = locals[cdt][cdn].custom_packaging_unit;

    if (packagingUnit) {
      const response = await frappe.db.get_value(
        packagingUnitDoctypeName,
        {
          name: packagingUnit,
        },
        ["code"]
      );

      const code = response.message?.code;
      locals[cdt][cdn].custom_packaging_unit_code = code;
      frm.refresh_field("custom_packaging_unit_code");
    }
  },
  custom_unit_of_quantity: async function (frm, cdt, cdn) {
    const unitOfQuantity = locals[cdt][cdn].custom_unit_of_quantity;

    if (unitOfQuantity) {
      const response = await frappe.db.get_value(
        unitOfQuantityDoctypeName,
        {
          name: unitOfQuantity,
        },
        ["code"]
      );

      const code = response.message?.code;
      locals[cdt][cdn].custom_unit_of_quantity_code = code;
      frm.refresh_field("custom_unit_of_quantity_code");
    }
  },
});

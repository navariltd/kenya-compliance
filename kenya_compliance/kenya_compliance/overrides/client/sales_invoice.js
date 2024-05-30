const parentDoctype = "Sales Invoice";
const childDoctype = `${parentDoctype} Item`;
const packagingUnitDoctypeName = "Navari eTims Packaging Unit";
const unitOfQuantityDoctypeName = "Navari eTims Unit of Quantity";
const taxationTypeDoctypeName = "Navari KRA eTims Taxation Type";

frappe.ui.form.on(childDoctype, {
  item_code: function (frm, cdt, cdn) {
    const item = locals[cdt][cdn].item_code;
    const taxationType = locals[cdt][cdn].custom_taxation_type;

    if (!taxationType) {
      frappe.db.get_value(
        "Item",
        { item_code: item },
        ["custom_taxation_type"],
        (response) => {
          locals[cdt][cdn].custom_taxation_type = response.custom_taxation_type;
          locals[cdt][cdn].custom_taxation_type_code =
            response.custom_taxation_type;
        }
      );
    }
  },
  custom_packaging_unit: async function (frm, cdt, cdn) {
    const packagingUnit = locals[cdt][cdn].custom_packaging_unit;

    if (packagingUnit) {
      frappe.db.get_value(
        packagingUnitDoctypeName,
        {
          name: packagingUnit,
        },
        ["code"],
        (response) => {
          const code = response.code;
          locals[cdt][cdn].custom_packaging_unit_code = code;
          frm.refresh_field("custom_packaging_unit_code");
        }
      );
    }
  },
  custom_unit_of_quantity: function (frm, cdt, cdn) {
    const unitOfQuantity = locals[cdt][cdn].custom_unit_of_quantity;

    if (unitOfQuantity) {
      frappe.db.get_value(
        unitOfQuantityDoctypeName,
        {
          name: unitOfQuantity,
        },
        ["code"],
        (response) => {
          const code = response.code;
          locals[cdt][cdn].custom_unit_of_quantity_code = code;
          frm.refresh_field("custom_unit_of_quantity_code");
        }
      );
    }
  },
});

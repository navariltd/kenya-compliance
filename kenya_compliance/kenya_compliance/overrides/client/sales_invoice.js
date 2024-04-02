const parentDoctype = "Sales Invoice";
const childDoctype = `${parentDoctype} Item`;
const packagingUnitDoctypeName = "Navari eTims Packaging Unit";
const unitOfQuantityDoctypeName = "Navari eTims Unit of Quantity";

frappe.ui.form.on(parentDoctype, {
  status: function (frm) {
    // const invoiceStatus = frm.doc.status;
    // if (invoiceStatus === "Credit Note Issued") {
    //   frm.set_value("custom_transaction_progres", "Credit Note Generated");
    // } else if (invoiceStatus === "Submitted") {
    //   frm.set_value("custom_transaction_progres", "Approved");
    // } else if (invoiceStatus === "Cancelled") {
    //   frm.set_value("custom_transaction_progres", "Cancelled");
    // } else if (invoiceStatus === "Draft") {
    //   frm.set_value("custom_transaction_progres", "Wait for Approval");
    // } else if (invoiceStatus === "Internal Transfer") {
    //   frm.set_value("custom_transaction_progres", "Transferred");
    // } else {
    //   frm.set_value("custom_transaction_progres", "Wait for Approval");
    // }
  },
});

frappe.ui.form.on(childDoctype, {
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

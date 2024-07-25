const doctypeName = "POS Invoice";
const childDoctypeName = `${doctypeName} Item`;
const packagingUnitDoctypeName = "Navari eTims Packaging Unit";
const unitOfQuantityDoctypeName = "Navari eTims Unit of Quantity";
const taxationTypeDoctypeName = "Navari KRA eTims Taxation Type";
const settingsDoctypeName = "Navari KRA eTims Settings";

frappe.ui.form.on(doctypeName, {
  refresh: function (frm) {
    frappe.db.get_value(
      settingsDoctypeName,
      {
        is_active: 1,
        bhfid: frm.doc.branch,
        company: frappe.defaults.get_user_default("Company"),
      },
      [
        "name",
        "company",
        "bhfid",
        "sales_payment_type",
        "sales_transaction_progress",
      ],
      (response) => {
        if (!frm.doc.custom_payment_type) {
          frm.set_value("custom_payment_type", response.sales_payment_type);
        }
        if (!frm.doc.custom_transaction_progres) {
          frm.set_value(
            "custom_transaction_progres",
            response.sales_transaction_progress
          );
        }
      }
    );
  },
});

frappe.ui.form.on(childDoctypeName, {
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
  custom_taxation_type: async function (frm, cdt, cdn) {
    const taxationType = locals[cdt][cdn].custom_taxation_type;

    if (taxationType) {
      const response = await frappe.db.get_value(
        taxationTypeDoctypeName,
        {
          name: taxationType,
        },
        ["cd"]
      );

      const code = response.message?.cd;
      locals[cdt][cdn].custom_taxation_type_code = code;
      frm.refresh_field("custom_taxation_type_code");
    }
  },
});

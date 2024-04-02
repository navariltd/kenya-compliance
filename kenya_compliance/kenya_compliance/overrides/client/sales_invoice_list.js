frappe.listview_settings["Sales Invoice"].onload = function (listview) {
  listview.page.add_action_item(__("Bulk Submit to eTims"), function () {
    submit_bulk_invoice(listview, "Sales Invoice");
  });
};

function submit_bulk_invoice(listview, doctype) {
  const selectedItems = listview.get_checked_items();

  frappe.call({
    method: "kenya_compliance.kenya_compliance.apis.apis.bulk_submit_invoices",
    args: {
      docs_list: selectedItems,
    },
    callback: (response) => {
      frappe.msgprint("Bulk submission queued.");
    },
    error: (r) => {
      // Error Handling is Defered to the Server
    },
  });
}

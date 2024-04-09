const doctypeName = "Item";

frappe.listview_settings[doctypeName].onload = function (listview) {
  const companyName = frappe.boot.sysdefaults.company;

  listview.page.add_inner_button(
    __("Search Registered Items"),
    function (listview) {
      frappe.call({
        method:
          "kenya_compliance.kenya_compliance.apis.apis.perform_item_search",
        args: {
          request_data: {
            company_name: companyName,
          },
        },
        callback: (response) => {
          frappe.msgprint("Search queued. Please check in later.");
        },
        error: (r) => {
          // Error Handling is Defered to the Server
        },
      });
    }
  );

  listview.page.add_inner_button(
    __("Search Registered Imported Items"),
    function (listview) {
      frappe.call({
        method:
          "kenya_compliance.kenya_compliance.apis.apis.perform_import_item_search",
        args: {
          request_data: {
            company_name: companyName,
          },
        },
        callback: (response) => {
          frappe.msgprint("Search queued. Please check in later.");
        },
        error: (r) => {
          // Error Handling is Defered to the Server
        },
      });
    }
  );

  listview.page.add_inner_button(
    __("Search Items Classification"),
    function (listview) {
      frappe.call({
        method:
          "kenya_compliance.kenya_compliance.apis.apis.perform_item_classification_search",
        args: {
          request_data: {
            company_name: companyName,
          },
        },
        callback: (response) => {
          frappe.msgprint("Search queued. Please check in later.");
        },
        error: (r) => {
          // Error Handling is Defered to the Server
        },
      });
    }
  );
};

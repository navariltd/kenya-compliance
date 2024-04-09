const doctypeName = "Purchase Invoice";

frappe.listview_settings[doctypeName].onload = function (listview) {
  const companyName = frappe.boot.sysdefaults.company;

  listview.page.add_inner_button(
    __("Search Registered Purchases"),
    function (listview) {
      frappe.call({
        method:
          "kenya_compliance.kenya_compliance.apis.apis.perform_purchases_search",
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

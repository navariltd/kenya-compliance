const doctypeName = "Customer";

frappe.listview_settings[doctypeName].onload = function (listview) {
  const companyName = frappe.boot.sysdefaults.company;

  listview.page.add_inner_button(
    __("Search Branch Requests"),
    function (listview) {
      frappe.call({
        method:
          "kenya_compliance.kenya_compliance.apis.apis.search_branch_request",
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

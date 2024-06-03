const doctypeName = "Branch";

frappe.listview_settings[doctypeName] = {
  onload: function (listview) {
    const companyName = frappe.boot.sysdefaults.company;

    listview.page.add_inner_button(__("Get Branches"), function (listview) {
      frappe.call({
        method:
          "kenya_compliance.kenya_compliance.apis.apis.search_branch_request",
        args: {
          request_data: {
            company_name: companyName,
          },
        },
        callback: (response) => {
          console.log("Request queued. Please check in later");
        },
        error: (error) => {
          // Error Handling is Defered to the Server
        },
      });
    });
  },
};

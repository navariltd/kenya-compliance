const doctypeName = "Navari eTims Registered Imported Item";

frappe.listview_settings[doctypeName] = {
  onload: function (listview) {
    const companyName = frappe.boot.sysdefaults.company;

    listview.page.add_inner_button(
      __("Get Imported Items"),
      function (listview) {
        frappe.call({
          method:
            "kenya_compliance.kenya_compliance.apis.apis.perform_import_item_search",
          args: {
            request_data: {
              company_name: companyName,
            },
          },
          callback: (response) => {},
          error: (error) => {
            // Error Handling is Defered to the Server
          },
        });
      }
    );
  },
};

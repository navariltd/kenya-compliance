// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Navari KRA eTims Settings", {
  refresh: function (frm) {
    if (!frm.is_new() && frm.doc.is_active) {
      frm.add_custom_button(
        __("Perform Notice Search"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.perform_notice_search",
            args: {
              request_data: {
                name: frm.doc.name,
                company: frm.doc.company,
                communication_key: frm.doc.communication_key,
                server_url: frm.doc.server_url,
                branch_id: frm.doc.bhfid,
                pin: frm.doc.tin,
              },
            },
            callback: (response) => {},
            error: (error) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );

      frm.add_custom_button(
        __("Perform Code Search"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.perform_code_search",
            args: {
              request_data: {
                name: frm.doc.name,
                company: frm.doc.company,
                communication_key: frm.doc.communication_key,
                server_url: frm.doc.server_url,
                branch_id: frm.doc.bhfid,
                pin: frm.doc.tin,
              },
            },
            callback: (response) => {},
            error: (error) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );

      frm.add_custom_button(
        __("Perform Stock Movements Search"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.perform_stock_movement_search",
            args: {
              request_data: {
                name: frm.doc.name,
                company: frm.doc.company,
                communication_key: frm.doc.communication_key,
                server_url: frm.doc.server_url,
                branch_id: frm.doc.bhfid,
                pin: frm.doc.tin,
              },
            },
            callback: (response) => {},
            error: (error) => {
              // Error Handling is Defered to the Server
            },
          });
        },
        __("eTims Actions")
      );
    }

    frm.add_custom_button(
      __("Check if eTims Servers are Online"),
      function () {
        frappe.call({
          method:
            "kenya_compliance.kenya_compliance.apis.apis.ping_server",
          args: {
            request_data: {
              server_url: frm.doc.server_url,
            },
          },
        });
      },
      __("eTims Actions")
    );
  },
  sandbox: function (frm) {
    const sandboxFieldValue = parseInt(frm.doc.sandbox);
    const sandboxServerUrl = "https://etims-api-sbx.kra.go.ke/etims-api";
    const productionServerUrl = "https://etims-api.kra.go.ke/etims-api";

    if (sandboxFieldValue === 1) {
      frm.set_value("env", "Sandbox");
      frm.set_value("server_url", sandboxServerUrl);
    } else {
      frm.set_value("env", "Production");
      frm.set_value("server_url", productionServerUrl);
    }
  },
});

// Copyright (c) 2024, Navari Ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on("Navari KRA eTims Settings", {
  refresh: function (frm) {
    const companyName = frappe.boot.sysdefaults.company;

    if (!frm.is_new() && frm.doc.is_active) {
      frm.add_custom_button(
        __("Get Notices"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.perform_notice_search",
            args: {
              request_data: {
                name: frm.doc.name,
                company_name: companyName,
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
        __("Get Codes"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.background_tasks.tasks.refresh_code_lists",
            args: {
              request_data: {
                name: frm.doc.name,
                company_name: companyName,
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
        __("Get Stock Movements"),
        function () {
          frappe.call({
            method:
              "kenya_compliance.kenya_compliance.apis.apis.perform_stock_movement_search",
            args: {
              request_data: {
                name: frm.doc.name,
                company_name: companyName,
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
      __("Ping Server"),
      function () {
        frappe.call({
          method: "kenya_compliance.kenya_compliance.apis.apis.ping_server",
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
  init_devc: function (frm) {
    if(frm.is_new()){
      if(frm.doc.init_devc){
        frm.get_field("communication_key").df.read_only = 0;
        frm.get_field("communication_key").df.reqd = 1;
        frm.refresh_field("communication_key");
      }else{
        frm.get_field("communication_key").df.read_only = 1;
        frm.get_field("communication_key").df.reqd = 0;
        frm.refresh_field("communication_key");
      }
    }
  }
});

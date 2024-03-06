# Kenya-Compliance

ERPNext KRA eTIMS Integration via Online Sales Control Unit (OSCU)

More details:

https://www.kra.go.ke/etims

https://www.kra.go.ke/images/publications/OSCU_Specification_Document_v2.0.pdf

## How to Install

To install the app in a [Frappe Bench](https://frappeframework.com/docs/user/en/bench) instance, run:

`bench get-app https://github.com/navariltd/kenya-compliance.git`

followed by:

`bench --site your.site.name.here install-app kenya_compliance`

To run tests, ensure Testing is enabled in the target site by running:

`bench --site your.site.name.here set-config allow_tests true`

followed by

`bench --site your.site.name.here run-tests --app kenya_compliance`

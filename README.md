# Kenya-Compliance

<a id="more_details"></a>

ERPNext KRA eTIMS Integration via Online Sales Control Unit (OSCU)

For more details:

https://www.kra.go.ke/etims

<a id="etims_official_documentation"></a>
https://www.kra.go.ke/images/publications/OSCU_Specification_Document_v2.0.pdf

## How to Install

To install the app, [Setup, Initialise, and run a Frappe Bench instance](https://frappeframework.com/docs/user/en/installation).

Once the instance is up and running, add the application to the environment by running the command below in an active Bench terminal:

`bench get-app https://github.com/navariltd/kenya-compliance.git`

followed by:

`bench --site <your.site.name.here> install-app kenya_compliance`

To run tests, ensure Testing is enabled in the target site by executing:

`bench --site <your.site.name.here> set-config allow_tests true`

followed by

`bench --site <your.site.name.here> run-tests --app kenya_compliance`

**NOTE**: Replace _<your.site.name.here>_ with the target site name.

## Key Features

The app includes features to enable you to submit Sales, Stock, Purchase, Insurance as well as Customer information to KRA's eTims Servers.

The following are the major doctypes included:

1. [Current Environment Identifier](#current_env_id)
2. [Environment Settings for single and/or multiple companies](#environment_settings)
3. [Routes Reference](#routes_reference)

The app also creates a Workspace that collates important doctypes.

### Current Environment Identifier

<a id="current_env_id"></a>

This doctype is used to provide a global identifier for the current environment, which will in turn influence whether communication will happen with the Sandbox or Production eTims servers that KRA has provided.

This is a Single doctype with only two possible values: _Sandbox or Production_.

**NOTE**: The option is applied globally to all users of the current ERPNext instance.

![Current Environment Identifier](/kenya_compliance/docs/images/current_environment_identifier.PNG)

### Environment Settings

<a id="environment_settings"></a>

This doctype aggregates all the settings, and credentials required for communication with the eTims Servers.

![Environment Settings](/kenya_compliance/docs/images/environment_settings.PNG)

The fields present include:

1. **Branch ID**: Acquired from KRA during registration for etims OSCU.
2. **Device Serial Number**: Acquired from KRA during registration for etims OSCU.
3. **Company**: This is a link to an existing company in the ERPNext instance. 4.**Sandbox Environment Check**: Marks the current settings record as associated with either the Sandbox or Production eTims server. Sandbox is used for testing while Production is for real-world cases. Make sure to choose the correct environment.
4. **is Active Check**: Marks the current settings record as the active one, in the event of multiple settings for the same company. Note you can only have one settings record as active for each unique combination of environment, company (and by extension company PIN), and branch Id.

**NOTE**: The company's PIN selected together with the Branch Id and Device Serial number are important in generating the communication key, which is in turn used for all subsequent communication with eTims servers.

![Environment Settings Next Tab](/kenya_compliance/docs/images/environment_settings_page_2.PNG)

The additional Settings tab offers options to customise the frequency of communication to the eTims Servers. Choosing hourly implies information will be batched, and sent on an hourly basis. Possible options include: _Immediately_, _Half-Hourly_, _Hourly_, and _Daily_

**NOTE**: The communication key is stored in this doctype, and it's fetched immediately one tries to save a record. If all information is valid, a valid key will be issued and stored which is used for all subsequent communication. If the key was not fetched, one cannot proceed to save the record as that will impose an inconsistent state upon the system. **The key is only issued once. In the event of loosing it, one has to liaise with KRA to regenerate a new key**.

### Routes Reference

<a id="routes_reference"></a>

![Routes Reference](/kenya_compliance/docs/images/routes_reference.PNG)

This doctype holds references to the endpoints provided by KRA for the various activities. Each endpoint has an associated last request date that is updated after each eTims response. For a comprehensive documentation on the various endpoints, see the [More Details](#etims_official_documentation) section at the beginning.

**NOTE**: The _URL Path Function_ field is used as the search parameter whenever an endpoint is retrieved.

## Customisations

The following are the customisations done in order for the ERPNext instance to interface with the eTims servers.

1. [Item Doctype](#item_doctype_customisations)
2. [Sales Invoice Doctype](#sales_invoice_doctype_customisations)
3. [POS Invoice Doctype](#pos_invoice_doctype_customisations)
4. [Customer Doctype](#customer_doctype_customisations)

### Item Doctype

<a id="item_doctype_customisations"></a>

![Item Doctype Customisations](/kenya_compliance/docs/images/item_etims_tab.PNG)

The **eTims Details tab** will be present for each item during and after loading of each item. The tab holds fields to various doctypes that allow one to classify each item according to the specifications provided by KRA.

**NOTE**: The information captured here is mandatory when sending sales information to the eTims servers.

The doctypes linked include:

1. **Item Classifications**: Item classifications as specified by KRA
2. **Packaging Unit**: Packaging units as specified by KRA, e.g. Jars, wooden box, etc.
3. **Unit of Quantity**: Units of Quantity as specified by KRA, e.g. kilo-gramme, grammes, etc.
4. **Product Type Code**: Product type as specified by KRA, e.g. finished product, raw materials, etc.
5. **Country of Origin**: The country of origin declared for the item.

The _eTims Action_ button is also present for items that have not been registered in the etims server (for the lifetime of the current instance), which are denoted by the _Item Registered?_ check field not being ticked. This is a read-only field that is updated only after successful Item registration.

### Customer Doctype

<a id="customer_doctype_customisations"></a>

![Customer Doctype Customisations](/kenya_compliance/docs/images/customer_doctype.PNG)

For customers, the customisations are domiciled in the Tax tab. Also present is the eTims Actions Button where one can perform _Customer Searches_ in the eTims Servers. Successful customer searches update read-only fields in the record and check the _Is Validated field_.

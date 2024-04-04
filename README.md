# Kenya-Compliance

<a id="more_details"></a>

This app works to integrate ERPNext with KRA's eTIMS via the Online Sales Control Unit (OSCU) to allow for the sharing of information with the revenue authority.

This integration allows the user to send and receive the required information after sales, and purchase transactions, updating inventory, and creating customers. The user can also register their information such as items to the eTims servers.

For more details about eTims:

<a id="etims_official_documentation"></a>

https://www.kra.go.ke/images/publications/OSCU_Specification_Document_v2.0.pdf

## Architectural Overview

<a id="architectural_overview"></a>

An overview of ERPNext's Architecture
![ERPNext Architectural Overview](/kenya_compliance/docs/images/erpnext_instance_architecture.PNG)

An overview of an ERPNext Instance's communication with the eTims servers
![Architectural Overview](/kenya_compliance/docs/images/architectural_overview.jpg)

Once the application is [installed](#installation) and [configured](#environment-settings) in an ERPNext instance, communication to the ETims servers takes place through background jobs executed by [Redis Queue](https://redis.com/glossary/redis-queue/). The eTims response Information is stored in the relevant [customised DocType's](#customisations) tables in the [site's database](https://frappeframework.com/docs/user/en/basics/sites).

## Key Features

The following are the key features of the application:

1. [Application Workspace](#workspace)
2. [Error Logs](#error_logs)
3. [Bulk submission of information](#bulk_submissions)
4. [Flexible setup and configuration](#flexible_setup_and_configuration)

### App Workspace

<a id="workspace"></a>

![App Workspace](/kenya_compliance/docs/images/workspace.PNG)

The workspace contains shortcuts to various documents of interest concerning eTims.

**NOTE**: The workspace may look different depending on when you install the app or due to future changes.

### Error Logs

<a id="error_logs"></a>

![Example Error Log](/kenya_compliance/docs/images/error_log.PNG)

Each request is logged in the Integration Request DocType. Any response errors are logged in the Error Log doctype. Additionally, logs are written and can also be accessed through the logs folder of the bench harbouring the running instance if the records in the Error Logs/Integration Request DocTypes are cleared.

### Bulk Submission of Information

<a id="bulk_submissions"></a>

![Bulk Submission of Records](/kenya_compliance/docs/images/bulk_submission.PNG)

Bulk submission of information is supported for relevant DocTypes.

### Flexible Setup and Configuration

<a id="flexible_setup_and_configuration"></a>

Check under the [Key Doctypes](#key_doctypes) section to learn how to setup and get running

## Key DocTypes

<a id="key_doctypes"></a>

The following are the key doctypes included:

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

For customers, the customisations are domiciled in the Tax tab. Also present is the eTims Actions Button where one can perform a _Customer Search_ in the eTims Servers. Successful customer searches update read-only fields in the same record and check the _Is Validated field_.

**NOTE**: Supplying the customer's KRA PIN is a pre-requisite to making the search.

### Sales Invoice

<a id="sales_invoice_doctype_customisations"></a>

![Sales Invoice Customisations](/kenya_compliance/docs/images/sales_invoice_details.PNG)

Customisations on the Sales Invoice are found under the eTims Details tab. The fields in the tab are:

1. **Payment Type**: A reference to the relevant payment type for the invoice record. This is a link field, with values fetched from KRA.
2. **Transaction Progress**: A reference to the relevant transaction progress for the invoice record. This is also a link field, with values also fetched from KRA.

Fields under the _eTims Response Details_ are values received as a response from eTims. These are read-only, and only updated after a successful response is received.

![Sales Invoice Items Customisations](/kenya_compliance/docs/images/sales_invoice_item_details.PNG)

For each item, the above fields are required in order to submit sales information to eTims. These information is fetched from the item data by default, but it can be edited on the sales invoice before submitting information.

**NOTE**: Submission of the data happens whenever one submits a sales invoice as a background job.

### POS Invoice

<a id="pos_invoice_doctype_customisations"></a>

POS Invoice customisations also reflect the changes such as Sales Invoice, with the same behavior for the items, as well as submission.

## How to Install

<a id="installation"></a>

### Manual Installation/Self Hosting

<a id="manual_installation"></a>

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

### FrappeCloud Installation

<a id="frappecloud_installation"></a>

Installing on [FrappeCloud](https://frappecloud.com/docs/introduction) can be achieved after setting up a Bench instance, and a site. The app can then be added using the _Add App_ button in the _App_ tab of the bench and referencing this repository by using the _Install from GitHub_ option if you are not able to search for the app.

### Summary of Integrated Endpoints

As development is still ongoing, not all endpoints have been fully integrated with. The table below lists the endpoints that are currently supported.

| Endpoint              |   Status   | [Documentation Section](#more_details) |
| :-------------------- | :--------: | -------------------------------------: |
| DeviceVerificationReq | Completely |                                3.3.1.1 |
| CodeSearchReq         | Completely |                                3.3.2.1 |
| CustSearchReq         | Completely |                                3.3.2.2 |
| NoticeSearchReq       |  Not Yet   |                                3.3.2.3 |
| ItemClsSearchReq      | Completely |                                3.3.3.1 |
| ItemSaveReq           | Completely |                                3.3.3.2 |
| ItemSearchReq         |  Not Yet   |                                3.3.3.3 |
| BhfSearchReq          |  Not Yet   |                                3.3.4.1 |
| BhfCustSaveReq        |  Not Yet   |                                3.3.4.2 |
| BhfUserSaveReq        |  Not Yet   |                                3.3.4.3 |
| BhfInsuranceSaveReq   |  Not Yet   |                                3.3.4.4 |
| ImportItemSearchReq   |  Not Yet   |                                3.3.5.1 |
| ImportItemUpdateReq   |  Not Yet   |                                3.3.5.2 |
| TrnsSalesSaveWrReq    | Completely |                                3.3.6.1 |
| TrnsPurchaseSalesReq  |  Not Yet   |                                3.3.7.1 |
| TrnsPurchaseSaveReq   |  Not Yet   |                                3.3.7.2 |
| StockMoveReq          | Completely |                                3.3.8.1 |
| StockIOSaveReq        | Completely |                                3.3.8.2 |
| StockMasterSaveReq    |  Not Yet   |                                3.3.8.2 |

To get a deeper understanding of the above endpoints, consult the [documentation provided by KRA](#more_details) in the beginning.

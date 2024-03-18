"""Maps doctype names defined and used in the app to variable names"""

from typing import Final

# Doctypes
COMMUNICATION_KEYS_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Communication Key"
SETTINGS_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Settings"
LAST_REQUEST_DATE_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Last Request Date"
ROUTES_TABLE_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Route Table"
ROUTES_TABLE_CHILD_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Route Table Item"
ITEM_CLASSIFICATIONS_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Item Classification"
TAXATION_TYPE_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Taxation Type"
PAYMENT_TYPE_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Payment Type"
TRANSACTION_PROGRESS_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Transaction Progress"
PACKAGING_UNIT_DOCTYPE_NAME: Final[str] = "Navari eTims Packaging Unit"
UNIT_OF_QUANTITY_DOCTYPE_NAME: Final[str] = "Navari eTims Unit of Quantity"
ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME: Final[str] = (
    "Navari KRA eTims Environment Identifier"
)
INTEGRATION_LOGS_DOCTYPE_NAME: Final[str] = "Navari KRA eTims Integration Log"

# Global Variables
SANDBOX_SERVER_URL: Final[str] = "https://etims-api-sbx.kra.go.ke/etims-api"
PRODUCTION_SERVER_URL: Final[str] = "https://etims-api.kra.go.ke/etims-api"

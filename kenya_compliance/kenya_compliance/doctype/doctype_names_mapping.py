"""Maps doctype names defined and used in the app to variable names"""

from typing import Final

# Doctypes
COMMUNICATION_KEYS_DOCTYPE_NAME: Final[str] = "KRA eTims Communication Keys Navari"
SETTINGS_DOCTYPE_NAME: Final[str] = "KRA eTims Settings Navari"
LAST_REQUEST_DATE_DOCTYPE_NAME: Final[str] = "KRA eTims Last Request Date Navari"
ROUTES_TABLE_DOCTYPE_NAME: Final[str] = "KRA eTims Routes Table Navari"
ROUTES_TABLE_CHILD_DOCTYPE_NAME: Final[str] = "KRA eTims Route Child Table"

# Global Variables
SANDBOX_SERVER_URL: Final[str] = "https://etims-api-sbx.kra.go.ke/etims-api"
PRODUCTION_SERVER_URL: Final[str] = "https://etims-api.kra.go.ke/etims-api"

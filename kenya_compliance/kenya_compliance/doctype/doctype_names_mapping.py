"""Maps doctype names defined and used in the app to variable names"""

from typing import Final

# Doctypes
COMMUNICATION_KEYS_DOCTYPE_NAME: Final[str] = "KRA eTims Communication Keys Navari"
SETTINGS_DOCTYPE_NAME: Final[str] = "KRA eTims Settings Navari"
LAST_REQUEST_DATE_DOCTYPE_NAME: Final[str] = "KRA eTims Last Request Date Navari"

# Global Variables
SANDBOX_SERVER_URL: Final[str] = "https://etims-api-sbx.kra.go.ke/etims-api"
PRODUCTION_SERVER_URL: Final[str] = "https://etims-api.kra.go.ke/etims-api"

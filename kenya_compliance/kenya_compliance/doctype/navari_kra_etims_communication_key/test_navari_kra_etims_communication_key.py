# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from ..doctype_names_mapping import COMMUNICATION_KEYS_DOCTYPE_NAME


class TestNavariKRAeTimsCommunicationKey(FrappeTestCase):
    """Test Cases"""

    def test_communication_key_length(self) -> None:
        """Tests cases of invalid communication key length"""
        with self.assertRaises(frappe.ValidationError):
            token = """
            1e15aa7ff0377b9e3d5d27a64ead0e2e998fe4fbf8ac207003a7411c9cc34cc9eb255bba556491c03a47f7ac6807844b2dd0030e456350e4e74e7b099ba574ef74af3db7578753d2956e91974002c5f057438e4798921c7dbfc5d53db00cd5510902e582f699fa2b0ba2df1425d8f38736bb4543354c562337def989d26cfdf27ad2063ea2440e23a08467fd7cc166a7a0a67940a7b3ba18ba19f5eda60bdbdac6c23d01fa50414ec26afe1e0b4a8adec9258615bad0d7f2d852578b94ba5e589ab1cc253c03d74e82aef9b6392976382c6dc7be47023c634fffce1097acb7273f2644c25f38badd36677b9b064e7b102561828020a37f443be47597ce0447fa
            """
            cmckey = frappe.get_doc(COMMUNICATION_KEYS_DOCTYPE_NAME)

            cmckey.cmckey = token
            cmckey.save()

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Frontware IoT module",
    "version": "1.0",
    "author": "Frontware International",
    "category": "Miscellanous",
    "depends": [
        "mail"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "views/device_type.xml",
        "views/device.xml",
        "views/menu.xml",

        "wizard/fwiot_device_create_wizard.xml",
        "wizard/fwiot_device_lock_wizard.xml",
        
        "models/beacon/setting_wizard.xml",

        "models/thermometer/device.xml",
        "models/thermometer/action_wizard.xml",
        "models/thermometer/setting_wizard.xml",

        "models/sniffer/device.xml",
        "models/sniffer/action_wizard.xml",
        "models/sniffer/setting_wizard.xml",

        "models/nfc_reader/device.xml",
        "models/nfc_reader/action_wizard.xml",
        "models/nfc_reader/setting_wizard.xml",

        "models/smoke_detector/device.xml",
        "models/smoke_detector/action_wizard.xml",
        "models/smoke_detector/setting_wizard.xml",
    ],
    "installable": True,
    "active": False,
    "website": "http://www.frontware.com",
    "description": """ 

Module Odoo to get FW IoT Data
============================================

feature:

    - device

    - devie type


change log:
------------------------------------
* 2021-10-04 KPO (1.0) created

""",
}

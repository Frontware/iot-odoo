# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Frontware IoT module",
    "version": "1.0",
    "author": "Frontware International",
    "category": "Miscellanous",
    "depends": [
        "mail","hr"
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",

        "views/device_type.xml",
        "views/device_alert.xml",
        "views/device.xml",
        "views/menu.xml",
        "views/device_status.xml",

        "views/employee.xml",

        "wizard/fwiot_device_create_wizard.xml",
        "wizard/fwiot_device_lock_wizard.xml",
        "wizard/fwiot_device_cron_wizard.xml",
        
        "models/devices/beacon/setting_wizard.xml",

        "models/devices/thermometer/device.xml",
        "models/devices/thermometer/setting_wizard.xml",

        "models/devices/scanner/device.xml",
        "models/devices/scanner/setting_wizard.xml",

        "models/devices/sniffer/device.xml",
        "models/devices/sniffer/setting_wizard.xml",

        "models/devices/nfc_reader/device.xml",
        "models/devices/nfc_reader/setting_wizard.xml",

        "models/devices/smoke_detector/device.xml",
        "models/devices/smoke_detector/setting_wizard.xml",

        "models/devices/nfc_reader/cron.xml",
        "models/devices/scanner/cron.xml",
        "models/devices/smoke_detector/cron.xml",
        "models/devices/sniffer/cron.xml",
        "models/devices/thermometer/cron.xml",
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

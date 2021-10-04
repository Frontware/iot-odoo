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

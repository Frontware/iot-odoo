# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceThermoHumidSettingWizard(models.TransientModel):
    _name = 'fwiot_device_remote_433_setting_wizard'
    _inherit = 'fwiot_device_generic_setting_wizard'
    _description = 'Frontware IOT device: show remote 433 setting'
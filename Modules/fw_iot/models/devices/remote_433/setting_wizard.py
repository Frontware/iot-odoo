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

    mode = [('button','Button'),
            ('door_sensor','Dorr sensor')]

    pin_4 = fields.Selection(mode,string='Pin 4 type')
    pin_5 = fields.Selection(mode,string='Pin 5 type')

    def get_action_data(self):
        return {
            "pin_4": self.pin_4,
            "pin_5": self.pin_5,
        }

    def save_setting(self, data):
        """
        save current setting
        """
        self.create({
            "pin_4": data.get('pin_4', False),
            "pin_5": data.get('pin_5', False),
        })                
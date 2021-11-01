# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceThermoHumidSettingWizard(models.TransientModel):
    _name = 'fwiot_device_thermo_humidity_setting_wizard'
    _inherit = 'fwiot_device_generic_setting_wizard'
    _description = 'Frontware IOT device: show thermometer-humidity setting'

    delay = fields.Integer(string='Delay (sec)', help='number of seconds between 2 temperatures scan')
    deep_sleep = fields.Boolean(string='Deep sleep', help='if set to true then the board is set to deep sleep mode between 2 scans. Useful when use witn battery. Delay should be at least 5 minutes long.')

    @api.onchange('deep_sleep', 'delay')
    def when_change_delay(self):
        if self.deep_sleep:
           if self.delay < 300:
              self.delay = 300  

    def get_action_data(self):
        return {
            "delay": self.delay,
            "deep_sleep": self.deep_sleep,
        }

    def save_setting(self, data):
        """
        save current setting
        """
        self.create({
            "delay": data.get('delay', 0),
            "deep_sleep": data.get('deep_sleep', False),
        })                
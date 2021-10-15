# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceSmokeSettingWizard(models.TransientModel):
    _name = 'fwiot_device_smoke_detector_setting_wizard'
    _inherit = 'fwiot_device_generic_setting_wizard'
    _description = 'Frontware IOT device: show smoke_detector setting'

    delay = fields.Integer(string='Delay (sec)', help='the number of seconds between 2 stay alive mqtt ping, minimum = 15 secs')
    deep_sleep = fields.Boolean(string='Deep sleep', help='if set to true then the board is set to deep sleep mode. if set to false then device is OFF until smoke is detected.')

    @api.onchange('delay')
    def when_change_delay(self):
        if self.delay < 15:
           self.delay = 15  

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
            "deep_sleep": data.get('deep_sleep', False),
            "delay": data.get('delay', 0),
        })        
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceThermoSettingWizard(models.TransientModel):
    _name = 'fwiot_device_thermo_setting_wizard'
    _inherit = 'fwiot_device_generic_setting_wizard'
    _description = 'Frontware IOT device: show thermometer setting'

    delay = fields.Integer(string='Delay (sec)', help='number of seconds between 2 temperatures scan')
    deep_sleep = fields.Boolean(string='Deep sleep', help='if set to true then the board is set to deep sleep mode between 2 scans. Useful when use witn battery. Delay should be at least 5 minutes long.')
    resolution = fields.Selection([
        ('9','1 digit precision'),
        ('10','2 digit precision'),
        ('11','3 digit precision'),
        ('12','4 digit precision'),
    ],string='Resolution')

    @api.onchange('deep_sleep', 'delay')
    def when_change_delay(self):
        if self.deep_sleep:
           if self.delay < 300:
              self.delay = 300  

    def get_action_data(self):
        return {
            "delay": self.delay,
            "deep_sleep": self.deep_sleep,
            "resolution": int(self.resolution),
        }

    def save_setting(self, data):
        """
        save current setting
        """
        r = data.get('resolution', 9)
        if not r in [9, 10, 11, 12]:
           r = 9 
        self.create({
            "delay": data.get('delay', 0),
            "deep_sleep": data.get('deep_sleep', False),
            "resolution": '%s' % r,
        })                
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceThermoSettingWizard(models.TransientModel):
    _name = 'fwiot_device_thermo_setting_wizard'
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

    def action_update(self):
        """
        update setting
        """        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "delay": self.delay,
            "deep_sleep": self.deep_sleep,
            "resolution": int(self.resolution),
        }

        resp = requests.post(self.env.context.get('code'), headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Error while send new settings to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Error while send new settings to device : %s' % j.get('error', 'Unexpected error')))  

        return
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceSmokeSettingWizard(models.TransientModel):
    _name = 'fwiot_device_smoke_detector_setting_wizard'
    _description = 'show smoke_detector setting'

    delay = fields.Integer(string='Delay (sec)', help='the number of seconds between 2 stay alive mqtt ping, minimum = 15 secs')
    deep_sleep = fields.Boolean(string='Deep sleep', help='if set to true then the board is set to deep sleep mode. if set to false then device is OFF until smoke is detected.')

    @api.onchange('delay')
    def when_change_delay(self):
        if self.delay < 15:
           self.delay = 15  

    def action_update(self):
        """
        update setting
        """        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "delay": self.delay,
            "deep_sleep": self.deep_sleep,
        }

        resp = requests.post(self.env.context.get('code'), headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Erro while send new settings to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Erro while send new settings to device : %s' % j.get('error', 'Unexpected error')))  

        return
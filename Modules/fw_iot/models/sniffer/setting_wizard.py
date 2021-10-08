# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceSnifferSettingWizard(models.TransientModel):
    _name = 'fwiot_device_sniffer_setting_wizard'
    _description = 'show sniffer setting'

    scan_delay = fields.Integer(string='Scan delay', help='time in seconds between 2 scans.')
    deep_sleep = fields.Boolean(string='Deep sleep', help='if set to true then board goes to deep sleep mode between 2 scans. Useful when use with battery. scan_delay should be at least 5 minutes.')
    macs = fields.Text(string="Only MAC",help='list of mac addresses we want to report. If empty then we report all mac addresses.')
    exclude = fields.Text(string="Exclude MAC",help='list of mac don\'t have to report. exclude is ignored if macs is present in json.')

    @api.onchange('scan_delay', 'deep_sleep')
    def when_change_delay(self):
        if self.deep_sleep:
           if self.scan_delay < 300:
              self.scan_delay = 300  

    def action_update(self):
        """
        update setting
        """        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "scan_delay": self.scan_delay,
            "deep_sleep": self.deep_sleep,
            "scan_bluetooth": self.scan_bluetooth,
            "macs": (self.macs or '').split("\r\n"),
            "exclude": (self.exclude or '').split("\r\n"),
        }

        resp = requests.post(self.env.context.get('code'), headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Error while send new settings to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Error while send new settings to device : %s' % j.get('error', 'Unexpected error')))  

        return
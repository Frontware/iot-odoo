# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceScannerSettingWizard(models.TransientModel):
    _name = 'fwiot_device_scanner_setting_wizard'
    _description = 'show scanner setting'

    scan_wifi = fields.Boolean(string='Scan wifi', default=True)
    scan_bluetooth = fields.Boolean(string='Scan bluetooth', default=True)
    scan_delay = fields.Integer(string='Scan delay', help='number of seconds between 2 scans. Ignored if scan_wifi and scan_bluetooth are false. Set to 120 seconds for any value < 30')
    macs = fields.Text(string="Only MAC",help='list of mac addresses we want to report. If empty then we report all mac addresses.')
    exclude = fields.Text(string="Exclude MAC",help='list of mac don\'t have to report. exclude is ignored if macs is present in json.')

    @api.onchange('scan_delay', 'scan_wifi', 'scan_bluetooth')
    def when_change_delay(self):
        if self.scan_bluetooth or self.scan_wifi:
           if self.scan_delay < 30:
              self.scan_delay = 120  
        if not (self.scan_bluetooth or self.scan_wifi):
           self.scan_delay = 0  

    def action_update(self):
        """
        update setting
        """        
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "scan_delay": self.scan_delay,
            "scan_wifi": self.scan_wifi,
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
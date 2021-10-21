# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceScannerSettingWizard(models.TransientModel):
    _name = 'fwiot_device_scanner_setting_wizard'
    _inherit = 'fwiot_device_generic_setting_wizard'
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

    def get_action_data(self):
        return {
            "scan_delay": self.scan_delay,
            "scan_wifi": self.scan_wifi,
            "scan_bluetooth": self.scan_bluetooth,
            "macs": (self.macs or '').split("\n"),
            "exclude": (self.exclude or '').split("\n"),
        }

    def save_setting(self, data):
        """
        save current setting
        """
        ls = ''
        for e in data.get('macs', []):
           if e:
              ls += e + '\n'
        es = ''
        for e in data.get('exclude', []):
           if e:
              es += e + '\n'
        self.create({
            "scan_wifi": data.get('scan_wifi', False),
            "scan_bluetooth": data.get('scan_bluetooth', False),
            "scan_delay": data.get('scan_delay', 0),
            "macs": ls,
            "exclude": es,
        })
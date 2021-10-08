# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceNFCReaderSettingWizard(models.TransientModel):
    _name = 'fwiot_device_nfc_reader_setting_wizard'
    _description = 'Frontware IOT: show nfc reader setting'

    delay = fields.Integer(string='Delay (sec)', help='minimum time between 2 scans of same tag. Default is 3 second. There is no delay between scans of 2 different tags.', default=3)
    beep = fields.Boolean(string='Play beep', help='play a beep when a RFID tag is read.')
    led = fields.Boolean(string='Switch LED on', help='switch LED on when RFID is read.')
    rfids = fields.Text(string='RFID list', help='if exists then it will send MQTT or Beep or Led only if scan an ID that is in the list. (max 100)')

    def action_update(self):
        """
        update setting
        """        
        ls = (self.rfids or '').split("\n")
        if len(ls) > 100:
           raise UserError('Maximum of RIFDs list is 100, current list number is %s' % len(ls))

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        data = {
            "delay": self.delay,
            "beep": self.beep,
            "led": self.led,
            "rfids": ls,
        }

        resp = requests.post(self.env.context.get('code'), headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Erro while send new settings to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Erro while send new settings to device : %s' % j.get('error', 'Unexpected error')))  

        return
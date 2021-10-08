# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import requests
from requests.structures import CaseInsensitiveDict

from odoo import models, _
from odoo.exceptions import UserError

class FWIOTDeviceSnifferActionWizard(models.TransientModel):
    _name = 'fwiot_device_sniffer_action_wizard'
    _description = 'show sniffer action'

    def _do_action(self, data):
        """
        do action and send @data
        """
        url = "https://iot.frontware.com/action/%s" % self.env.context.get('code')

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        resp = requests.post(url, headers=headers, data=json.dumps(data))

        if resp.status_code != 200:
           raise UserError(_('Erro while send action to device')) 

        j = json.loads(resp.content)
        
        if j.get('error',''):
           raise UserError(_('Erro while send action to device : %s' % j.get('error', 'Unexpected error')))  

        return

    def action_update(self):
        return self._do_action({"update": True}) 

    def action_restart(self):
        return self._do_action({"reboot": True}) 
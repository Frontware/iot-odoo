# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
import requests
import simplejson

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class FWIOTDeviceTGWizard(models.TransientModel):
    _name = 'fwiot_device_tg_wizard'
    _description = 'Frontware IOT: update chat id from telegram bot token'

    token = fields.Text(string="Bot token")
    alert_id = fields.Many2one('fwiot_device_alert',string="Device alert")

    def action_confirm(self):
        """
        read and get list of chat
        """                
        if not self.token:
           raise UserError(_('Must input Bot Token'))

        url = 'https://api.telegram.org/bot%s/getUpdates' % self.token
        r = requests.get(url)
        
        if r.status_code != 200:
           raise UserError(_('Error while try to get telegram update data'))
        
        if not r.content:
           raise UserError(_('Error while try to get telegram update data'))

        jj = simplejson.loads(r.content)
        if not jj.get('ok', False):
           raise UserError(_('Error while try to get telegram update data'))

        if not jj.get('result', False):
           raise UserError(_('Please connect at least 1 person to this bot'))

        self.alert_id.write({'tg_bot_token': self.token})

        tgc = self.env['fwiot_tg_chat']
        
        for c in jj.get('result', []):
            ch = c.get('message', {}).get('chat', {})
            if ch and ch.get('id', False):
               if not tgc.search([('chat_id','=', ch.get('id'))]).id:
                  tgc.create({
                      'name' : ' '.join([ch.get('first_name', ''),ch.get('last_name', '')]),
                      'chat_id': ch.get('id')
                  })  
        return
# -*- coding: utf-8 -*-
import requests
import urllib
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
class FWIOT_device_alert(models.Model):
    _name = 'fwiot_device_alert'
    _description = "Frontware IOT device alert trigger"
    _inherit = ['mail.thread']

    device_id = fields.Many2one('fwiot_device', string='Device', default=lambda self: self.env.context.get('device_id'))
    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active',default=True)

    condition_fields = fields.Selection(selection='_get_condition_fields', string="If")
    condition_type = fields.Selection([('!=', '<>'),
                                       ('==', '='),
                                       ('<', '<'),
                                       ('>', '>')
                                       ], string="operator")
    condition_value = fields.Char(string='compare value')
    condition_last_min = fields.Integer(string='last seen')

    message_type = fields.Selection([
        ('odoo','Email / Odoo Bot'),
        ('tg','Telegram')
    ],string='Message type')
    message = fields.Text(string='Message',translate=True)

    allow_partner_ids = fields.Many2many('res.partner', compute='_get_allow_partner',readonly=True,string="allowed partner",default=lambda self: self._get_allow_partners())

    odoo_recipient_ids = fields.Many2many('res.partner', string='To (Partners)',
        context={'active_test': False})

    tg_bot_token = fields.Text(compute='get_tg_bot_token',readonly=True,string='Telegram Bot Token',default=lambda self: self.get_tg_bot_token())
    tg_recipients = fields.Text(string='To (Telegram)')

    @api.depends('message_type')
    def _get_allow_partners(self):
        if self.message_type != 'odoo':
           return []

        return [x.partner_id.id for x in self.env['res.users'].search([
            ('active','=',True)])]

    def _get_allow_partner(self):
        """
        read current login's partner
        """
        pp = self._get_allow_partners()
        for each in self:
            each.allow_partner_ids = [(6, 0, pp)]
    
    @api.model
    def _get_condition_fields(self):
        tt = _('a device is not active for ')
        return self.env['fwiot_device'].get_condition_fields(self.env.context.get('device_id')) + \
               [('last_time', tt)] 

    def action_test(self):
        """
        test send message from odoo bot
        """
        self.ensure_one()
        if self.message_type == 'odoo':
           self.send_to_odoo([self.env.user.partner_id.id])
        elif self.message_type == 'tg':
           r = self.send_to_tg(self.tg_recipients)   
           if r:
              raise UserError(_('Error while send message to Telegram:\r\n %s') % r) 

    def parse_message(self):
        """
        parse message with condition value, device name
        """
        msg_dev = '%s (%s)' % (self.device_id.name, self.device_id.token)

        msg_con = self.condition_value
        if self.condition_fields == 'last_time':
           msg_con = '%s' % self.condition_last_min
        
        msg = self.env['ir.translation'].search([
            ('name', '=', 'fwiot_device_alert,message'),
            ('res_id', '=', self.id),
            ('lang', '=', 'en_US'),
        ]).value

        return (msg or self.message).replace('%value%', msg_con)\
                                   .replace('%device%', msg_dev)


    def send_to_odoo(self, partners):
        """
        send message to odoo (email/bot)
        """
        odoobot = self.env.ref('base.partner_root')        
        self.message_post(body=self.parse_message(), 
                          partner_ids=partners,author_id=odoobot.id)

    def send_to_tg(self, recipients):
        """
        send message to tg 
        @recipients text separate by enter
        """
        err = False
        if not recipients:
           err = _('no recipient') 
           return err

        ls = (recipients or '').split('\r\n')
        
        send_text = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text='
                
        for each in ls:
            response = requests.get(send_text % (
                    self.get_tg_bot_token(), each) +
                    urllib.parse.quote(self.parse_message())
                    )
            j_rp = response.json()
            if not j_rp.get('ok',False):
               err = j_rp.get('description', _('unexpected error'))
               return err
        
        return err               

    def get_tg_bot_token(self):
        """
        get tg bot token
        """
        tt = self.env["ir.config_parameter"].sudo().get_param("tg.bot-token")
        self.tg_bot_token = tt
        return tt
    
    def alert_record(self, value, field):
        tosend = False
        if field == 'last_time':
           min = (datetime.now() - self.device_id.last_online).total_seconds() / 60
           if self.condition_last_min < min:
              tosend = True 

        elif field == self.condition_fields:
           if type(value) == list:                               
              for l in value:
                  # found at least 1
                  print('"%s" %s "%s"' % (l, self.condition_type, self.condition_value))
                  chke = eval('"%s" %s "%s"' % (l, self.condition_type, self.condition_value))   
                  if chke:
                     tosend = chke
                     break

           elif type(value) != str:
              print('%s %s %s' % (value, self.condition_type, self.condition_value))
              tosend = eval('%s %s %s' % (value, self.condition_type, self.condition_value)) 
           else:
              print('"%s" %s "%s"' % (value, self.condition_type, self.condition_value))
              tosend = eval('"%s" %s "%s"' % (value, self.condition_type, self.condition_value))   

        if not tosend:
           return 

        if self.message_type == 'odoo':
           self.send_to_odoo([x.id for x in self.odoo_recipient_ids])

        elif self.message_type == 'tg':
           r = self.send_to_tg(self.tg_recipients)   
           if r:
              raise UserError(_('Error while send message to Telegram:\r\n %s') % r) 

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

    device_id = fields.Many2one('fwiot_device', string='Device',
                                default=lambda self: self.env.context.get('device_id'))
    device_image = fields.Image(related='device_id.image_1920', readonly=True)
    device_image_128 = fields.Image(
        related='device_id.image_128', readonly=True)
    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active', default=True)
    type = fields.Selection(
        [('in', 'In'), ('out', 'Out')], string='For', default='in')
    device_type_code = fields.Char(
        related='device_id.type.code', readonly=True)

    condition_fields = fields.Selection(
        selection='_get_condition_fields', string="If")
    condition_type = fields.Selection([('!=', '<>'),
                                       ('==', '='),
                                       ('<', '<'),
                                       ('>', '>')
                                       ], string="operator")
    condition_value = fields.Char(string='compare value')
    condition_last_min = fields.Integer(string='last seen')

    message_type = fields.Selection([
        ('odoo', 'Email / Odoo Bot'),
        ('tg', 'Telegram'),
        ('line', 'LINE'),
    ], string='Message type')
    message = fields.Text(string='Message', translate=True)

    allow_partner_ids = fields.Many2many('res.partner', compute='_get_allow_partner', readonly=True,
                                         string="allowed partner", default=lambda self: self._get_allow_partners())

    odoo_recipient_ids = fields.Many2many('res.partner', string='To (Partners)',
                                          context={'active_test': False})

    tg_bot_token = fields.Text(compute='get_tg_bot_token', readonly=True,
                               string='Telegram Bot Token', default=lambda self: self.get_tg_bot_token())
    tg_recipient_ids = fields.Many2many('hr.employee', 'fwiot_emp_tg', 'alert_id', 'employee_id',
                                        domain="[('telegram_id','!=',False)]", string='To (Telegram)', context={'active_test': False})

    line_recipient_ids = fields.Many2many('hr.employee', 'fwiot_emp_line', 'alert_id', 'employee_id',
                                          domain="[('line_token','!=',False)]", string='To (LINE)', context={'active_test': False})

    recipients = fields.Char(
        compute='_compute_recipients', string='To', readonly=True)

    @api.depends('message_type', 'odoo_recipient_ids', 'tg_recipient_ids', 'line_recipient_ids')
    @api.onchange('message_type', 'odoo_recipient_ids', 'tg_recipient_ids', 'line_recipient_ids')
    def _compute_recipients(self):
        for each in self:
            if each.message_type == 'odoo':
                each.recipients = ','.join(
                    [x.display_name for x in each.odoo_recipient_ids])
                if not each.odoo_recipient_ids:
                    each.active = False
            elif each.message_type == 'tg':
                each.recipients = ','.join(
                    [x.display_name for x in each.tg_recipient_ids])
                if not each.tg_recipient_ids:
                    each.active = False
            elif each.message_type == 'line':
                each.recipients = ','.join(
                    [x.display_name for x in each.line_recipient_ids])
                if not each.line_recipient_ids:
                    each.active = False

    @api.depends('message_type')
    def _get_allow_partners(self):
        if self.message_type != 'odoo':
            return []

        return [x.partner_id.id for x in self.env['res.users'].search([
            ('active', '=', True)])]

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
            self.send_to_odoo([self.env.user.partner_id.id],
                              self.parse_message())
        elif self.message_type == 'tg':
            r = self.send_to_tg(self.tg_recipient_ids, self.parse_message())
            if r:
                raise UserError(
                    _('Error while send message to Telegram:\r\n %s') % r)
        elif self.message_type == 'line':
            r = self.send_to_LINE(self.line_recipient_ids,
                                  self.parse_message())
            if r:
                raise UserError(
                    _('Error while send message to LINE:\r\n %s') % r)

    def parse_message(self, force_value=False):
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

        return (msg or self.message).replace('%value%', force_value or msg_con)\
                                    .replace('%device%', msg_dev)

    def send_to_odoo(self, partners, msg):
        """
        send message to odoo (email/bot)
        """
        odoobot = self.env.ref('base.partner_root')
        self.message_post(body=msg,
                          partner_ids=partners, author_id=odoobot.id)

    def send_to_tg(self, recipients, msg):
        """
        send message to tg 
        @recipients text separate by enter
        """
        err = False
        if not recipients:
            err = _('no recipient')
            return err

        send_text = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text='

        for each in recipients:
            if not each.telegram_id:
                continue
            response = requests.get(send_text % (
                self.get_tg_bot_token(), each.telegram_id) +
                urllib.parse.quote(msg)
            )
            j_rp = response.json()
            if not j_rp.get('ok', False):
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
        msg = self.parse_message(str(value or ''))
        if field == 'last_time':
            min = (datetime.now() - self.device_id.last_online).total_seconds() / 60
            if self.condition_last_min < min:
                tosend = True

                msg = self.parse_message(force_value=str(round(min)))

        elif field == self.condition_fields:
            if value and type(value) == list:
                for l in value:
                    msg = self.parse_message(str(l or ''))
                    # found at least 1
                    chke = eval('"%s" %s "%s"' %
                                (l, self.condition_type, self.condition_value))
                    if chke:
                        tosend = chke
                        break
            # when no value
            elif not value:
                # no value != any
                if self.condition_type == '!=':
                    tosend = True

            elif type(value) != str:
                tosend = eval('%s %s %s' % (
                    value, self.condition_type, self.condition_value))
            else:
                tosend = eval('"%s" %s "%s"' % (
                    value, self.condition_type, self.condition_value))

        if not tosend:
            return

        if self.message_type == 'odoo':
            self.send_to_odoo([x.id for x in self.odoo_recipient_ids], msg)

        elif self.message_type == 'tg':
            r = self.send_to_tg(self.tg_recipient_ids, msg)
            if r:
                raise UserError(
                    _('Error while send message to Telegram:\r\n %s') % r)

        elif self.message_type == 'line':
            r = self.send_to_LINE(self.line_recipient_ids, msg)
            if r:
                raise UserError(
                    _('Error while send message to LINE:\r\n %s') % r)

    def send_to_LINE(self, recipients, msg):
        """
        send message to LINE
        @recipients text separate by enter
        """
        err = False
        if not recipients:
            err = _('no recipient')
            return err

        for each in recipients:
            if not each.line_token:
                continue
            response = requests.post('https://notify-api.line.me/api/notify',
                                     headers={
                                         'content-type': 'application/x-www-form-urlencoded',
                                         'Authorization': 'Bearer ' + each.line_token
                                     }, data={
                                         'message': msg
                                     }
                                     )
            j_rp = response.json()
            if j_rp.get('message', False) != 'ok':
                err = j_rp.get('message', _('unexpected error'))
                return err

        return err

    @api.onchange('condition_last_min', 'condition_fields')
    def _onchange_last_min(self):
        f = self.condition_fields
        fv = self.condition_last_min
        if f == 'last_time':
            sch = self.device_id.get_schedule()
            sch_min = sch.interval_number
            if sch.interval_type == 'months':
                # 30 days
                sch_min = sch.interval_number * 60 * 24 * 30
            elif sch.interval_type == 'weeks':
                # 7 days
                sch_min = sch.interval_number * 60 * 24 * 7
            elif sch.interval_type == 'days':
                sch_min = sch.interval_number * 60 * 24
            elif sch.interval_type == 'hours':
                sch_min = sch.interval_number * 60
            elif sch.interval_type == 'minutes':
                pass
            if sch_min > fv:
                langdb = self.env['ir.translation']
                ft = self.env['ir.model.fields.selection'].search([
                    ('field_id.model', '=', 'ir.cron'),
                    ('field_id.name', '=', 'interval_type'),
                    ('value', '=', sch.interval_type),
                ])
                sch_t = langdb.search([
                    ('name', '=', 'ir.model.fields.selection,name'),
                    ('lang', '=', self.env.user.lang),
                    ('module', '=', 'base'), ('res_id', '=', ft.id or 0)])
                sch_tt = sch.interval_type
                if sch_t and sch_t.id:
                    sch_tt = sch_t.value

                sch_min_t = '%s %s' % (sch.interval_number, sch_tt)
                return {'warning': {
                    'title': _('Schedule & alert'),
                    'message': _('If you schedule refresh data every %s, you shouldn\'t set alert for offline every %s minutes') % (sch_min_t, fv)
                }}

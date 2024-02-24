from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CrmTeam(models.Model):

	_name = 'crm.team.ept'
	_description = 'CRM Teams'

	name = fields.Char(string="Team Name", help="Name of the crm team")
	team_leader = fields.Many2one(comodel_name='res.users', string="Team Leader", help="Leader of the crm team")

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command


class AccountTax(models.Model):
	_name = 'account.tax.ept'
	_description = 'Account Tax'

	name = fields.Char(string="Name", help="Name of the account record")
	tax_use = fields.Selection(selection=[
		('None', 'None'),
		('Sale', 'Sale'),
		('Purchase', 'Purchase'),
		], string="Tax Use", help="Tax use of the account")
	tax_value = fields.Float(string="Amount", help="Tax amount of the account")
	tax_amount_type = fields.Selection(selection=[
		('Percentage', 'Percentage'),
		('Fixed', 'Fixed'),
		], string="Amount Type", help="Tax amount type of the account", default="Percentage")

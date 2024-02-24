from odoo import fields, models


class ResParter(models.Model):
	_name = 'res.partner.ept'
	_description = 'Res Partners'

	name = fields.Char(string="Name", help="Name of the partner")
	email = fields.Char(string="Email", help="Email of the partner")
	mobile = fields.Char(string="Mobile No.", help="Mobile number of the partner")
	photo = fields.Image(string="Photo", help="Profile image of the partner")
	website = fields.Char(string="Website", help="Website of the partner")
	street1 = fields.Char(string="Street1", help="Street1 address of the partner")
	street2 = fields.Char(string="Street2", help="Street2 address of the partner")
	city = fields.Many2one(comodel_name="res.city.ept", string="City", help="City of the partner")
	state = fields.Many2one(comodel_name="res.state.ept", string="State", help="State of the partner")
	country = fields.Many2one(comodel_name="res.country.ept", string="Country", help="Country of the partner")
	zipcode = fields.Char(string="Zip Code", help="Zip code of the partner")
	active = fields.Boolean(string="Active", help="Whether this partner is active or not?", default=True)
	parent_id = fields.Many2one(comodel_name="res.partner.ept", string="Parent Partner", help="Parent of the partner")
	child_ids = fields.One2many(comodel_name="res.partner.ept", inverse_name="parent_id", string="Parent Partner", help="Parent of the partner")
	address_type = fields.Selection(selection=[
		('Invoice', 'Invoice'), ('Shipping', 'Shipping'), ('Contact', 'Contact')
		], string="Parent Partner", help="Parent of the partner")

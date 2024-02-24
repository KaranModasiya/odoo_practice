from odoo import models, fields

class EmployeeLeave(models.Model):

	_name = 'employee.leave.ept'
	_description = 'Employee Leaves'
	_rec_name = 'employee_id'

	employee_id = fields.Many2one(comodel_name="employee.ept", string="Employee", help="Name of the employee")
	department_id = fields.Many2one(comodel_name="employee.department.ept", related="employee_id.department_name_id", string="Department", help="Department of the employee")
	start_date = fields.Date(string="Start Date", help="Start date of the leave")
	end_date = fields.Date(string="End Date", help="End date of the leave")
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Approved', 'Approved'),
		('Refused', 'Refused'),
		('Cancelled', 'Cancelled'),
		], string="Status", help="Status of the leave", default="Draft")
	leave_description = fields.Char(string="Leave Description", help="Description of the leave")

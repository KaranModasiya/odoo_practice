from odoo import models, fields

class EmployeeDepartmentShift(models.Model):
	
	_name = 'employee.department.shift.ept'
	_description = 'Employee Department Shift'
	_rec_name = 'shift'

	shift = fields.Selection(
		selection=[
			('Morning', 'Morning'),
			('Afternoon', 'Afternoon'),
			('Evening', 'Evening'),
			('Night', 'Night')
			], string="Shift", help="Shift of the employee"
		)

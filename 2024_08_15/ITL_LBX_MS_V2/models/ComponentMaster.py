from odoo import models, fields, api, _

class ComponentsMater(models.Model):
    _name = "components_master"
    _description = "Components details"
    _rec_name = 'ComponentName'

    ComponentName = fields.Char(string='Component Name', required=True, index=True)

    _sql_constraints = [
        ('component_name_unique', 'UNIQUE(ComponentName)', 'Component Name must be unique!'),
    ]
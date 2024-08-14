from odoo import models, fields, api, _

class FiberMaster(models.Model):
    _name = "fiber_master"
    _description = "fiber master"
    _rec_name = "fibername"

    fibername = fields.Char(string='Fiber Name')
    id = fields.Integer(string='Id')
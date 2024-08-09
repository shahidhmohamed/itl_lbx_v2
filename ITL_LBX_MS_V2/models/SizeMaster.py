from odoo import models, fields

class SizeMaster(models.Model):
    _name = "size_master"

    size_id = fields.Char(string='Size Id')
    size = fields.Char(string='Size')
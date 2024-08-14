from odoo import models, fields, api, _



class SubChain(models.Model):
    _name = "itl_code"
    _description = "Itl Code Details"
    _rec_name = 'ItlCode'

    ItlCode = fields.Char(string='Itl Code')
    ItlCode_Name = fields.Char(string='Itl Code')
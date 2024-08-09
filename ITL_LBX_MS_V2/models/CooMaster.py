from odoo import models, fields, api, _


class LbxCoomaster(models.Model):
    _name = "coo_master"
    _description = "LBX COO MASTER"
    _rec_name = 'Coo'


    Coo = fields.Char (string = 'Coo')
    coo_name = fields.Char (string = 'Coo Name')
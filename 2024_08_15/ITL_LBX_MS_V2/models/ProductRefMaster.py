from odoo import models, fields, api, _


class LbxMiReferenceMaster(models.Model):
    _name = "product_reference_master"
    _description = "PRODUCT REFERENCE MASTER"
    _rec_name = 'ProductRef'

    ProductRef = fields.Char(string='Product Reference')
    ProductRef_name = fields.Char(string='Product Reference')
    # is_default = fields.Boolean(string='Is Default')

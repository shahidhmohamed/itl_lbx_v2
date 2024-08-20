from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        result = []
        for partner in self:
            if partner.type == 'delivery':
                # Construct the address string
                name = ', '.join(filter(None, [
                    partner.street,
                    partner.street2,
                    partner.city,
                    partner.state_id.name if partner.state_id else None,
                    partner.zip,
                    partner.country_id.name if partner.country_id else None
                ]))
            else:
                name = partner.name
            result.append((partner.id, name))
        return result

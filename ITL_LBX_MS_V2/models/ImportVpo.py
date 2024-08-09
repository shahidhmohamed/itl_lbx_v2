import base64
import hashlib
from io import BytesIO
import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class GetVpoMas(models.Model):
    _name = 'get_vpo_mas'
    _description = 'Purchase Order Lines'
    _rec_name = 'po_number'

    po_number = fields.Char(string='Po Number')
    line_ids = fields.One2many('get_vpo_mas_lines', 'header_table', string='Order Lines')
    file_ids = fields.One2many('vpo_files', 'parent_id', string='Files')
    file_number = fields.Char(string='File Number', related='file_ids.name', store=True)
    imported_files = fields.One2many('vpo_imported_files', 'parent_id', string='Imported Files')

    def import_file(self):
        if not self.file_ids:
            raise UserError(_("Please upload at least one Excel file."))

        for file_record in self.file_ids:
            if file_record.file_type == 'excel':
                file_hash = hashlib.md5(base64.b64decode(file_record.file_data)).hexdigest()
                if self.imported_files.filtered(lambda f: f.file_hash == file_hash):
                    continue  # Skip this file as it's already imported

                self._import_excel(file_record.file_data, file_record.name)
                self.env['vpo_imported_files'].create({
                    'parent_id': self.id,
                    'file_hash': file_hash,
                    'file_number': file_record.name,
                })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('All Excel files imported successfully.'),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _import_excel(self, file_data, file_number):
        try:
            # Decode the uploaded file
            data = base64.b64decode(file_data)
            workbook = xlrd.open_workbook(file_contents=BytesIO(data).read())
            records = []

            for sheet_index in range(workbook.nsheets):
                sheet = workbook.sheet_by_index(sheet_index)

                # Find the header row by scanning the sheet
                header_row_index = None
                for row_idx in range(sheet.nrows):
                    row = sheet.row(row_idx)

                    if any(cell.value == 'STYLE' for cell in row) and any(cell.value == 'QTY' for cell in row):
                        header_row_index = row_idx
                        break

                if header_row_index is None:
                    raise UserError(_('Header row not found in sheet %d' % sheet_index))

                header_columns = {cell.value: idx for idx, cell in enumerate(sheet.row(header_row_index))}
                expected_headers = ['STYLE', 'CC', 'SIZE', 'RETAIL (USD)', 'RETAIL (CAD)', 'RETAIL (GBP)', 'SKU', 'DESC', 'ARTICLE', 'QTY']

                for header in expected_headers:
                    if header not in header_columns:
                        raise UserError(_('Expected header column "%s" not found in sheet %d' % (header, sheet_index)))

                for row_idx in range(header_row_index + 1, sheet.nrows):
                    row = sheet.row(row_idx)

                    if row_idx == header_row_index + 1 and len(row) > len(expected_headers):
                        continue

                    if not any(cell.value for cell in row):
                        continue

                    try:
                        style_idx = header_columns.get('STYLE')
                        cc_idx = header_columns.get('CC')
                        size_idx = header_columns.get('SIZE')
                        retail_usd_idx = header_columns.get('RETAIL (USD)')
                        retail_cad_idx = header_columns.get('RETAIL (CAD)')
                        retail_gbp_idx = header_columns.get('RETAIL (GBP)')
                        sku_idx = header_columns.get('SKU')
                        desc_idx = header_columns.get('DESC')
                        article_idx = header_columns.get('ARTICLE')
                        qty_idx = header_columns.get('QTY')

                        style = row[style_idx].value if style_idx is not None else ''
                        cc = row[cc_idx].value if cc_idx is not None else ''
                        size = row[size_idx].value if size_idx is not None else ''
                        retail_usd = row[retail_usd_idx].value if retail_usd_idx is not None else ''
                        retail_cad = row[retail_cad_idx].value if retail_cad_idx is not None else ''
                        retail_gbp = row[retail_gbp_idx].value if retail_gbp_idx is not None else ''
                        sku = row[sku_idx].value if sku_idx is not None else ''
                        desc = row[desc_idx].value if desc_idx is not None else ''
                        article = row[article_idx].value if article_idx is not None else ''
                        qty = row[qty_idx].value if qty_idx is not None else ''

                        if style and qty:
                            record = {
                                'header_table': self.id,
                                'style': style or '',
                                'cc': cc or '',
                                'size': size or '',
                                'retail_usd': retail_usd or '',
                                'retail_cad': retail_cad or '',
                                'retail_gbp': retail_gbp or '',
                                'sku': sku or '',
                                'desc': desc or '',
                                'article': article or '',
                                'qty': qty or '',
                                'file_number': file_number,
                            }
                            records.append(record)
                    except Exception as e:
                        raise UserError(_('Error processing row %d in sheet %d: %s' % (row_idx, sheet_index, str(e))))

            if records:
                self.env['get_vpo_mas_lines'].create(records)

        except Exception as e:
            raise UserError(_('Failed to import Excel file: %s' % str(e)))

    def delete_records_from_related_model(self):
        if not self.po_number:
            raise UserError(_('Please provide a PO Number for deleting records.'))

        # Assuming get_vpo_mas_lines is the related model
        gpo_d001_model = self.env['get_vpo_mas_lines']
        hash_table = self.env['vpo_imported_files']

        # Find records based on PoNumber
        records_to_delete = gpo_d001_model.search([('po_number', '=', self.po_number)])

        if not records_to_delete:
            raise UserError(_('No records found with PO Number %s' % self.po_number))

        file_numbers_to_delete = records_to_delete.mapped('file_number')
    
        # Find the file hash records related to the file numbers
        imported_files_to_delete = self.env['vpo_imported_files'].search([('file_number', 'in', file_numbers_to_delete)])

        # Delete the records in the related model
        records_to_delete.unlink()

        # Delete the imported file hash records
        imported_files_to_delete.unlink()

        # Check if any records were deleted
        if records_to_delete or imported_files_to_delete:
            # Notification for success
            message = _("PO and related imported file records deleted successfully.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'danger',
                    'sticky': True,
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
                }
            }
        else:
            # No records deleted, show a different message or do nothing
            return {'type': 'ir.actions.do_nothing'}


class VpoImportedFiles(models.Model):
    _name = 'vpo_imported_files'
    _description = 'Imported Files'

    parent_id = fields.Many2one('get_vpo_mas', string='Parent')
    file_hash = fields.Char(string='File Hash')
    file_number = fields.Char(string='File Number')

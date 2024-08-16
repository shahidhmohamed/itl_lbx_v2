import base64
from io import BytesIO
import xlrd
from odoo import models, fields, _
from odoo.exceptions import UserError

class GetPoImportWizard(models.TransientModel):
    _name = 'get_po.import.wizard'
    _description = 'Import PO Lines from Excel'

    file = fields.Binary(string='File', required=True)
    order_number = fields.Char(string='PO Number')

    def import_file(self):
        if not self.file:
            raise UserError(_("Please upload an Excel file."))

        try:
            # Decode the uploaded file
            data = base64.b64decode(self.file)
            workbook = xlrd.open_workbook(file_contents=BytesIO(data).read())
            records = []

            for sheet_index in range(workbook.nsheets):
                sheet = workbook.sheet_by_index(sheet_index)

                # Find the header row by scanning the sheet
                header_row_index = None
                for row_idx in range(sheet.nrows):
                    row = sheet.row(row_idx)

                    # Detect if the row contains the actual header columns
                    if any(cell.value == 'STYLE' for cell in row) and any(cell.value == 'QTY' for cell in row):
                        header_row_index = row_idx
                        break

                if header_row_index is None:
                    raise UserError(_('Header row not found in sheet %d' % sheet_index))

                # Extract header columns dynamically
                header_columns = {cell.value: idx for idx, cell in enumerate(sheet.row(header_row_index))}
                expected_headers = ['STYLE', 'CC', 'SIZE', 'RETAIL (USD)', 'RETAIL (CAD)', 'RETAIL (GBP)', 'SKU', 'DESC', 'ARTICLE', 'QTY']

                # Check if all expected headers are present
                for header in expected_headers:
                    if header not in header_columns:
                        raise UserError(_('Expected header column "%s" not found in sheet %d' % (header, sheet_index)))

                # Process the data rows
                for row_idx in range(header_row_index + 1, sheet.nrows):
                    row = sheet.row(row_idx)

                    # Skip the unwanted column
                    if row_idx == header_row_index + 1 and len(row) > len(expected_headers):
                        continue

                    # Skip rows that are likely not data (e.g., metadata or empty rows)
                    if not any(cell.value for cell in row):
                        continue

                    try:
                        # Extract values using the correct indexes
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

                        # Extract values using the correct indexes
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

                        # Check if the row has valid data
                        if style and qty:  # Basic check to ensure 'style' and 'qty' are not empty
                            record = {
                                'header_table': self.env.context.get('active_id'),
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
                            }
                            records.append(record)
                    except Exception as e:
                        raise UserError(_('Error processing row %d in sheet %d: %s' % (row_idx, sheet_index, str(e))))

            # Create records in the model
            if records:
                self.env['get_vpo_ms_31_07_lines'].create(records)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Excel file imported successfully.'),
                    'type': 'success',
                    'next': {'type': 'ir.actions.act_window_close'},
                },
            }

        except Exception as e:
            raise UserError(_('Failed to import Excel file: %s' % str(e)))

"""
Author: Roberto Requejo Fernández
Date: [11-12-2024]
GitHub: https://github.com/Roberto-RRF
"""

from odoo import models, fields, api # type: ignore
from odoo.exceptions import UserError # type: ignore
import base64
import re
from datetime import datetime

class PayrollPoliciesImport(models.TransientModel):
    _name = 'payroll.policies.import'
    _description = 'Wizard for payroll policies import'


    journal_id = fields.Many2one(
        'account.journal',  # Make sure this is the correct model reference
        string='Diario',
        required=True,
    )
    file = fields.Binary('Archvio Estado de Póliza', required=True,)
    file_name = fields.Char('Nombre Archivo')

    def action_upload(self):
        if not self.file:
            raise UserError("No file uploaded. Please upload a file.")

        try:
            file_content = base64.b64decode(self.file)
            lines = file_content.decode('utf-8').splitlines()

            if lines[0].startswith("P"):

                values = re.split(r'\s{2,}', lines[0])
                date = datetime.strptime(values[1], "%Y%m%d").date()

                JournalEntry = self.env['account.move']
                newEntry = JournalEntry.create({
                    'move_type':'entry',
                    'journal_id': self.journal_id.id,
                    'name':values[4],
                    'date': date,
                })

                self.env['ir.attachment'].create({
                'name': self.file_name, 
                'type': 'binary',
                'datas': self.file,
                'res_model': 'account.move',
                'res_id': newEntry.id,  
                'mimetype': 'text/plain', 
                })
            else:
                raise UserError("Error procesando el archivo")
            line_data = []  

            for line in lines: 
                if line.startswith("M1"):
                    line_values = re.split(r'\s{2,}', line) 
                    account_code = self.format_account_string(line_values[0]) 
                    account = self.env['account.account'].search([('code', '=', '601.84.01')], limit=1)

                    monto = line_values[2].split(' ')
                    name = line_values[1] + " - "+line_values[5]
                    if monto[0] == '0':
                        line_data.append((0, 0, {
                            'account_id': account.id,
                            'debit': float(monto[1]),
                            'name': name,
                        }))
                        line_data.append((0, 0, {
                            'account_id': account.id,
                            'credit': float(monto[1]),
                            'name': name,
                        }))
                    elif monto[1] == 1:
                        line_data.append((0, 0, {
                            'account_id': account.id,
                            'credit': float(monto[1]),
                            'name': name,
                        }))
                        line_data.append((0, 0, {
                            'account_id': account.id,
                            'debit': float(monto[1]),
                            'name': name,
                        }))

                 
            newEntry.write({'line_ids': line_data})

            return {
                'type': 'ir.actions.act_window',
                'name': 'Journal Entry',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': newEntry.id,  # ID of the newly created record
                'target': 'current',
            }

        except Exception as e:
            raise UserError(f"Error processing the file: {e}")
        
    def format_account_string(self, acc_str):
        acc_str = acc_str.split(' ')[1]
        if len(acc_str) == 7:
            return f"{acc_str[:3]}.{acc_str[3:5]}.{acc_str[5:]}"
        else:
            raise ValueError("Error al procesar el codigo de la cuenta")

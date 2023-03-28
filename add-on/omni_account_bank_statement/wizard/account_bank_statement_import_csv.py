import io
import csv
import psycopg2
import datetime

from base64 import b64decode, b64encode
from xml.etree import ElementTree as etree
from lxml import etree as ElementTree
from odoo import _, api, models, Command
from odoo.exceptions import UserError
from odoo.addons.base_import.models.base_import import FIELDS_RECURSION_LIMIT

class AccountBankStmtImportCSV(models.TransientModel):

    _inherit = 'base_import.import'

    def parse_preview(self, options, count=10):

        journal_id = self._context.get('default_journal_id')

        print(f"{journal_id=}")
        for item in self:
            print(f"{item=}")
        
        if options.get('bank_stmt_import', False):
            data = []
            ref = ""
            data_string = ""
            date_format = "%y"

            if "CorpAcctTrxn" in self.file_name and "text/csv" == self.file_type:
                decoded_data = self.file.decode(options["encoding"])
                # Decoded
                with io.StringIO(decoded_data) as fp:
                    reader = csv.reader(fp, delimiter=",", quotechar='"')
                    for index, row in enumerate(reader):
                        if len(row) <= 2:
                            continue
                        if index == 0:
                            ref = row[0].split(" - ")[-1]
                            continue
                        if index == 6:
                            row.append("Reference")
                        elif index > 6:
                            if len(row[0].split("/")) < 3:
                                row[0] += "/" + datetime.date.today().strftime(date_format)
                            row.append(ref)

                        string_converted = '","'.join(row)
                        data_string += '"' + string_converted + '"' + '\n'
                        data.append(row)

                    # Convert string to encoded
                    message_bytes = data_string.encode('ascii')
                    self.file = message_bytes
            elif "trx_inquiry" in self.file_name and "text/csv" == self.file_type:
                decoded_data = self.file.decode(options["encoding"])
                # Decoded
                with io.StringIO(decoded_data) as fp:
                    reader = csv.reader(fp, delimiter=",", quotechar='"')
                    for index, row in enumerate(reader):
                        column_content = row[5]
                        if index > 0:
                            # Remove column 5, As it is duplicated
                            new_line = row[4].strip() + ": " + column_content
                            row[4] = new_line
                        del row[5]
                        string_converted = '","'.join(row)
                        data_string += '"' + string_converted + '"' + '\n'
                        data.append(row)
                    # Convert string to encoded
                    message_bytes = data_string.encode('ascii')
                    self.file = message_bytes

            self = self.with_context(bank_stmt_import=True)
        return super(AccountBankStmtImportCSV, self).parse_preview(options, count=count)


    def _parse_import_data(self, data, import_fields, options):

        # EXTENDS base
        if 'date' in import_fields:
            index_date = import_fields.index('date')
            date_format = "'%d/%m/%y'"
            now = datetime.date.today().strftime(date_format)
            for line in data:
                if "PEND" in line[index_date]:
                    line[index_date] = now
                    options['date_format'] = date_format


        data = super()._parse_import_data(data, import_fields, options)
        journal_id = self._context.get('default_journal_id')
        bank_stmt_import = options.get('bank_stmt_import')
        if not journal_id or not bank_stmt_import:
            return data

        # Improve logic for BCA
        if 'jumlah' in import_fields:
            index_jumlah = import_fields.index('jumlah')
            index_amount = import_fields.index('amount')
            import_fields.append('debit')
            import_fields.append('credit')
            for line in data:
                line[index_jumlah] = line[index_jumlah].strip()
                if not line[index_jumlah]:
                    continue

                get_last_char = list(line[index_jumlah].split(" "))
                length = len(get_last_char)
                sign = get_last_char[length - 1]
                value = get_last_char[0]
                line[index_jumlah] = value

                if "CR" in sign:
                    line.append("0")
                    line.append(value)
                elif "DB" in sign:
                    line.append(value)
                    line.append("0")


            self._parse_float_from_data(data, index_jumlah, 'jumlah', options)

            index_debit = import_fields.index('debit')
            index_credit = import_fields.index('credit')
            for item in data:
                if item[index_debit] == '0':
                    item[index_amount] = item[index_jumlah]
                    item[index_credit] = item[index_jumlah]
                else:
                    item[index_amount] = '-' + item[index_jumlah]
                    item[index_debit] = item[index_jumlah]

            import_fields.remove('debit')
            import_fields.remove('credit')

        return data


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _import_bank_statement(self, attachments):

        # In case of CSV files, only one file can be imported at a time.
        if len(attachments) > 1:
            csv = [bool(self._check_csv(att.name)) for att in attachments]
            if True in csv and False in csv:
                raise UserError(_('Mixing CSV files with other file types is not allowed.'))
            if csv.count(True) > 1:
                raise UserError(_('Only one CSV file can be selected.'))
            return super()._import_bank_statement(attachments)

        if not self._check_csv(attachments.name):
            return super()._import_bank_statement(attachments)
        ctx = dict(self.env.context)

        bank = self.env['account.journal'].search([('id', '=', ctx['default_journal_id'])])
        attachments = self.modify_import_attachement(attachments, bank)

        import_wizard = self.env['base_import.import'].create({
            'res_model': 'account.bank.statement.line',
            'file': attachments.raw,
            'file_name': attachments.name,
            'file_type': attachments.mimetype,
        })
        ctx['wizard_id'] = import_wizard.id
        ctx['default_journal_id'] = self.id
        return {
            'type': 'ir.actions.client',
            'tag': 'import_bank_stmt',
            'params': {
                'model': 'account.bank.statement.line',
                'context': ctx,
                'filename': 'bank_statement_import.csv',
            }
        }

    def modify_import_attachement(self, attachments, bank):

        data = []
        ref = ""
        data_string = ""
        date_format = "%y"
        wrong_bank_account = False

        if isinstance(''.join([i for i in bank.name.upper() if not i.isdigit()]), str):
            bank_name = ''.join([i for i in bank.name.upper() if not i.isdigit()])
        else:
            bank_name = ""
        if isinstance(bank.code.upper(), str):
            bank_code = bank.code.upper()
        else:
            bank_code = ""

        bank_number = ''.join(d for d in bank.name if d.isdigit())

        # print(f"{bank_number=}")
        # print(f"{bank_code=}")

        if 'BCA' in bank_name or 'BCA' in bank_code:
            decoded_data = b64decode(attachments.datas).decode('utf-8')
            # Decoded
            with io.StringIO(decoded_data) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                header = False
                status = False
                row_index = 0
                for index, row in enumerate(reader):
                    if index == 0:
                        if 'Informasi Rekening' in row[0]:
                            ref = row[0].split(" - ")[-1]
                        continue

                    if len(row) <= 3:
                        continue
                    elif header == False:
                        header = True
                        for i in range(len(row)):
                            if row[i] == '':
                                row_index = i
                                status = True
                        if status:
                            del row[row_index]
                        row.append("Reference")
                    else:
                        row[0] = row[0].replace("'","")
                        if status:
                            row[row_index - 1] = row[row_index - 1] + " " + row[row_index]
                            del row[row_index]
                        if len(row[0].split("/")) < 3:
                            row[0] += "/" + datetime.date.today().strftime(date_format)

                        row.append(ref)

                    string_converted = '","'.join(row)
                    data_string += '"' + string_converted + '"' + '\n'
                    data.append(row)

                # Convert string to encoded
                message_bytes = data_string.encode('ascii')
                base64_bytes = b64encode(message_bytes)
                attachments.datas = base64_bytes

        elif 'BANK MANDIRI' in bank_name or 'MDR' in bank_code:
            decoded_data = b64decode(attachments.datas).decode('utf-8')
            # Decoded
            with io.StringIO(decoded_data) as fp:
                reader = csv.reader(fp, delimiter=",", quotechar='"')
                for index, row in enumerate(reader):
                    try:
                        column_content = row[5]
                        if index > 0:
                            if row[0] != bank_number:
                                if row[0].isdigit():
                                    wrong_bank_account = True
                                raise
                            # Remove column 5, As it is duplicated
                            new_line = row[4].strip() + ": " + column_content
                            row[4] = new_line
                        del row[5]
                        string_converted = '","'.join(row)
                        data_string += '"' + string_converted + '"' + '\n'
                        data.append(row)
                    except:
                        if wrong_bank_account:
                            raise UserError(
                                _('Bank Number ' + bank_number + ' is not matching to the import bank number ' +
                                  row[
                                      0] + '. Please refresh the page and re-import the file.'))
                        raise UserError(_('Wrong import statement is selected. Please refresh the page and re-import the correct file.'))

                # Convert string to encoded
                message_bytes = data_string.encode('ascii')
                base64_bytes = b64encode(message_bytes)
                attachments.datas = base64_bytes

        return attachments

# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

from dateutil.relativedelta import relativedelta

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    jumlah = fields.Char("Jumlah")
    


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # _sql_constraints = [
    #     ('bank_statement_unique', 'unique(date, debit, credit, balance, name)', 'Bank Statement Record must be unique!'),
    #     ]
    
# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    google_service_account_credentials = fields.Text(string="Google Service Account Credentials",
        help="Input the downloaded JSON format from Google Service Account. "
        "Copy and paste the content of the JSON file here. ", related='website_id.google_service_account_credentials', readonly=False)

    google_drive_folder_id = fields.Char(string="Google Drive Folder ID",
        help = "Input Google Drive Share Folder ID here", related='website_id.google_drive_folder_id', readonly=False)

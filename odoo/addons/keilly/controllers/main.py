from odoo import http
from odoo.http import request


class Main(http.Controller):
    @http.route('/api/customers', type='json', auth='user')
    def students_json(self):
        records = request.env['res.partner'].sudo().search([])
        return records.read(['name', 'partner_latitude', 'partner_longitude'])

    @http.route('/api/dashboard', auth='user', type='json')
    def get_business_counts(self):
        sale_count = request.env['sale.order'].search_count([])
        customer_count = request.env['res.partner'].search_count([('customer_rank', '>', 0)])
        purchase_count = request.env['purchase.order'].search_count([])

        data = {
            'sale_count': sale_count,
            'customer_count': customer_count,
            'purchase_count': purchase_count
        }

        return data

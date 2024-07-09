import logging
import requests
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

# Disable warnings for insecure requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_latitude = fields.Float(string='Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Longitude', digits=(16, 5))

    @api.model_create_multi
    def create(self, vals_list):
        """ Override create to geocode new partners. """
        partners = super(ResPartner, self).create(vals_list)
        partners._geocode_addresses()
        return partners

    def write(self, vals):
        """ Override write to geocode partners if address changes. """
        result = super(ResPartner, self).write(vals)
        if any(field in vals for field in ['street', 'street2', 'city', 'state_id', 'zip', 'country_id']):
            self._geocode_addresses()
        return result

    def _geocode_addresses(self):
        """ Geocode addresses using Melissa API. """
        for partner in self:
            if not partner.street or not partner.city or not partner.zip or not partner.country_id:
                continue

            base_url = "https://address.melissadata.net/v3/WEB/GlobalAddress/doGlobalAddress"
            params = {
                'id': 'ZWK0LtET-ECyzXccJthCIN**nSAcwXpxhQ0PC2lXxuDAZ-**',
                'format': 'json',
                'a1': partner.street,
                'loc': partner.city,
                'admarea': partner.state_id.name,
                'postal': partner.zip,
                'ctry': partner.country_id.code
            }

            try:
                response = requests.get(base_url, params=params, verify=False)
                response.raise_for_status()
                data = response.json()
                if data['Records'][0]['Latitude']:
                    partner.partner_latitude = data['Records'][0]['Latitude']
                    partner.partner_longitude = data['Records'][0]['Longitude']
            except requests.exceptions.RequestException as e:
                _logger.error(f"Error geocoding partner {partner.id}: {e}")
                print(f"Error geocoding partner {partner.id}: {e}")

# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class APITEST(models.Model):
    _name = "api.test"
    _rec_name='db'
    
    db=fields.Char('Database')
    login=fields.Char('Login')
    password=fields.Char('Password')
    url=fields.Char('URL')

    def check_login(self):
        headers = {
            'charset':'utf-8',
            'content-type': 'application/x-www-form-urlencoded'
        }
        data = {
            'login': self.login, # Local login
            'password': self.password,# Local password
            'db': self.db,
        }
        req = requests.post('/api/login',data=data, headers=headers)
#        _logger.info('----------%s'%(req.content))
        content = json.loads(req.content.decode('utf-8'))
#        # or add the access token to the headers
        headers['access-token'] = content.get('access_token')
        return headers

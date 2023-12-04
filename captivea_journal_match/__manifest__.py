{
    'name': 'Captivea Journal Match',
    'version': '8.0',
    'author': 'Captivea LLC',
    'category': 'Account',
    'website': 'https://www.captivea.us',
    'description': 'Captivea Journal Match',
    'depends': ['account_accountant', 'purchase'],
    'data': [
             'data/ir_cron.xml',
             'data/ir_sequence.xml',
             'views/res_config_settings_view.xml',
             'views/account_move_line.xml',
             'views/journal_match.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}

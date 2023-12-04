{
    'name': 'Cap Purchase Transaction Report',
    'version': '11',
    'category': 'purchase',
    'sequence': 10,
    'summary': 'Purchase Transaction Report',
    'description': """
This module creates the excel report for purchase transactions
       """,
    'website': 'https://www.captivea.com',
    'depends': ['purchase', 'account_reports'],
    'data': [
        'views/purchase_order_view.xml',
        'wizard/purchase_transaction_report_wiz_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
{
    'name': 'Payroll Policies Import',
    'version': '1.0',
    'author':'ANFEPI: Roberto Requejo Fernández',
    'depends': ['base', 'account'],
    'description': """
    
    """,
    'data': [
        'wizard/payroll_policies_import_view.xml',
        'views/menus.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': False,
    "license": "AGPL-3",
}
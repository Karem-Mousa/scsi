# -*- coding: utf-8 -*-
{
    'name': "Excellence CRM Customization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "excellence",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'sale', 'sale_crm', 'project', 'hr_expense'],
    'data': [
        'security/groups.xml',
        'views/crm_lead_inherit.xml',
        'views/sale_order_inherit.xml',
        'views/purchase_order_inherit.xml',
        'views/project_project_inherit.xml',
        'views/hr_expense_inherit.xml'
    ],

}

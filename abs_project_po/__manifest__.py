# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2022-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################
{
    'name'        : 'Purchase Order On Project',
    'author'      : 'Ascetic Business Solution',
    'category'    : 'Purchases',
    'summary'     : 'Purchase Order On Project',
    'website'     : 'http://www.asceticbs.com',
    'description' : """  """,
    'version'     : '15.0.1.0',
    'depends'     : ['base','purchase','project'],
    'data'        : [
                    'views/purchase_order_view.xml',
                    'views/project_view.xml',
                    'views/project_task_view.xml',
                    ],
    'images': ['static/description/banner.png'],
    'license'     : 'AGPL-3',    
    'installable' : True,
    'auto_install': False,    
    'application' : True,
}

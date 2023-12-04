{
    "name": "Kernel - RESTFUL API",
    "version": "2.0",
    "category": "API",
    "author": "Bista Solutions Pvt. Ltd.",
    "website": "https://www.bistasolutions.com",
    "summary": "RESTFUL API",
    "description": """
Integration between OCPLM and RESTFUL API 
==========================================
With use of this module user can enable REST API integration with ocplm.
""",
    "depends": ["web", "base","product"],
    "data": [
        "data/ir_config_param.xml",
        "views/ir_model.xml",
        "views/api_test.xml",
        "views/res_users.xml",
        "security/ir.model.access.csv",
    ],
    "images": ["static/description/main_screenshot.png"],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "external_dependencies": {"python": ["simplejson"], "bin": []},
}

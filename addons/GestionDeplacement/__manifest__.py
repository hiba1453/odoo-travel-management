{
    'name': 'Gestion des Déplacements',
    'version': '1.4',
    'summary': 'Gestion des déplacements des employés avec validation et calcul automatique des frais',
    'category': 'Human Resources',
    'author': 'Lambda Company',
    'depends': ['base', 'hr', 'fleet'],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/ville_view.xml',
        'views/deplacement_view.xml',
        'views/rejet_wizard_view.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}

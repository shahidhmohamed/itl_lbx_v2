{
    'name': 'ITL V 2.2',
    'author':' M.SHAHIDH',
    'sequence': 1,
    'summary': 'New interface for ITL Purches order ',
    'category': 'Administration/Automation',
    'depends':[
        'mail',
        'product',
    ],
    'data': [
        'views/GetPoMas.xml',
        'views/GetVpoMas.xml',
        'security/ir.model.access.csv',
        'views/SizeMaster.xml',
        'views/SizeRangeMaster.xml',
        'views/SizeMapMaster.xml',
        'views/ChainMaster.xml',
        'views/ProductRefMaster.xml',
        'views/CooMaster.xml',
        'views/SeasonMaster.xml',
        'views/CollectionMaster.xml',
        'views/SilhouetteMaster.xml',
        'views/ItlCodeMaster.xml',
        'views/FiberMaster.xml',
        'views/ComponentMaster.xml',
        'views/CompositionMaster.xml',
        'views/CareInstructionSetCodeMaster.xml',
        'views/AdditionalInstructionMaster.xml',
        'views/Dashboard.xml',
        'wizard/RfidPopUpWizard.xml',
        'wizard/RfidPopUpWizardForm.xml',
        'views/AdditionalCareInstructionMaster.xml',
        'security/security.xml',
        'views/ComboColorCodeMaster.xml'
        
    ],
    'assets': {
        'web.assets_backend': [
            'ITL_LBX_MS_V2/static/src/components/**/*.js',
            'ITL_LBX_MS_V2/static/src/components/**/*.xml',
            ('ITL_LBX_MS_V2/static/css/style_backend.css'),
            'https://fonts.googleapis.com/css2?family=Acme&family=Audiowide&family=Bebas+Neue&family=Lexend:wght@100..900&display=swap',
        ],
        'web.assets_frontend': [
            'https://fonts.googleapis.com/css2?family=Acme&family=Audiowide&family=Bebas+Neue&family=Lexend:wght@100..900&display=swap'
        ],
    },
    'installable': True,
    'application': True,
}
import json
from django.core.management.base import BaseCommand,CommandError
from vdt.configuration import load_configuration,preflight
class Command(BaseCommand):
    help='Validate configuration without running CRM or modifying data'
    def add_arguments(self,p):
        p.add_argument('path');p.add_argument('--target',default='all')
    def handle(self,*args,**options):
        result=preflight(load_configuration(options['path']),target=options['target'])
        self.stdout.write(json.dumps(result.as_dict(),ensure_ascii=False,indent=2))
        if result.status!='CONFIG_VALID':raise CommandError('Configuration is not ready for the selected target')

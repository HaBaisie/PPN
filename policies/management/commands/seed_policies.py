from django.core.management.base import BaseCommand
from policies.models import Policy


class Command(BaseCommand):
    help = 'Seed 10 policies'

    def handle(self, *args, **kwargs):
        policies_data = [
            {"name": "Revised National Policy on Food and Nutrition (2016)", "description": "Improve food security and nutrition outcomes."},
            {"name": "National Health Policy", "description": "Strengthen health systems and access to care."},
            {"name": "National Education Policy", "description": "Improve access and quality of education."},
            {"name": "National Agriculture Policy", "description": "Boost agricultural productivity and sustainability."},
            {"name": "National Youth Policy", "description": "Empower youth through skills and opportunities."},
            {"name": "National Gender Policy", "description": "Promote gender equality and inclusion."},
            {"name": "National Climate Change Policy", "description": "Guide mitigation and adaptation efforts."},
            {"name": "National Social Protection Policy", "description": "Provide social safety nets for vulnerable populations."},
            {"name": "National Transport Policy", "description": "Improve transport networks and mobility."},
            {"name": "National ICT Policy", "description": "Expand digital infrastructure and services."},
        ]
        for data in policies_data:
            Policy.objects.get_or_create(name=data['name'], defaults={'description': data['description']})
        self.stdout.write(self.style.SUCCESS('Policies seeded'))

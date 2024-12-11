import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tutorials.models import User, Role
from tutorials.constants import UserRoles

class Command(BaseCommand):
    help = 'Create text files for each user role and save their details'

    def handle(self, *args, **options):
        roles =  [UserRoles.STUDENT, UserRoles.TUTOR, UserRoles.ADMIN]
        output_dir = os.path.join(settings.BASE_DIR, 'user_roles')

        os.makedirs(output_dir, exist_ok=True)
        for role in roles:
            file_path = os.path.join(output_dir, f'{role}.txt')
            
            users = User.objects.filter(roles__name=role)
            
            with open(file_path, 'w') as f:
                if users.exists():
                    for user in users:
                        f.write(f'ID: {user.id}, Name: {user.username}, Email: {user.email}\n')
                else:
                    f.write(f'No users with the role: {role}\n')
        self.stdout.write(self.style.SUCCESS(f"Files created in '{output_dir}'"))

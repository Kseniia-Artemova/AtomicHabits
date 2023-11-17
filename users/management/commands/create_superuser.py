import os
from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    """Команда для создания админа (суперюзера) с заданными в файле .env логином и паролем"""

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username=os.getenv('ADMIN_USERNAME'),
            is_staff=True,
            is_superuser=True
        )
        if created:
            user.set_password(os.getenv('ADMIN_PASSWORD'))
            user.save()
            print('Суперпользователь создан.')
            return
        print('Суперпользователь существует.')

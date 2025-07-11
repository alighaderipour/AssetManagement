# backend/assetmangement/management/commands/create_initial_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from assetmanagement.models import Department, Category, Brand

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial data for the application'

    def handle(self, *args, **options):
        # ایجاد Superuser
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@company.com',
                password='admin123',
                first_name='مدیر',
                last_name='سیستم',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Admin user already exists'))
        
        # ایجاد کاربر عادی
        if not User.objects.filter(username='user1').exists():
            regular_user = User.objects.create_user(
                username='user1',
                email='user1@company.com',
                password='user123',
                first_name='کاربر',
                last_name='تست',
                role='user'
            )
            self.stdout.write(self.style.SUCCESS('Regular user created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Regular user already exists'))

        # ایجاد بخش‌های نمونه
        departments = [
            {'name': 'فناوری اطلاعات', 'code': 'IT', 'type':'hospital'},
            {'name': 'نیرو انسانی', 'code': 'HR', 'type':'hospital'},
            {'name': 'مالی', 'code': 'FIN', 'type':'hospital'},
            {'name': ' امداد و عملیات', 'code': 'OPS', 'type':'hospital'},
            {'name': 'ماشین های اداری پردیس', 'code': 'PAD', 'type':'maintenance'},
        ]
        
        for dept_data in departments:
            department, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={'name': dept_data['name'],  'type': dept_data['type'],}
            )
            if created:
                self.stdout.write(f'Department {dept_data["name"]} created')
            else:
                self.stdout.write(f'Department {dept_data["name"]} already exists')

        # ایجاد دسته‌بندی‌های نمونه با code
        categories = [
            {'name': 'کامپیوت', 'code': 'COMP'},
            {'name': 'لپ‌تاپ', 'code': 'LAPT'},
            {'name': 'پرینتر', 'code': 'PRINT'},
            {'name': 'اسکنر', 'code': 'SCN'},
            {'name': 'تجهیزات شبکه', 'code': 'NET'},
            {'name': 'لوازم جانبی', 'code': 'ACC'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                code=cat_data['code'],
                defaults={'name': cat_data['name']}
            )
            if created:
                self.stdout.write(f'Category {cat_data["name"]} created')
            else:
                self.stdout.write(f'Category {cat_data["name"]} already exists')

        brand_data = {
            'name': 'HP',
            'code': 'BR0001',
            'description': 'اچ پی'
        }
        brand, created = Brand.objects.get_or_create(
            code=brand_data['code'],
            defaults={'name': brand_data['name'], 'description': brand_data['description']}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Brand {brand_data["name"]} created!'))
        else:
            self.stdout.write(self.style.WARNING(f'Brand {brand_data["name"]} already exists.'))

        self.stdout.write(self.style.SUCCESS('Initial data created successfully!'))

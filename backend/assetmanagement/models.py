from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import os
#haha models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    phone = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

class UseCase(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=12, unique=True, editable=False)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = 'UC' + str(UseCase.objects.count() + 1).zfill(4)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
class Department(models.Model):
    DEPARTMENT_TYPES = [
        ('hospital', 'Hospital Department'),
        ('maintenance', 'Maintenance Department'),
    ]
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=20, choices=DEPARTMENT_TYPES, default='hospital')
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Asset(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, editable=False)
    description = models.TextField(blank=True)
    usecase = models.ForeignKey(UseCase, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assets'
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='owned_assets'
    )

    current_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_department_assets'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.IntegerField(default=1, editable=False)
    serial_number = models.CharField(max_length=100, blank=True)
    asset_code = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='assets/', blank=True, null=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_assets'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Assets"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:8].upper()
        if not self.current_department and self.department:
            self.current_department = self.department
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class AssetTransfer(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    from_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='transfers_from'
    )
    to_department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='transfers_to'
    )
    transfer_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    transferred_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='initiated_transfers'
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    image = models.ImageField(upload_to='asset_transfers/', null=True, blank=True)

    def __str__(self):
        return f"{self.asset.name} from {self.from_department.name} to {self.to_department.name}"




class Brand(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=12, unique=True, editable=False)  # اتومات جنریت میشه
    description = models.TextField(blank=True)
    # می‌تونی هر فیلد دیگه‌ای نیاز داری اضافه کنی

    def save(self, *args, **kwargs):
        if not self.code:
            # تولید کد منحصر به فرد به طور اتومات (مثلا نام کوتاه+آی‌دی یا ...)
            self.code = 'BR' + str(Brand.objects.count() + 1).zfill(4)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

from django.db.models.signals import post_delete
from django.dispatch import receiver
@receiver(post_delete, sender=AssetTransfer)
def delete_invoice_image_file(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        if os.path.isfile(image_path):
            try:
                os.remove(image_path)
                print(f"DELETED: {image_path}")
            except Exception as e:
                print(f"Error deleting {image_path}: {e}")
        else:
            print(f"File not found: {image_path}")
    else:
        print("No image to delete.")





from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        PHARMACIST = 'PHARMACIST', _('Pharmacist')
        ASSISTANT = 'ASSISTANT', _('Assistant')

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.ASSISTANT
    )

    def is_admin(self):
        return self.role == self.Role.ADMIN
        
    def is_pharmacist(self):
        return self.role == self.Role.PHARMACIST
        
    def is_assistant(self):
        return self.role == self.Role.ASSISTANT

class Medicine(models.Model):
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=150)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    reorder_level = models.PositiveIntegerField(default=10)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.brand})"
        
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.reorder_level

class Prescription(models.Model):
    patient_name = models.CharField(max_length=150)
    prescriber = models.CharField(max_length=150, blank=True, help_text="Doctor who issued the prescription")
    date_prescribed = models.DateTimeField(auto_now_add=True)
    
    filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='filled_prescriptions')
    filled_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.patient_name} - {self.date_prescribed.strftime('%Y-%m-%d')}"

    @property
    def total_price(self):
        return sum(item.item_total for item in self.items.all())

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine = models.ForeignKey(Medicine, on_delete=models.RESTRICT, related_name='prescription_items')
    quantity = models.PositiveIntegerField()
    dosage = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.medicine.name} for {self.prescription.patient_name}"

    @property
    def item_total(self):
        return self.medicine.price * self.quantity

class Sale(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='sale')
    medicine = models.ForeignKey(Medicine, on_delete=models.RESTRICT, related_name='sales')
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_sold = models.DateTimeField(auto_now_add=True)
    sold_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sales_processed')

    def __str__(self):
        return f"Sale {self.id} - {self.medicine.name}"

class Supplier(models.Model):
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class StockEntry(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='stock_entries')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='stock_entries')
    quantity = models.PositiveIntegerField()
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_entries_added')

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            # Update medicine stock only for new entries
            self.medicine.stock_quantity += self.quantity
            self.medicine.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stock Entry: {self.medicine.name} - {self.quantity}"

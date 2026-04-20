from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Medicine, Prescription, PrescriptionItem, Sale, Supplier, StockEntry

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'stock_quantity', 'reorder_level', 'expiry_date')
    list_filter = ('category',)
    search_fields = ('name', 'brand')

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email')
    search_fields = ('name', 'contact_person')

@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'supplier', 'quantity', 'unit_cost', 'date_added', 'added_by')
    list_filter = ('supplier', 'date_added')
    search_fields = ('medicine__name',)

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 0

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'item_count', 'total_price', 'date_prescribed', 'filled')
    list_filter = ('filled', 'date_prescribed')
    search_fields = ('patient_name',)
    inlines = [PrescriptionItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Number of Items'

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('medicine', 'quantity', 'total_price', 'date_sold', 'sold_by')
    list_filter = ('date_sold',)
    search_fields = ('medicine__name',)

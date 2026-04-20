from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Medicine, Prescription, Sale, Supplier, StockEntry
from .forms import (
    MedicineForm, PrescriptionForm, SaleForm, SupplierForm, StockEntryForm,
    CustomUserCreationForm
)

def is_admin_or_assistant(user):
    return user.is_authenticated and (user.is_admin() or user.is_assistant())

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm()
    return render(request, 'landing.html', {'form': form})

@login_required
def dashboard(request):
    total_medicines = Medicine.objects.count()
    low_stock_medicines = [m for m in Medicine.objects.all() if m.is_low_stock]
    low_stock_count = len(low_stock_medicines)
    
    pending_prescriptions = Prescription.objects.filter(filled=False).count()
    
    # Calculate today's sales and prescriptions
    today = timezone.localtime().date()
    todays_sales = Sale.objects.filter(date_sold__date=today).aggregate(total=Sum('total_price'))['total']
    todays_sales = todays_sales if todays_sales else 0.00
    
    todays_prescriptions = Prescription.objects.filter(date_prescribed__date=today).count()
    
    context = {
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'today_sales': todays_sales,
        'pending_prescriptions': pending_prescriptions,
        'todays_prescriptions': todays_prescriptions,
    }
    
    # Role-specific data
    if request.user.role == User.Role.PHARMACIST:
        # Optimization: prefetch items for the dashboard list
        context['recent_pending_prescriptions'] = Prescription.objects.filter(filled=False).prefetch_related('items__medicine').order_by('-date_prescribed')[:5]
    else:
        # Admin and Assistant see low stock items
        context['low_stock_medicines'] = low_stock_medicines[:5]
    return render(request, 'dashboard.html', context)

@login_required
def medicine_list(request):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    stock_filter = request.GET.get('stock', '')
    
    medicines = Medicine.objects.all()
    
    if query:
        medicines = medicines.filter(name__icontains=query) | medicines.filter(brand__icontains=query)
    if category:
        # Use exact match for better filtering from dropdown
        medicines = medicines.filter(category=category)
        
    if stock_filter == 'low':
        medicines = [m for m in medicines if m.is_low_stock]
        
    # Get unique categories for filter, excluding empty/None and sorting
    categories = Medicine.objects.exclude(category__in=['', None]).values_list('category', flat=True)
    categories = sorted(list(set(categories)))
    
    return render(request, 'medicine_list.html', {
        'medicines': medicines,
        'categories': categories,
        'query': query,
        'selected_category': category
    })

@user_passes_test(is_admin_or_assistant)
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine added successfully.')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'medicine_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(is_admin_or_assistant)
def medicine_update(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=medicine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicine updated successfully.')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
    return render(request, 'medicine_form.html', {'form': form, 'action': 'Edit', 'medicine': medicine})

@user_passes_test(is_admin_or_assistant)
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully.')
        return redirect('medicine_list')
    return render(request, 'medicine_confirm_delete.html', {'medicine': medicine})

# --- Prescription Views ---

@login_required
def prescription_list(request):
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'filled':
        prescriptions = Prescription.objects.filter(filled=True).order_by('-filled_date')
    else:
        prescriptions = Prescription.objects.filter(filled=False).order_by('-date_prescribed')
        
    return render(request, 'prescription_list.html', {
        'prescriptions': prescriptions,
        'status_filter': status_filter
    })

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist() or u.is_assistant()))
def prescription_create(request):
    from .forms import PrescriptionItemFormSet
    from django.db import transaction

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                prescription = form.save()
                formset.instance = prescription
                formset.save()
                
                messages.success(request, 'Prescription added successfully.')
                return redirect('prescription_list')
    else:
        # Default prescriber to current user
        form = PrescriptionForm(initial={'prescriber': request.user})
        formset = PrescriptionItemFormSet()
        
    return render(request, 'prescription_form.html', {'form': form, 'formset': formset})

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def prescription_fill(request, pk):
    from django.utils import timezone
    from .models import Sale
    
    prescription = get_object_or_404(Prescription, pk=pk)
    
    if request.method == 'POST':
        if prescription.filled:
            messages.error(request, 'This prescription has already been filled.')
            return redirect('prescription_list')
            
        items = prescription.items.all()
        if not items.exists():
            messages.error(request, 'Empty prescription cannot be filled.')
            return redirect('prescription_detail', pk=pk)

        # 1. Validation check for all items first
        for item in items:
            if item.medicine.stock_quantity < item.quantity:
                messages.error(request, f'Insufficient stock for {item.medicine.name}. Available: {item.medicine.stock_quantity}')
                return redirect('prescription_detail', pk=pk)
            
        # 2. Process all items
        for item in items:
            medicine = item.medicine
            # Deduct stock
            medicine.stock_quantity -= item.quantity
            medicine.save()
            
            # Create a sale record
            Sale.objects.create(
                prescription=prescription,
                medicine=medicine,
                quantity=item.quantity,
                total_price=medicine.price * item.quantity,
                sold_by=request.user
            )
            
        # 3. Mark prescription as filled
        prescription.filled = True
        prescription.filled_by = request.user
        prescription.filled_date = timezone.now()
        prescription.save()
        
        messages.success(request, f'Prescription for {prescription.patient_name} filled successfully ({items.count()} items).')
        return redirect('prescription_list')
        
    return render(request, 'prescription_detail.html', {'prescription': prescription})

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, 'prescription_detail.html', {'prescription': prescription})

@login_required
def prescription_print(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, 'prescription_print.html', {'prescription': prescription})

# --- Direct OTC Sale Views ---

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_assistant() or u.is_pharmacist()))
def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            medicine = sale.medicine
            
            if medicine.stock_quantity < sale.quantity:
                messages.error(request, f'Insufficient stock! Only {medicine.stock_quantity} available.')
            else:
                # Deduct stock
                medicine.stock_quantity -= sale.quantity
                medicine.save()
                
                # Complete sale
                sale.total_price = medicine.price * sale.quantity
                sale.sold_by = request.user
                sale.save()
                messages.success(request, f'Direct sale for {medicine.name} registered. Total: ₦{sale.total_price}')
                return redirect('dashboard')
    else:
        form = SaleForm()
    return render(request, 'sale_form.html', {'form': form})

# --- Analytics Views ---

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def analytics(request):
    import json
    from datetime import timedelta
    from django.db.models import Count
    
    # Last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # 1. Top Medicines (Quantity Sold)
    top_medicines = Sale.objects.filter(date_sold__gte=thirty_days_ago) \
        .values('medicine__name') \
        .annotate(total_quantity=Sum('quantity')) \
        .order_by('-total_quantity')[:10]
        
    top_meds_labels = [item['medicine__name'] for item in top_medicines]
    top_meds_data = [item['total_quantity'] for item in top_medicines]
    
    # 2. Revenue Trend (Last 7 Days)
    seven_days_ago = timezone.now() - timedelta(days=6) # 7 days including today
    daily_revenue = []
    daily_labels = []
    
    for i in range(7):
        target_date = (seven_days_ago + timedelta(days=i)).date()
        daily_labels.append(target_date.strftime('%b %d'))
        sales = Sale.objects.filter(date_sold__date=target_date).aggregate(total=Sum('total_price'))['total']
        daily_revenue.append(float(sales or 0.00))
        
    # 3. Sales by Category
    category_sales = Sale.objects.filter(date_sold__gte=thirty_days_ago) \
        .values('medicine__category') \
        .annotate(total=Sum('total_price')) \
        .order_by('-total')
        
    cat_labels = [item['medicine__category'] for item in category_sales]
    cat_data = [float(item['total']) for item in category_sales]
    
    # Summary Cards
    monthly_revenue = Sale.objects.filter(date_sold__gte=thirty_days_ago).aggregate(total=Sum('total_price'))['total'] or 0.00
    total_sales_count = Sale.objects.filter(date_sold__gte=thirty_days_ago).count()
    avg_daily_sales = float(monthly_revenue) / 30 if monthly_revenue else 0.00

    # 4. Prescription Metrics (Accountability)
    total_prescriptions = Prescription.objects.filter(date_prescribed__gte=thirty_days_ago).count()
    filled_count = Prescription.objects.filter(date_prescribed__gte=thirty_days_ago, filled=True).count()
    pending_count = Prescription.objects.filter(date_prescribed__gte=thirty_days_ago, filled=False).count()
    
    # Prescriptions by Staff member (Accountability leader-board)
    staff_stats = Prescription.objects.filter(date_prescribed__gte=thirty_days_ago) \
        .values('prescriber__username') \
        .annotate(count=Count('id')) \
        .order_by('-count')
    
    staff_labels = [item['prescriber__username'] or 'Unknown' for item in staff_stats]
    staff_data = [item['count'] for item in staff_stats]

    context = {
        'top_meds_labels': json.dumps(top_meds_labels),
        'top_meds_data': json.dumps(top_meds_data),
        
        'daily_labels': json.dumps(daily_labels),
        'daily_revenue': json.dumps(daily_revenue),
        
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        
        'staff_labels': json.dumps(staff_labels),
        'staff_data': json.dumps(staff_data),
        
        'monthly_revenue': float(monthly_revenue),
        'total_sales_count': total_sales_count,
        'avg_daily_sales': avg_daily_sales,
        
        'total_precscriptions': total_prescriptions, # typo preserved if any, but let's fix it
        'total_prescriptions': total_prescriptions,
        'filled_count': filled_count,
        'pending_count': pending_count,
    }
    
    return render(request, 'analytics.html', context)

# --- Reporting & Exporting Views ---

import csv
from django.http import HttpResponse

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist() or u.is_assistant()))
def reports_portal(request):
    return render(request, 'reports.html')

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist() or u.is_assistant()))
def export_inventory(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Brand', 'Category', 'Price', 'Stock Quantity', 'Reorder Level', 'Status', 'Expiry Date'])

    for medicine in Medicine.objects.all():
        status = "Low Stock" if medicine.is_low_stock else "Sufficient"
        writer.writerow([
            medicine.id, medicine.name, medicine.brand, medicine.category, 
            medicine.price, medicine.stock_quantity, medicine.reorder_level, 
            status, medicine.expiry_date
        ])

    return response

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def export_prescriptions(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="prescriptions.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Patient Name', 'Prescribed By', 'Medicines', 'Date Prescribed', 'Filled', 'Filled By', 'Filled Date'])

    for p in Prescription.objects.all().order_by('-date_prescribed'):
        # Combine all medicine names and quantities for this prescription
        medicines_list = [f"{item.medicine.name} (x{item.quantity})" for item in p.items.all()]
        medicines_str = ", ".join(medicines_list)
        
        prescriber_name = p.prescriber.get_full_name() or p.prescriber.username if p.prescriber else "Unknown"
        filled_by = p.filled_by.get_full_name() or p.filled_by.username if p.filled_by else "N/A"
        filled_date = p.filled_date.strftime('%Y-%m-%d %H:%M:%S') if p.filled_date else "N/A"
        
        writer.writerow([
            p.id, 
            p.patient_name, 
            prescriber_name,
            medicines_str, 
            p.date_prescribed.strftime('%Y-%m-%d %H:%M:%S'), 
            "Yes" if p.filled else "No", 
            filled_by, 
            filled_date
        ])

    return response

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def export_sales(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Medicine', 'Quantity', 'Total Price', 'Sold By', 'Date Sold', 'Type'])

    for s in Sale.objects.all().order_by('-date_sold'):
        sale_type = "Prescription" if s.prescription else "OTC Direct"
        sold_by = s.sold_by.username if s.sold_by else "Unknown"
        writer.writerow([
            s.id, s.medicine.name, s.quantity, s.total_price, 
            sold_by, s.date_sold.strftime('%Y-%m-%d %H:%M:%S'), sale_type
        ])

    return response

# --- Print Report Views ---

@login_required
def report_inventory_print(request):
    medicines = Medicine.objects.all().order_by('name')
    return render(request, 'report_inventory_print.html', {
        'medicines': medicines,
        'report_title': 'Full Inventory List',
        'now': timezone.now()
    })

@login_required
def report_low_stock_print(request):
    medicines = [m for m in Medicine.objects.all() if m.is_low_stock]
    return render(request, 'report_inventory_print.html', {
        'medicines': medicines,
        'report_title': 'Low Stock Alert Report',
        'now': timezone.now()
    })

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def report_sales_print(request):
    sales = Sale.objects.all().order_by('-date_sold')
    total_revenue = sales.aggregate(total=Sum('total_price'))['total'] or 0
    return render(request, 'report_sales_print.html', {
        'sales': sales,
        'total_revenue': total_revenue,
        'report_title': 'Sales Transaction Report',
        'now': timezone.now()
    })


# --- Supplier Views ---

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'supplier_list.html', {'suppliers': suppliers})

@user_passes_test(is_admin_or_assistant)
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'supplier_form.html', {'form': form, 'action': 'Add'})

@user_passes_test(is_admin_or_assistant)
def supplier_update(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully.')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'supplier_form.html', {'form': form, 'action': 'Edit'})

@user_passes_test(is_admin_or_assistant)
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect('supplier_list')
    return render(request, 'supplier_confirm_delete.html', {'supplier': supplier})

# --- Stock Entry Views ---

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_assistant() or u.is_pharmacist()))
def stock_entry_create(request):
    if request.method == 'POST':
        form = StockEntryForm(request.POST)
        if form.is_valid():
            stock_entry = form.save(commit=False)
            stock_entry.added_by = request.user
            stock_entry.save() # The model's save() now handles medicine stock update
            
            messages.success(request, f'Added {stock_entry.quantity} units to {stock_entry.medicine.name}.')
            return redirect('medicine_list')
    else:
        initial_med_pk = request.GET.get('medicine')
        initial_data = {}
        if initial_med_pk:
            initial_data['medicine'] = initial_med_pk
        form = StockEntryForm(initial=initial_data)
    return render(request, 'stock_entry_form.html', {'form': form})
# --- User Management Views (Admin only) ---

@user_passes_test(lambda u: u.is_authenticated and u.is_admin())
def user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'user_list.html', {'users': users})

@user_passes_test(lambda u: u.is_authenticated and u.is_admin())
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'user_form.html', {'form': form, 'action': 'Create'})

@user_passes_test(lambda u: u.is_authenticated and u.is_admin())
def user_delete(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')
    
    if request.method == 'POST':
        user_to_delete.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')
    return render(request, 'supplier_confirm_delete.html', {
        'object': user_to_delete, 
        'title': 'User',
        'cancel_url': 'user_list'
    })

@login_required
def setup_system(request):
    # 1. Update current user to ADMIN
    user = request.user
    user.role = User.Role.ADMIN
    user.save()
    
    # 2. Add sample medicines if none exist
    if Medicine.objects.count() == 0:
        Medicine.objects.create(
            name="Paracetamol",
            brand="Panadol",
            category="Pain Relief",
            price=1.50,
            stock_quantity=100,
            reorder_level=20,
            expiry_date="2027-12-31"
        )
        Medicine.objects.create(
            name="Amoxicillin",
            brand="Amoxil",
            category="Antibiotics",
            price=12.00,
            stock_quantity=50,
            reorder_level=10,
            expiry_date="2026-06-30"
        )
        Medicine.objects.create(
            name="Ibuprofen",
            brand="Advil",
            category="Inflammation",
            price=4.50,
            stock_quantity=80,
            reorder_level=15,
            expiry_date="2027-01-01"
        )
        messages.success(request, 'System initialized with sample data.')
    
    messages.success(request, f'Your role has been upgraded to {user.get_role_display()}.')
    return redirect('dashboard')


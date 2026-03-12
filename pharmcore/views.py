from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Medicine, Prescription, Sale, Supplier, StockEntry
from .forms import MedicineForm, PrescriptionForm, SaleForm, SupplierForm, StockEntryForm
from django.utils import timezone
from django.db.models import Sum
from django.contrib import messages
from .models import Medicine
from .forms import MedicineForm

def is_admin_or_assistant(user):
    return user.is_authenticated and (user.is_admin() or user.is_assistant())

@login_required
def dashboard(request):
    total_medicines = Medicine.objects.count()
    low_stock_medicines = [m for m in Medicine.objects.all() if m.is_low_stock]
    low_stock_count = len(low_stock_medicines)
    
    pending_prescriptions = Prescription.objects.filter(filled=False).count()
    
    # Calculate today's sales
    today = timezone.localtime().date()
    todays_sales = Sale.objects.filter(date_sold__date=today).aggregate(total=Sum('total_price'))['total']
    todays_sales = todays_sales if todays_sales else 0.00
    
    context = {
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'today_sales': todays_sales,
        'pending_prescriptions': pending_prescriptions,
        'low_stock_medicines': low_stock_medicines[:5] # Show top 5
    }
    return render(request, 'dashboard.html', context)

@login_required
def medicine_list(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    stock_filter = request.GET.get('stock', '')
    
    medicines = Medicine.objects.all()
    
    if query:
        medicines = medicines.filter(name__icontains=query) | medicines.filter(brand__icontains=query)
    if category:
        medicines = medicines.filter(category__icontains=category)
        
    if stock_filter == 'low':
        medicines = [m for m in medicines if m.is_low_stock]
        
    # Get unique categories for filter
    categories = Medicine.objects.values_list('category', flat=True).distinct()
    
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

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def prescription_create(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prescription added successfully.')
            return redirect('prescription_list')
    else:
        form = PrescriptionForm()
    return render(request, 'prescription_form.html', {'form': form})

@user_passes_test(lambda u: u.is_authenticated and (u.is_admin() or u.is_pharmacist()))
def prescription_fill(request, pk):
    from django.utils import timezone
    from .models import Sale
    
    prescription = get_object_or_404(Prescription, pk=pk)
    
    if request.method == 'POST':
        if prescription.filled:
            messages.error(request, 'This prescription has already been filled.')
            return redirect('prescription_list')
            
        medicine = prescription.medicine
        
        if medicine.stock_quantity < prescription.quantity:
            messages.error(request, f'Insufficient stock for {medicine.name}. Only {medicine.stock_quantity} available.')
            return redirect('prescription_detail', pk=pk)
            
        # Deduct stock
        medicine.stock_quantity -= prescription.quantity
        medicine.save()
        
        # Mark as filled
        prescription.filled = True
        prescription.filled_by = request.user
        prescription.filled_date = timezone.now()
        prescription.save()
        
        # Create a sale record
        total_price = medicine.price * prescription.quantity
        Sale.objects.create(
            prescription=prescription,
            medicine=medicine,
            quantity=prescription.quantity,
            total_price=total_price,
            sold_by=request.user
        )
        
        messages.success(request, 'Prescription filled and stock deducted successfully.')
        return redirect('prescription_list')
        
    return render(request, 'prescription_detail.html', {'prescription': prescription})

@login_required
def prescription_detail(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, 'prescription_detail.html', {'prescription': prescription})

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
                messages.success(request, f'Direct sale for {medicine.name} registered. Total: ${sale.total_price}')
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

    context = {
        'top_meds_labels': json.dumps(top_meds_labels),
        'top_meds_data': json.dumps(top_meds_data),
        
        'daily_labels': json.dumps(daily_labels),
        'daily_revenue': json.dumps(daily_revenue),
        
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        
        'monthly_revenue': float(monthly_revenue),
        'total_sales_count': total_sales_count,
        'avg_daily_sales': avg_daily_sales,
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
    writer.writerow(['ID', 'Patient Name', 'Medicine', 'Quantity', 'Date Prescribed', 'Filled', 'Filled By', 'Filled Date'])

    for p in Prescription.objects.all().order_by('-date_prescribed'):
        filled_by = p.filled_by.username if p.filled_by else "N/A"
        filled_date = p.filled_date.strftime('%Y-%m-%d %H:%M:%S') if p.filled_date else "N/A"
        writer.writerow([
            p.id, p.patient_name, p.medicine.name, p.quantity, 
            p.date_prescribed.strftime('%Y-%m-%d %H:%M:%S'), 
            "Yes" if p.filled else "No", filled_by, filled_date
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

@user_passes_test(is_admin_or_assistant)
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

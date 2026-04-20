from django.core.management.base import BaseCommand
from pharmcore.models import Medicine


MEDICINES = [
    # --- Analgesics / Pain Relief ---
    {"name": "Paracetamol", "brand": "Panadol", "category": "Analgesics", "price": 150.00, "stock_quantity": 200, "reorder_level": 30, "expiry_date": "2027-12-31"},
    {"name": "Ibuprofen 400mg", "brand": "Advil", "category": "Analgesics", "price": 250.00, "stock_quantity": 150, "reorder_level": 20, "expiry_date": "2027-06-30"},
    {"name": "Aspirin 300mg", "brand": "Disprin", "category": "Analgesics", "price": 100.00, "stock_quantity": 120, "reorder_level": 20, "expiry_date": "2027-09-30"},
    {"name": "Diclofenac 50mg", "brand": "Voltaren", "category": "Analgesics", "price": 350.00, "stock_quantity": 100, "reorder_level": 15, "expiry_date": "2027-03-31"},
    {"name": "Tramadol 50mg", "brand": "Tramal", "category": "Analgesics", "price": 500.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-01-31"},
    {"name": "Piroxicam 20mg", "brand": "Feldene", "category": "Analgesics", "price": 400.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2026-11-30"},

    # --- Antibiotics ---
    {"name": "Amoxicillin 500mg", "brand": "Amoxil", "category": "Antibiotics", "price": 800.00, "stock_quantity": 100, "reorder_level": 20, "expiry_date": "2027-06-30"},
    {"name": "Amoxicillin-Clavulanate 625mg", "brand": "Augmentin", "category": "Antibiotics", "price": 1500.00, "stock_quantity": 80, "reorder_level": 15, "expiry_date": "2027-04-30"},
    {"name": "Ciprofloxacin 500mg", "brand": "Ciproflox", "category": "Antibiotics", "price": 1200.00, "stock_quantity": 90, "reorder_level": 15, "expiry_date": "2027-05-31"},
    {"name": "Azithromycin 500mg", "brand": "Zithromax", "category": "Antibiotics", "price": 1800.00, "stock_quantity": 70, "reorder_level": 10, "expiry_date": "2027-08-31"},
    {"name": "Metronidazole 400mg", "brand": "Flagyl", "category": "Antibiotics", "price": 300.00, "stock_quantity": 150, "reorder_level": 20, "expiry_date": "2027-07-31"},
    {"name": "Erythromycin 500mg", "brand": "Erythrocin", "category": "Antibiotics", "price": 900.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2026-12-31"},
    {"name": "Tetracycline 250mg", "brand": "Tetracyn", "category": "Antibiotics", "price": 500.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-02-28"},
    {"name": "Doxycycline 100mg", "brand": "Vibramycin", "category": "Antibiotics", "price": 700.00, "stock_quantity": 90, "reorder_level": 15, "expiry_date": "2027-03-31"},
    {"name": "Cotrimoxazole 480mg", "brand": "Septrin", "category": "Antibiotics", "price": 200.00, "stock_quantity": 120, "reorder_level": 20, "expiry_date": "2027-09-30"},

    # --- Antimalarials ---
    {"name": "Artemether-Lumefantrine", "brand": "Coartem", "category": "Antimalarials", "price": 2500.00, "stock_quantity": 100, "reorder_level": 20, "expiry_date": "2027-06-30"},
    {"name": "Chloroquine 250mg", "brand": "Malarex", "category": "Antimalarials", "price": 300.00, "stock_quantity": 150, "reorder_level": 25, "expiry_date": "2027-08-31"},
    {"name": "Quinine 300mg", "brand": "Quinbisul", "category": "Antimalarials", "price": 600.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-01-31"},
    {"name": "Artesunate 200mg", "brand": "Artesunat", "category": "Antimalarials", "price": 1500.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2026-11-30"},

    # --- Antihypertensives ---
    {"name": "Amlodipine 5mg", "brand": "Norvasc", "category": "Cardiovascular", "price": 500.00, "stock_quantity": 120, "reorder_level": 20, "expiry_date": "2027-12-31"},
    {"name": "Lisinopril 10mg", "brand": "Zestril", "category": "Cardiovascular", "price": 450.00, "stock_quantity": 100, "reorder_level": 15, "expiry_date": "2027-10-31"},
    {"name": "Losartan 50mg", "brand": "Cozaar", "category": "Cardiovascular", "price": 700.00, "stock_quantity": 90, "reorder_level": 15, "expiry_date": "2027-09-30"},
    {"name": "Atenolol 50mg", "brand": "Tenormin", "category": "Cardiovascular", "price": 350.00, "stock_quantity": 110, "reorder_level": 15, "expiry_date": "2027-07-31"},
    {"name": "Hydrochlorothiazide 25mg", "brand": "Esidrex", "category": "Cardiovascular", "price": 200.00, "stock_quantity": 130, "reorder_level": 20, "expiry_date": "2027-08-31"},
    {"name": "Methyldopa 250mg", "brand": "Aldomet", "category": "Cardiovascular", "price": 600.00, "stock_quantity": 70, "reorder_level": 10, "expiry_date": "2027-05-31"},
    {"name": "Nifedipine 20mg", "brand": "Adalat", "category": "Cardiovascular", "price": 400.00, "stock_quantity": 85, "reorder_level": 15, "expiry_date": "2027-04-30"},

    # --- Antidiabetics ---
    {"name": "Metformin 500mg", "brand": "Glucophage", "category": "Antidiabetics", "price": 400.00, "stock_quantity": 100, "reorder_level": 20, "expiry_date": "2027-12-31"},
    {"name": "Glibenclamide 5mg", "brand": "Daonil", "category": "Antidiabetics", "price": 250.00, "stock_quantity": 90, "reorder_level": 15, "expiry_date": "2027-11-30"},
    {"name": "Glimepiride 2mg", "brand": "Amaryl", "category": "Antidiabetics", "price": 650.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2027-06-30"},

    # --- Vitamins & Supplements ---
    {"name": "Vitamin C 500mg", "brand": "Emvite C", "category": "Vitamins & Supplements", "price": 200.00, "stock_quantity": 300, "reorder_level": 50, "expiry_date": "2027-12-31"},
    {"name": "Vitamin B Complex", "brand": "Berocca", "category": "Vitamins & Supplements", "price": 350.00, "stock_quantity": 200, "reorder_level": 30, "expiry_date": "2027-10-31"},
    {"name": "Folic Acid 5mg", "brand": "Folate", "category": "Vitamins & Supplements", "price": 150.00, "stock_quantity": 180, "reorder_level": 30, "expiry_date": "2027-09-30"},
    {"name": "Ferrous Sulfate 200mg", "brand": "Feosol", "category": "Vitamins & Supplements", "price": 180.00, "stock_quantity": 150, "reorder_level": 25, "expiry_date": "2027-08-31"},
    {"name": "Zinc Sulfate 20mg", "brand": "Zincovit", "category": "Vitamins & Supplements", "price": 300.00, "stock_quantity": 120, "reorder_level": 20, "expiry_date": "2027-07-31"},
    {"name": "Multivitamin Tablets", "brand": "Cerebe", "category": "Vitamins & Supplements", "price": 700.00, "stock_quantity": 100, "reorder_level": 20, "expiry_date": "2027-12-31"},
    {"name": "Calcium + Vitamin D3", "brand": "Calcimax", "category": "Vitamins & Supplements", "price": 500.00, "stock_quantity": 90, "reorder_level": 15, "expiry_date": "2027-06-30"},

    # --- Antacids & GIT ---
    {"name": "Omeprazole 20mg", "brand": "Losec", "category": "Gastrointestinal", "price": 600.00, "stock_quantity": 120, "reorder_level": 20, "expiry_date": "2027-12-31"},
    {"name": "Ranitidine 150mg", "brand": "Zantac", "category": "Gastrointestinal", "price": 300.00, "stock_quantity": 100, "reorder_level": 15, "expiry_date": "2027-08-31"},
    {"name": "Antacid Suspension", "brand": "Gelusil", "category": "Gastrointestinal", "price": 500.00, "stock_quantity": 80, "reorder_level": 15, "expiry_date": "2027-04-30"},
    {"name": "Metoclopramide 10mg", "brand": "Maxolon", "category": "Gastrointestinal", "price": 250.00, "stock_quantity": 90, "reorder_level": 15, "expiry_date": "2027-03-31"},
    {"name": "Oral Rehydration Salt", "brand": "Dioralyte", "category": "Gastrointestinal", "price": 100.00, "stock_quantity": 300, "reorder_level": 50, "expiry_date": "2027-12-31"},
    {"name": "Loperamide 2mg", "brand": "Imodium", "category": "Gastrointestinal", "price": 350.00, "stock_quantity": 100, "reorder_level": 15, "expiry_date": "2027-10-31"},

    # --- Respiratory ---
    {"name": "Salbutamol Inhaler 100mcg", "brand": "Ventolin", "category": "Respiratory", "price": 2000.00, "stock_quantity": 50, "reorder_level": 10, "expiry_date": "2027-06-30"},
    {"name": "Prednisolone 5mg", "brand": "Deltacortril", "category": "Respiratory", "price": 300.00, "stock_quantity": 100, "reorder_level": 15, "expiry_date": "2027-05-31"},
    {"name": "Promethazine 25mg", "brand": "Phenergan", "category": "Respiratory", "price": 400.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-04-30"},
    {"name": "Chlorphenamine 4mg", "brand": "Piriton", "category": "Respiratory", "price": 150.00, "stock_quantity": 150, "reorder_level": 25, "expiry_date": "2027-08-31"},
    {"name": "Ambroxol Syrup", "brand": "Mucosolvan", "category": "Respiratory", "price": 800.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2027-03-31"},

    # --- Antifungals ---
    {"name": "Fluconazole 150mg", "brand": "Diflucan", "category": "Antifungals", "price": 900.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-07-31"},
    {"name": "Griseofulvin 500mg", "brand": "Grisovin", "category": "Antifungals", "price": 600.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2027-06-30"},
    {"name": "Clotrimazole Cream 1%", "brand": "Canesten", "category": "Antifungals", "price": 700.00, "stock_quantity": 70, "reorder_level": 10, "expiry_date": "2027-09-30"},

    # --- Eye & Ear ---
    {"name": "Chloramphenicol Eye Drops", "brand": "Chloroptic", "category": "Eye & Ear", "price": 500.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2027-04-30"},
    {"name": "Gentamicin Eye Drops", "brand": "Garamycin", "category": "Eye & Ear", "price": 600.00, "stock_quantity": 50, "reorder_level": 10, "expiry_date": "2027-05-31"},

    # --- Skin ---
    {"name": "Hydrocortisone Cream 1%", "brand": "Dermacort", "category": "Dermatology", "price": 400.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-08-31"},
    {"name": "Betamethasone Cream", "brand": "Betnovate", "category": "Dermatology", "price": 600.00, "stock_quantity": 70, "reorder_level": 10, "expiry_date": "2027-07-31"},
    {"name": "Gentian Violet Solution", "brand": "GV Paint", "category": "Dermatology", "price": 200.00, "stock_quantity": 100, "reorder_level": 15, "expiry_date": "2027-12-31"},

    # --- Antiparasitic ---
    {"name": "Albendazole 400mg", "brand": "Zentel", "category": "Antiparasitic", "price": 350.00, "stock_quantity": 150, "reorder_level": 20, "expiry_date": "2027-10-31"},
    {"name": "Ivermectin 6mg", "brand": "Mectizan", "category": "Antiparasitic", "price": 500.00, "stock_quantity": 80, "reorder_level": 10, "expiry_date": "2027-06-30"},
    {"name": "Praziquantel 600mg", "brand": "Biltricide", "category": "Antiparasitic", "price": 800.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2027-05-31"},

    # --- Sedatives / CNS ---
    {"name": "Diazepam 5mg", "brand": "Valium", "category": "CNS", "price": 300.00, "stock_quantity": 60, "reorder_level": 10, "expiry_date": "2027-03-31"},
    {"name": "Phenobarbitone 30mg", "brand": "Luminal", "category": "CNS", "price": 250.00, "stock_quantity": 70, "reorder_level": 10, "expiry_date": "2027-02-28"},
    {"name": "Haloperidol 5mg", "brand": "Haldol", "category": "CNS", "price": 400.00, "stock_quantity": 50, "reorder_level": 10, "expiry_date": "2027-01-31"},
]


class Command(BaseCommand):
    help = "Seed the database with common pharmacy medicines"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing medicines before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            count = Medicine.objects.count()
            Medicine.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing medicine(s).'))

        added = 0
        skipped = 0

        for med in MEDICINES:
            obj, created = Medicine.objects.get_or_create(
                name=med['name'],
                defaults={
                    'brand': med['brand'],
                    'category': med['category'],
                    'price': med['price'],
                    'stock_quantity': med['stock_quantity'],
                    'reorder_level': med['reorder_level'],
                    'expiry_date': med['expiry_date'],
                }
            )
            if created:
                added += 1
                self.stdout.write(f'  + Added: {obj.name}')
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {added} medicine(s) added, {skipped} already existed.'
        ))

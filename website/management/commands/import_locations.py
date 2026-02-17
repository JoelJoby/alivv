import csv
from django.core.management.base import BaseCommand
from website.models import Country, State

class Command(BaseCommand):
    help = 'Import countries and states from CSV files'

    def handle(self, *args, **kwargs):
        self.stdout.write("Importing Countries...")
        
        countries_created = 0
        states_created = 0
        
        try:
            with open('iso_country_codes_sorted.csv', 'r', encoding='utf-8-sig') as file:
                # Using utf-8-sig to handle potential BOM
                reader = csv.DictReader(file)
                
                # Check actual headers
                headers = reader.fieldnames
                self.stdout.write(f"Headers found: {headers}")

                for row in reader:
                    # Clean keys and values
                    clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                    
                    # Logic to find keys even if there are slight variations
                    country_name = clean_row.get('Country')
                    iso2 = clean_row.get('ISO Alpha-2')
                    iso3 = clean_row.get('ISO Alpha-3')
                    
                    # Fallback search for keys if exact match fails
                    if not country_name:
                        for k in clean_row:
                            if 'Country' in k: country_name = clean_row[k]
                    if not iso2:
                         for k in clean_row:
                            if 'Alpha-2' in k: iso2 = clean_row[k]
                    if not iso3:
                         for k in clean_row:
                            if 'Alpha-3' in k: iso3 = clean_row[k]

                    if country_name and iso2:
                        obj, created = Country.objects.get_or_create(
                            name=country_name,
                            defaults={
                                'iso_alpha_2': iso2,
                                'iso_alpha_3': iso3 if iso3 else ''
                            }
                        )
                        if created:
                            countries_created += 1

        except FileNotFoundError:
             self.stderr.write("iso_country_codes_sorted.csv not found.")
             return

        self.stdout.write(f"Created {countries_created} countries.")
        self.stdout.write("Importing Indian States...")
        
        try:
            india = Country.objects.filter(name__iexact='India').first()
            if not india:
                self.stderr.write("India not found in Country list. Cannot import states.")
                return

            with open('indian_states_sorted.csv', 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                    state_name = clean_row.get('State')
                    
                    if not state_name:
                        for k in clean_row:
                            if 'State' in k: state_name = clean_row[k]

                    if state_name:
                        obj, created = State.objects.get_or_create(
                            name=state_name,
                            country=india
                        )
                        if created:
                            states_created += 1
                            
        except FileNotFoundError:
             self.stderr.write("indian_states_sorted.csv not found.")
             return

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {countries_created} countries and {states_created} states.'))

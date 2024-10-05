from django.core.management.base import BaseCommand
from proctorings.views import save_sheet_data_to_model
from proctorings.google_sheets import get_sheet_data  # Import your function

class Command(BaseCommand):
    help = 'Fetch data from Google Sheets and save it to the model.'

    def handle(self, *args, **kwargs):
        # Fetch the data from Google Sheets
        data = get_sheet_data()

        if data is not None:
            # Call your function with the retrieved data
            save_sheet_data_to_model(data)
            self.stdout.write(self.style.SUCCESS('Successfully processed form data.'))
        else:
            self.stdout.write(self.style.WARNING('No data fetched from Google Sheets.'))


#python manage.py run_form_response

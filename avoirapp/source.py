import os
import sys
import logging
import zipfile
# database_backup.py
import os
import sys
import logging
import datetime  # Import datetime module to work with dates
from django.conf import settings
import subprocess
from django.core.mail import EmailMessage
# Get the directory of the script
script_directory = os.path.dirname(os.path.abspath(__file__))
# Set the path to the log file
log_file_path = os.path.join(script_directory, 'daily.log')
# Configure logging to write to the log file
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Add the directory containing the Django project to the Python path
project_root = os.path.abspath(os.path.join(script_directory, '..'))
sys.path.append(project_root)
# Set the Django settings module environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SHERLY.settings")
# Manually configure Django settings
import django
django.setup()
from django.core.mail import EmailMessage

from django.template.loader import render_to_string

if __name__ == "__main__":
    current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_file = f'/home/gestionoptique/Avoir/backup_source_{current_date}.zip'
    source_folder = '/home/gestionoptique/Avoir'
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, source_folder))

        subject = "Backup File"
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        message = f"Backup SOURCE CODE pour : {current_time}."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = ['gestionoptic92@gmail.com']  # Update this with your recipient list
        email = EmailMessage(subject, message, from_email, recipient_list)
        # Attach the zip file to the email
        with open(zip_file, 'rb') as attachment:
            email.attach(f'backup_source_{current_time}.zip', attachment.read(), 'application/zip')
        # Send the email
        email.send()
        os.remove(zip_file)  # Remove the zip file after sending the email
        print("Email sent successfully.")
    except Exception as e:
        print(f"An error occurred while creating zip file or sending email: {str(e)}")



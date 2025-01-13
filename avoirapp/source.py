import os
import sys
import logging
import datetime
import zipfile
from django.conf import settings
from django.core.mail import EmailMessage

# Constants
MAX_EMAIL_SIZE = 25 * 1024 * 1024  # 25 MB limit for Gmail
ZIP_FILE_PATH_TEMPLATE = '/home/gestionoptique/Avoir/backup_source_{timestamp}.zip'
SOURCE_FOLDER = '/home/gestionoptique/Avoir'

# Logging configuration
script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, 'source.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    try:
        # Generate current timestamp and zip file path
        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_file_path = ZIP_FILE_PATH_TEMPLATE.format(timestamp=current_date)

        # Create the zip file
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(SOURCE_FOLDER):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, SOURCE_FOLDER))

        # Check the zip file size
        zip_file_size = os.path.getsize(zip_file_path)
        if zip_file_size > MAX_EMAIL_SIZE:
            logging.warning(f"Zip file size exceeds Gmail limit: {zip_file_size} bytes.")
            print(f"Zip file size ({zip_file_size} bytes) exceeds the email limit. Please upload the file to a cloud storage service.")
        else:
            # Send the email with the zip file attached
            subject = "Backup File"
            message = f"Backup SOURCE CODE pour : {current_date}."
            from_email = settings.EMAIL_HOST_USER
            recipient_list = ['gestionoptic92@gmail.com']

            email = EmailMessage(subject, message, from_email, recipient_list)
            with open(zip_file_path, 'rb') as attachment:
                email.attach(f'backup_source_{current_date}.zip', attachment.read(), 'application/zip')
            email.send()

            logging.info("Email sent successfully.")
            print("Email sent successfully.")

        # Clean up by removing the zip file
        os.remove(zip_file_path)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print(f"An error occurred while creating zip file or sending email: {str(e)}")

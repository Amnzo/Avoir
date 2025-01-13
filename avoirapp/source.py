import os
import sys
import logging
import datetime
import zipfile
from django.conf import settings
from django.core.mail import EmailMessage
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Constants
MAX_EMAIL_SIZE = 25 * 1024 * 1024  # 25 MB limit for Gmail
ZIP_FILE_PATH_TEMPLATE = '/home/gestionoptique/Avoir/backup_source_{timestamp}.zip'
SOURCE_FOLDER = '/home/gestionoptique/Avoir'

# Logging configuration
script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, 'source.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_zip_file(source_folder, zip_file_path):
    """Create a zip file containing the source folder."""
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, source_folder))
    return os.path.getsize(zip_file_path)

def upload_to_google_drive(zip_file_path, file_name):
    """Upload the zip file to Google Drive and return the download link."""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Follow authentication steps
    drive = GoogleDrive(gauth)

    upload_file = drive.CreateFile({'title': file_name})
    upload_file.SetContentFile(zip_file_path)
    upload_file.Upload()
    return upload_file['alternateLink']

def send_email(subject, message, recipient_list):
    """Send an email with the specified subject and message."""
    from_email = settings.EMAIL_HOST_USER
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.send()

if __name__ == "__main__":
    try:
        # Generate current timestamp and zip file path
        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_file_path = ZIP_FILE_PATH_TEMPLATE.format(timestamp=current_date)
        file_name = f'backup_source_{current_date}.zip'

        # Create the zip file
        zip_file_size = create_zip_file(SOURCE_FOLDER, zip_file_path)

        # Check the zip file size
        if zip_file_size > MAX_EMAIL_SIZE:
            logging.info(f"Zip file size ({zip_file_size} bytes) exceeds email limit. Uploading to Google Drive...")

            # Upload the file to Google Drive
            download_link = upload_to_google_drive(zip_file_path, file_name)

            # Send an email with the Google Drive link
            subject = "Backup File Available"
            message = f"The backup file is too large to send via email. You can download it from the following link:\n\n{download_link}"
            recipient_list = ['gestionoptic92@gmail.com']  # Update with recipient email(s)
            send_email(subject, message, recipient_list)

            logging.info(f"Backup uploaded to Google Drive and link emailed: {download_link}")
            print(f"Backup uploaded to Google Drive. Download link sent to {recipient_list}.")
        else:
            # Send the email with the zip file attached
            subject = "Backup File"
            message = f"Backup SOURCE CODE pour : {current_date}."
            recipient_list = ['gestionoptic92@gmail.com']

            email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            with open(zip_file_path, 'rb') as attachment:
                email.attach(file_name, attachment.read(), 'application/zip')
            email.send()

            logging.info("Email sent successfully.")
            print("Email sent successfully.")

        # Clean up by removing the zip file
        os.remove(zip_file_path)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")

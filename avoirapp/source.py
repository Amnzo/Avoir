



import math
import zipfile
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
log_file_path = os.path.join(script_directory, 'source.log')
# Configure logging to write to the log file
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Add the directory containing the Django project to the Python path
project_root = os.path.abspath(os.path.join(script_directory, '..'))
sys.path.append(project_root)
# Set the Django settings module environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Avoir.settings")
# Manually configure Django settings
import django
django.setup()
from django.core.mail import EmailMessage

from django.template.loader import render_to_string

# Constants
CHUNK_SIZE = 25 * 1024 * 1024  # 25 MB per zip file
SOURCE_FOLDER = '/home/gestionoptique/Avoir'
ZIP_FILE_PATH_TEMPLATE = '/home/gestionoptique/Avoir/backup_source_{timestamp}.zip'

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

def split_zip(zip_file_path, chunk_size):
    """Split a zip file into smaller chunks."""
    zip_files = []

    with zipfile.ZipFile(zip_file_path, 'r') as source_zip:
        files = source_zip.namelist()
        total_size = sum(source_zip.getinfo(f).file_size for f in files)
        chunks = math.ceil(total_size / chunk_size)

        for i in range(chunks):
            chunk_zip_file = f"{zip_file_path}_part{i+1}.zip"
            with zipfile.ZipFile(chunk_zip_file, 'w', zipfile.ZIP_DEFLATED) as chunk_zip:
                current_size = 0
                while files and current_size < chunk_size:
                    file = files.pop(0)
                    file_data = source_zip.read(file)
                    chunk_zip.writestr(file, file_data)
                    current_size += len(file_data)

            zip_files.append(chunk_zip_file)

    return zip_files

def send_email_with_attachments(subject, message, recipient_list, attachments):
    """Send an email with multiple attachments."""
    from_email = settings.EMAIL_HOST_USER
    email = EmailMessage(subject, message, from_email, recipient_list)
    for attachment in attachments:
        with open(attachment, 'rb') as file:
            email.attach(os.path.basename(attachment), file.read(), 'application/zip')
    email.send()



if __name__ == "__main__":
    try:
        # Generate current timestamp and zip file path
        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_file_path = ZIP_FILE_PATH_TEMPLATE.format(timestamp=current_date)

        # Step 1: Create the zip file
        logging.info(f"Creating zip file at {zip_file_path}.")
        create_zip_file(SOURCE_FOLDER, zip_file_path)

        # Step 2: Split the zip file into chunks
        logging.info(f"Splitting zip file into chunks (if required).")
        zip_chunks = split_zip(zip_file_path, CHUNK_SIZE)

        # Step 3: Prepare and send the email (only with the chunks)
        logging.info("Preparing email with zip chunks.")
        subject = "Backup Files"
        message = f"Backup source code for: {current_date}."
        recipient_list = ['gestionoptic92@gmail.com']  # Update with your recipients
        send_email_with_attachments(subject, message, recipient_list, zip_chunks)

        # Step 4: Clean up the zip file and chunks
        logging.info("Cleaning up generated files.")
        os.remove(zip_file_path)  # Delete the original zip file
        for chunk in zip_chunks:
            os.remove(chunk)  # Delete each chunk

        # Step 5: Log success
        logging.info("Backup and email process completed successfully.")
        print("Backup and email process completed successfully.")

    except Exception as e:
        # Log and print any errors
        logging.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")







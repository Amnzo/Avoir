import os
import sys
import logging
import datetime
import subprocess
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# Configuration de l'emplacement des logs
script_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(script_directory, 'backup.log')

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration Django
project_root = os.path.abspath(os.path.join(script_directory, '..'))
sys.path.append(project_root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Avoir.settings")

import django
django.setup()

# Fonction pour créer une sauvegarde de la base de données
def create_backup():
    try:
        database_settings = settings.DATABASES['default']
        db_user = database_settings['USER']
        db_password = database_settings['PASSWORD']
        db_host = database_settings['HOST']
        db_name = database_settings['NAME']

        current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{script_directory}/backup_{current_date}.sql"

        command = [
            "mysqldump",
            "-u", db_user,
            f"-p{db_password}",
            "-h", db_host,
            "--single-transaction",
            "--no-tablespaces",
            "--column-statistics=0",
            db_name
        ]

        with open(backup_path, "w") as backup_file:
            subprocess.run(command, stdout=backup_file, check=True)

        logging.info("Backup successful: %s", backup_path)
        return backup_path
    except subprocess.CalledProcessError as e:
        logging.error("Backup failed: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
    return None

# Fonction pour envoyer un email avec la sauvegarde
def send_email_with_attachment(file_path):
    try:
        email_settings = settings.EMAIL_HOST_USER

        subject = "Database Backup"
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Backup de la base de données réalisé avec succès le {current_date}."
        recipient_list = ['gestionoptic92@gmail.com']

        email = EmailMessage(subject, message, email_settings, recipient_list)
        email.attach_file(file_path)
        email.send()

        os.remove(file_path)
        logging.info("Email sent successfully to: %s", recipient_list)
    except Exception as e:
        logging.error("Error sending email: %s", e)

import zipfile

def compress_file(file_path):
    zip_path = f"{file_path}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    os.remove(file_path)  # Supprime le fichier SQL brut après compression
    return zip_path

# Exécution principale
if __name__ == "__main__":
    backup_file_path = create_backup()
    if backup_file_path:
        compressed_file_path = compress_file(backup_file_path)  # Compresse le fichier
        send_email_with_attachment(compressed_file_path)

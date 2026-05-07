import csv
from apps.scraping.models import JobOffer

def import_jobs(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)

        for row in reader:
            title = row.get('title', '') or row.get('job_title', '') or row.get('poste', '')
            company = row.get('company', '') or row.get('entreprise', '')
            description = row.get('description', '') or row.get('desc', '') or row.get('job_description', '')
            location = row.get('location', '') or row.get('city', '') or row.get('localisation', '')
            source_url = row.get('source_url', '') or row.get('url', '')
            published_date = row.get('date_start', '') or row.get('published_date', '')

            JobOffer.objects.create(
                title=title,
                company=company,
                sector=row.get('sector', ''),
                location=location,
                skills_required=row.get('skills_required', ''),
                experience_required=row.get('experience_required', ''),
                contract_type=row.get('contract_type', ''),
                description=description,
                source_url=source_url,
            )

    print("Jobs imported successfully!")
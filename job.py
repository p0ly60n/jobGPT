import csv

class Job:
    def __init__(self, job_title, job_company, job_location, job_link, job_text):
        self.job_title = job_title
        self.job_company = job_company
        self.job_location = job_location
        self.job_link = job_link
        self.job_text = job_text

    def __str__(self):
        return f"{self.job_title} @ {self.job_company}"

    def __repr__(self):
        return f"{self.job_title} @ {self.job_company}"

    def formatted(self):
        return \
        f'''{self.job_title} bei {self.job_company}
        Standort:
        {self.job_location}
        Link: 
        {self.job_link}
        Text:
        {self.job_text}'''

    def write_to_file(self, file_path):
        # writing to the CSV-file
        with open(file_path, mode="w", encoding="utf8") as file:
            writer = csv.writer(file, delimiter=",", lineterminator="\n")
            
            # Writing to CSV-file the job data
            writer.writerow([self.job_title, self.job_company, self.job_location, self.job_link, self.job_text])
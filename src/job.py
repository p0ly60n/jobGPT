import csv

class Job:
    def __init__(self, job_title: str, job_company: str, job_location: str, job_link: str, job_text: str):
        """
        Initializes a Job object with the given parameters.

        Args:
            job_title (str): The title of the job.
            job_company (str): The company offering the job.
            job_location (str): The location of the job.
            job_link (str): The link to the job posting.
            job_text (str): The text of the job posting.
        """
        self.job_title = job_title
        self.job_company = job_company
        self.job_location = job_location
        self.job_link = job_link
        self.job_text = job_text

    def __str__(self):
        """
        Returns a string representation of the Job object.

        Returns:
            str: A string representation of the Job object.
        """
        return f"{self.job_title} @ {self.job_company}"

    def __repr__(self):
        """
        Returns a string representation of the Job object.

        Returns:
            str: A string representation of the Job object.
        """
        return f"{self.job_title} @ {self.job_company}"

    def formatted(self):
        """
        Returns a formatted string representation of the Job object used for openAI requests.

        Returns:
            str: A formatted string representation of the Job object.
        """
        return \
        f"""{self.job_title} bei {self.job_company}
        Standort:
        {self.job_location}
        Link: 
        {self.job_link}
        Text:
        {self.job_text}"""

    def write_to_file(self, file_path: str):
        """
        Writes the job data to a CSV file.

        Args:
            file_path (str): The path to the CSV file.
        """
        # writing to the CSV-file
        with open(file_path, mode="a", encoding="utf8") as file:
            writer = csv.writer(file, delimiter=",", lineterminator="\n")
            
            # Writing to CSV-file the job data
            writer.writerow([self.job_title, self.job_company, self.job_location, self.job_link])
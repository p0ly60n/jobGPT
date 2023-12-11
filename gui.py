"""A graphical user interface for the job scraper and cover letter generator."""
import webbrowser
import csv
import os
from threading import Thread

import customtkinter as ctk
from customtkinter import filedialog
from CTkMessagebox import CTkMessagebox
from pypdf import PdfReader

import src.scraper as scraper
import src.gpt as gpt

class App(ctk.CTk):
    """A graphical user interface for a job scraper and cover letter generator."""

    def __init__(self):
        """Initializes the GUI and sets up the main window."""
        super().__init__()
        self.title("Job-Scraper")
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("system")

        self.website_choices = ["Stepstone", "Indeed"]
        self.website_choice = ctk.StringVar()
        self.website_choice.set(self.website_choices[0])

        self.interest_label = ctk.CTkLabel(self, text="Interest")
        self.location_label = ctk.CTkLabel(self, text="Location")
        self.radius_label = ctk.CTkLabel(self, text="Radius")
        self.no_of_jobs_label = ctk.CTkLabel(self, text="#Jobs")
        self.resume_label = ctk.CTkLabel(self, text="Resume")
        self.website_label = ctk.CTkLabel(self, text="Website")

        self.interest_field = ctk.CTkEntry(self)
        self.location_field = ctk.CTkEntry(self)
        self.radius_field = ctk.CTkEntry(self)
        self.no_of_jobs_field = ctk.CTkEntry(self)
        self.resume_field = ctk.CTkButton(self, text="Choose File", command=self.file_open)

        self.interest_label.grid(row=0, column=0, padx=5, pady=5)
        self.location_label.grid(row=1, column=0, padx=5, pady=5)
        self.radius_label.grid(row=2, column=0, padx=5, pady=5)
        self.no_of_jobs_label.grid(row=3, column=0, padx=5, pady=5)
        self.resume_label.grid(row=4, column=0, padx=5, pady=5)
        self.website_label.grid(row=5, column=0, padx=5, pady=5)

        self.interest_field.grid(row=0, column=1, padx=5, pady=5)
        self.location_field.grid(row=1, column=1, padx=5, pady=5)
        self.radius_field.grid(row=2, column=1, padx=5, pady=5)
        self.no_of_jobs_field.grid(row=3, column=1, padx=5, pady=5)
        self.resume_field.grid(row=4, column=1, padx=5, pady=5)

        ctk.CTkOptionMenu(self, variable=self.website_choice, values=self.website_choices).grid(row=5, column=1, padx=5, pady=5)

        self.scrape_button = ctk.CTkButton(self, text="Scrape", command=self.scrape)
        self.scrape_button.grid(row=6, column=1, padx=5, pady=5)

        # getting the working root directory
        self.directory = os.getcwd() + "/"
        # creating the output directory if it does not exist
        if not os.path.exists(self.directory + "/output"):
            os.mkdir(self.directory + "/output")
            print(f"Directory added at {self.directory + '/output'}")

        self.csv_file_name = ""
        self.personal_info = ""
        self.jobs = []
        self.resume_file = ""

        self.mainloop()

    def scrape(self):
        """Scrapes job data from a website based on user input and saves it to a CSV file."""
        #self.scrape_button.configure(state="disabled", text="Scraping...")
        interest = self.interest_field.get().strip()
        location = self.location_field.get().strip()
        radius = int(self.radius_field.get())
        no_of_jobs = int(self.no_of_jobs_field.get())
        resume_file = self.resume_file

        print(f"\nExtracting data of {resume_file}...\n")
        self.extract_personal_info(resume_file)

        print("\nScraping...\n")

        # create a scraper object based on the user's choice
        website_scraper = None
        choice = self.website_choice.get()
        if (choice == "Stepstone"):
            website_scraper = scraper.StepstoneScraper(interest.replace(" ", "%20"), \
            location.replace(" ", "%20"), radius, no_of_jobs)
        elif (choice == "Indeed"):
            website_scraper = scraper.IndeedScraper(interest.replace(" ", "%20"), \
            location.replace(" ", "%20"), radius, no_of_jobs)
        else:
            print("Website not supported yet, edit gui.py!")

        # run the scraper to extract the job data from the website
        self.jobs = website_scraper.scrape()

        print("\nScraping done!\n")

        self.csv_file_name = interest.title() + "_" + location.title() + "_Jobs.csv"

        self.save_csv()

        JobWindow(self.jobs, self.directory)

    def save_csv(self):
        """Saves the scraped job data to a CSV file."""
        with open(f"{self.directory}/output/{self.csv_file_name}", mode="w", encoding="utf8") as csv_file:
            writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
            writer.writerow(["TITLE", "COMPANY", "LOCATION", "LINK"])

        for job in self.jobs:
            job.write_to_file(f"{self.directory}/output/{self.csv_file_name}")

    def file_open(self):
        """Opens a file dialog to select a file."""
        filename = filedialog.askopenfilename(initialdir=self.directory, title="Select a file", filetypes=(("PDF files", "*.pdf"), ("TXT files", "*.txt")))
        if (os.path.basename(filename)) != "":
            self.resume_field.configure(text=os.path.basename(filename))
            self.resume_file = filename

    def extract_personal_info(self, resume_file):
        """Extracts personal information from a cover letter PDF or TXT file."""
        # if a resume is available, extract the text from it
        if (resume_file != ""):
            if (os.path.splitext(resume_file)[1] == ".txt"):
                with open(resume_file, mode="r", encoding="utf8") as txt_file:
                    self.personal_info = txt_file.read()
            elif (os.path.splitext(resume_file)[1] == ".pdf"):
                reader = PdfReader(resume_file)
                for page in reader.pages:
                    self.personal_info += page.extract_text()
            else:
                print("File format not supported yet, edit gui.py!")
        else:
            print("No resume selected!")


class JobWindow(ctk.CTkToplevel):
    def __init__(self, jobs, directory):
        super().__init__()
        self.title("Jobs")
        self.jobs = jobs
        self.selected = []
        self.directory = directory
        self.personal_info = ""

        self.resume_needed_label = ctk.CTkLabel(self, text="RESUME?")
        self.title_label = ctk.CTkLabel(self, text="TITLE")
        self.company_label = ctk.CTkLabel(self, text="COMPANY")
        self.location_label = ctk.CTkLabel(self, text="LOCATION")
        self.link_label = ctk.CTkLabel(self, text="LINK")

        self.resume_needed_label.grid(row=0, column=0, padx=40, sticky="WE", pady=5)
        self.title_label.grid(row=0, column=1, padx=40, sticky="WE", pady=5)
        self.company_label.grid(row=0, column=2, padx=40, sticky="WE", pady=5)
        self.location_label.grid(row=0, column=3, padx=40, sticky="WE", pady=5)
        self.link_label.grid(row=0, column=4, padx=40, sticky="WE", pady=5)



        for idx, job in enumerate(self.jobs, start=0):
            var = ctk.IntVar()
            self.selected.append(var)
            ctk.CTkCheckBox(self, variable=var, text="", width=30).grid(row=idx+1, column=0, padx=5, pady=5)
            ctk.CTkLabel(self, text=job.job_title[0:30]+"...").grid(row=idx+1, column=1, sticky="W", padx=5, pady=5)
            ctk.CTkLabel(self, text=job.job_company[0:30]+"...").grid(row=idx+1, column=2, sticky="W", padx=5, pady=5)
            ctk.CTkLabel(self, text=job.job_location[0:30]+"...").grid(row=idx+1, column=3, sticky="W", padx=5, pady=5)
            ctk.CTkButton(self, text="Link", command=lambda link=job.job_link: self.callback(link)).grid(row=idx+1, column=4, padx=5, pady=5)

        self.generate_button = ctk.CTkButton(self, text="Generate", command=self.generate_letter)
        self.generate_button.grid(row=len(self.jobs) + 1, column=4, padx=5, pady=5)

    def callback(self, link):
        """Opens a web browser with the provided link."""
        webbrowser.open_new(link)


    def start_gpt_generation_threaded(self, job, job_index, personal_info):
        """Generates a cover letter using GPT-3 for a specific job in a separate thread."""
        with open(f"{self.directory}/output/job{job_index}@{job.job_company}.txt", mode="w", encoding="utf8") as txt_file:
            # get the resume
            gpt_data = gpt.get_letter(job, personal_info)
            txt_file.write(gpt_data["message"])
            print(f"Cover-Letter for job{job_index} ({job}) generated!")
            print(f"-> Tokens: in:{gpt_data['input_tokens']}, out:{gpt_data['output_tokens']}")

    def generate_letter(self):
        """Generates cover letters for selected jobs using GPT-3."""
        #self.generate_button.configure(state="disabled", text="Generating...")
        threads = []
        for idx, job in enumerate(self.jobs, start=0):     
            if self.selected[idx].get() == 1:
                threads.append(Thread(target=self.start_gpt_generation_threaded, args=(job, idx, self.personal_info)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        CTkMessagebox(title="Success", message="Cover letters generated! Find them in the output folder.", \
            icon="check")
        self.destroy()
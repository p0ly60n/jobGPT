from tkinter import Tk, Label, Entry, Button, OptionMenu, Toplevel, Checkbutton, StringVar, IntVar, mainloop
from tkinter import filedialog
from tkinter.messagebox import showinfo

import csv
import os
from threading import Thread
from pypdf import PdfReader
import webbrowser

import src.scraper as scraper
import src.gpt as gpt
from src.job import Job

class GUI:
    """A graphical user interface for a job scraper and cover letter generator."""

    def scrape(self):
        """Scrapes job data from a website based on user input and saves it to a CSV file."""
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

        self.display_jobs()

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

    def display_jobs(self):
        """Displays the scraped job data in a new window."""
        self.job_window = Toplevel(self.master)
        self.job_window.resizable(width=False, height=False)
        self.job_window.title("Jobs")

        Label(self.job_window, text="RESUME?").grid(row=0, column=0, padx=40, sticky="WE")
        Label(self.job_window, text="TITLE").grid(row=0, column=1, padx=40, sticky="WE")
        Label(self.job_window, text="COMPANY").grid(row=0, column=2, padx=40, sticky="WE")
        Label(self.job_window, text="LOCATION").grid(row=0, column=3, padx=40, sticky="WE")
        Label(self.job_window, text="LINK").grid(row=0, column=4, padx=40, sticky="WE")


        for idx, job in enumerate(self.jobs, start=0):
            var = IntVar()
            self.selected.append(var)
            Checkbutton(self.job_window, variable=var, cursor="hand2").grid(row=idx+1, column=0)
            Label(self.job_window, text=job.job_title[0:30]+"...").grid(row=idx+1, column=1, sticky="W")
            Label(self.job_window, text=job.job_company[0:30]+"...").grid(row=idx+1, column=2, sticky="W")
            Label(self.job_window, text=job.job_location[0:30]+"...").grid(row=idx+1, column=3, sticky="W")
            Button(self.job_window, text="Link", fg="blue", cursor="hand2", command=lambda link=job.job_link: self.callback(link)).grid(row=idx+1, column=4)

        Button(self.job_window, text="Generate", command=self.generate_letter, cursor="hand2").grid(row=len(self.jobs) + 1, column=4, padx=5, pady=5, sticky="E")

    def save_csv(self):
        """Saves the scraped job data to a CSV file."""
        with open(f"{self.directory}/output/{self.csv_file_name}", mode="w", encoding="utf8") as csv_file:
            writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
            writer.writerow(["TITLE", "COMPANY", "LOCATION", "LINK"])

        for job in self.jobs:
            job.write_to_file(f"{self.directory}/output/{self.csv_file_name}")

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
        threads = []
        for idx, job in enumerate(self.jobs, start=0):     
            if self.selected[idx].get() == 1:
                threads.append(Thread(target=self.start_gpt_generation_threaded, args=(job, idx, self.personal_info)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        showinfo("Success", "Cover letters generated! Find them in the output folder.")
        self.job_window.destroy()

    def file_open(self):
        """Opens a file dialog to select a file."""
        filename = filedialog.askopenfilename(initialdir=self.directory, title="Select a file", filetypes=(("PDF files", "*.pdf"), ("TXT files", "*.txt")))
        if (os.path.basename(filename)) != "":
            self.resume_field.config(text=os.path.basename(filename))
            self.resume_file = filename


    def __init__(self):
        """Initializes the GUI and sets up the main window."""
        self.master = Tk()
        self.master.title("Job-Scraper")

        self.website_choices = ["Stepstone", "Indeed"]
        self.website_choice = StringVar(self.master)
        self.website_choice.set(self.website_choices[0])

        Label(self.master, text="Interest").grid(row=0)
        Label(self.master, text="Location").grid(row=1)
        Label(self.master, text="Radius").grid(row=2)
        Label(self.master, text="#Jobs").grid(row=3)
        Label(self.master, text="Resume").grid(row=4)
        Label(self.master, text="Website").grid(row=5)

        self.interest_field = Entry(self.master, cursor="xterm")
        self.location_field = Entry(self.master, cursor="xterm")
        self.radius_field = Entry(self.master, cursor="xterm")
        self.no_of_jobs_field = Entry(self.master, cursor="xterm")
        self.resume_field = Button(self.master, text="Choose File", command=self.file_open, cursor="hand2")

        self.interest_field.grid(row=0, column=1)
        self.location_field.grid(row=1, column=1)
        self.radius_field.grid(row=2, column=1)
        self.no_of_jobs_field.grid(row=3, column=1)
        self.resume_field.grid(row=4, column=1)

        OptionMenu(self.master, self.website_choice, *self.website_choices).grid(row=5, column=1, padx=5, pady=5)

        Button(self.master, text="Scrape", command=self.scrape, cursor="hand2").grid(row=6, column=1, padx=5, pady=5, sticky="E")

        # getting the working root directory
        self.directory = os.getcwd() + "/"
        # creating the output directory if it does not exist
        if not os.path.exists(self.directory + "/output"):
            os.mkdir(self.directory + "/output")
            print(f"Directory added at {self.directory + '/output'}")

        self.csv_file_name = ""
        self.personal_info = ""
        self.jobs = []
        self.selected = []
        self.resume_file = ""
        self.job_window = None

        mainloop()
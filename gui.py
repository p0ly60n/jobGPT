from tkinter import *

import csv
import os
from threading import Thread
from pypdf import PdfReader
import webbrowser

import src.scraper as scraper
import src.gpt as gpt
from src.job import Job

class GUI:
    def scrape(self):
        interest = self.interest_field.get().strip().replace(" ", "+")
        location = self.location_field.get().strip().replace(" ", "+")
        radius = int(self.radius_field.get())
        no_of_jobs = int(self.no_of_jobs_field.get())
        cover_letter_file = self.cover_letter_field.get()

        print(f"\nExtracting data of {cover_letter_file}...\n")
        self.extract_personal_info(cover_letter_file)
        
        print("\nScraping...\n")
        # run the scraper to extract the job data from the website
        stepstone_scraper = scraper.StepstoneScraper(interest, location, radius, no_of_jobs)
        self.jobs = stepstone_scraper.scrape()

        print("\nScraping done!\n")

        self.csv_file_name = interest.title() + "_" + location.title() + "_Jobs.csv"

        self.save_csv()

        self.display_jobs()

    def extract_personal_info(self, cover_letter_file):
        # if a resume is available, extract the text from it
        if (cover_letter_file != ""):
            reader = PdfReader(cover_letter_file)
            for page in reader.pages:
                self.personal_info += page.extract_text()

    def display_jobs(self):
        job_window = Toplevel(self.master)
        job_window.resizable(width=False, height=False)

        Label(job_window, text="RESUME?").grid(row=0, column=0, padx=40, sticky="WE")
        Label(job_window, text="TITLE").grid(row=0, column=1, padx=40, sticky="WE")
        Label(job_window, text="COMPANY").grid(row=0, column=2, padx=40, sticky="WE")
        Label(job_window, text="LOCATION").grid(row=0, column=3, padx=40, sticky="WE")
        Label(job_window, text="LINK").grid(row=0, column=4, padx=40, sticky="WE")

        for idx, job in enumerate(self.jobs, start=0):
            var = IntVar()
            self.selected.append(var)
            Checkbutton(job_window, variable=var).grid(row=idx+1, column=0)
            Label(job_window, text=job.job_title[0:30]+"...").grid(row=idx+1, column=1, sticky="W")
            Label(job_window, text=job.job_company[0:30]+"...").grid(row=idx+1, column=2, sticky="W")
            Label(job_window, text=job.job_location[0:30]+"...").grid(row=idx+1, column=3, sticky="W")
            link = Label(job_window, text="click here", fg="blue")
            link.grid(row=idx+1, column=4)
            link.bind("<Button-1>", lambda e: self.callback)

    def save_csv(self):
        with open(f"{self.directory}/output/{self.csv_file_name}", mode="w", encoding="utf8") as csv_file:
            writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
            writer.writerow(["TITLE", "COMPANY", "LOCATION", "LINK"])

        for job in self.jobs:
            job.write_to_file(f"{self.directory}/output/{self.csv_file_name}")

    def callback(self, link):
        webbrowser.open_new(link)

    def start_gpt_generation_threaded(self, job, job_index, personal_info):
        with open(f"{self.directory}/output/job{job_index}@{job.job_company}.txt", mode="w", encoding="utf8") as txt_file:
            # get the resume
            gpt_data = gpt.get_letter(job, personal_info)
            txt_file.write(gpt_data["message"])
            print(f"Cover-Letter for job{job_index} ({job}) generated!")
            print(f"-> Tokens: in:{gpt_data["input_tokens"]}, out:{gpt_data["output_tokens"]}")


    def generate_letter(self):
        threads = []
        for idx, job in enumerate(self.jobs, start=0):     
            if self.selected[idx].get() == 1:
                threads.append(Thread(target=self.start_gpt_generation_threaded, args=(job, idx, self.personal_info)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()


    def __init__(self):
        self.master = Tk()

        Label(self.master, text="Interest").grid(row=0)
        Label(self.master, text="Location").grid(row=1)
        Label(self.master, text="Radius").grid(row=2)
        Label(self.master, text="#Jobs").grid(row=3)
        Label(self.master, text="Cover-Letter").grid(row=4)

        self.interest_field = Entry(self.master)
        self.location_field = Entry(self.master)
        self.radius_field = Entry(self.master)
        self.no_of_jobs_field = Entry(self.master)
        self.cover_letter_field = Entry(self.master)

        self.interest_field.grid(row=0, column=1)
        self.location_field.grid(row=1, column=1)
        self.radius_field.grid(row=2, column=1)
        self.no_of_jobs_field.grid(row=3, column=1)
        self.cover_letter_field.grid(row=4, column=1)

        Button(self.master, text="Scrape", command=self.scrape).grid(row=5, column=0, sticky="WE", pady=4)
        Button(self.master, text="Generate", command=self.generate_letter).grid(row=5, column=1, sticky="WE", pady=4)

        # getting the working root directory
        self.directory = os.getcwd() + "/"
        # creating the output directory if it does not exist
        if not os.path.exists(self.directory + "/output"):
            os.mkdir(self.directory + "/output")
            print(f"Directory added at {self.directory + "/output"}")

        self.csv_file_name = ""
        self.personal_info = ""
        self.jobs = []
        self.selected = []

        mainloop()
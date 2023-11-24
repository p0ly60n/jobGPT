import csv
import os
from pypdf import PdfReader

import src.scraper as scraper
import src.gpt as gpt

if __name__ == "__main__":
    # search queries
    interest = input("Interest: ").strip().replace(" ", "+")
    location = input("Location: ").strip().replace(" ", "+")
    radius = int(input("Radius: "))
    no_of_jobs = int(input("#Jobs: "))
    pdf_file = input("Resume-File <.pdf> (leave blank if none available): ").strip()

    # getting the working root directory
    directory = os.getcwd() + "/"

    csv_file_name = interest.title() + "_" + location.title() + "_Jobs.csv"

    # creating the output directory if it does not exist
    if not os.path.exists(directory + "/output"):
        os.mkdir(directory + "/output")
        print(f"Directory added at {directory + "/output"}")

    # writing the labels to the CSV-file
    with open(f"{directory}/output/{csv_file_name}", mode="w", encoding="utf8") as csv_file:
        writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
        writer.writerow(["TITLE", "COMPANY", "LOCATION", "LINK"])

    print("\nScraping...\n")

    # run the scraper to extract the job data from the website
    jobs = scraper.extract_data(interest, location, radius, no_of_jobs)

    # writing the job data to the CSV-file
    for job in jobs:
        job.write_to_file(f"{directory}/output/{csv_file_name}")

    # if a resume is available, extract the text from it

    print("\nExtracting data of .pdf file if given...\n")

    personal_info = ""
    if (pdf_file != ""):
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            personal_info += page.extract_text()

    print("\nGenerating Cover-Letter...\n")

    for idx, job in enumerate(jobs):
        with open(f"{directory}/output/job{idx}.txt", mode="w", encoding="utf8") as txt_file:
            # get the resume
            txt_file.write(gpt.get_letter(job, personal_info))
            print(f"Cover-Letter for job{idx} ({job}) generated!")

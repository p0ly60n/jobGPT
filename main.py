import csv
import os
from threading import Thread
from pypdf import PdfReader

import src.scraper as scraper
import src.gpt as gpt

def start_gpt_generation_threaded(job, job_index, personal_info, directory):
    with open(f"{directory}/output/job{job_index}@{job.job_company}.txt", mode="w", encoding="utf8") as txt_file:
        # get the resume
        gpt_data = gpt.get_letter(job, personal_info)
        txt_file.write(gpt_data["message"])
        print(f"Cover-Letter for job{job_index} ({job}) generated!")
        print(f"-> Tokens: in:{gpt_data["input_tokens"]}, out:{gpt_data["output_tokens"]}")


if __name__ == "__main__":
    # search queries
    interest = input("Interest: ").strip().replace(" ", "+")
    location = input("Location: ").strip().replace(" ", "+")
    radius = int(input("Radius: "))
    no_of_jobs = int(input("#Jobs: "))
    pdf_file = input("Resume-File <.pdf> (leave blank if none available): ").strip()


    # getting the working root directory
    directory = os.getcwd() + "/"
    # creating the output directory if it does not exist
    if not os.path.exists(directory + "/output"):
        os.mkdir(directory + "/output")
        print(f"Directory added at {directory + "/output"}")


    # writing the labels to the CSV-file
    csv_file_name = interest.title() + "_" + location.title() + "_Jobs.csv"
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
    personal_info = ""
    if (pdf_file != ""):
        print(f"\nExtracting data of {pdf_file}...\n")
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            personal_info += page.extract_text()


    print("\nGenerating Cover-Letter...\n")
    # generate the cover letter for each job by using threading
    threads = [Thread(target=start_gpt_generation_threaded, args=(job, idx, personal_info, directory)) for idx, job in enumerate(jobs)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print("\nDone!")
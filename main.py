import csv
import os

from src.scraper import extract_data
from src.gpt import get_letter

if __name__ == "__main__":
    # search queries
    interest = input("Interest: ").strip().replace(" ", "+")
    location = input("Location: ").strip().replace(" ", "+")
    radius = int(input("Radius: "))
    no_of_jobs = int(input("#Jobs: "))

    # Creating the Main Directory
    directory = os.getcwd() + "/"
    if not os.path.exists(directory):
        os.mkdir(directory)
        print(f"Directory added at {directory}")


    # creating the CSV-file
    csv_file_name = interest.title() + "_" + location.title() + "_Jobs.csv"

    # writing the labels to the CSV-file
    with open(f"{directory}/output/{csv_file_name}", mode="w", encoding="utf8") as csv_file:
        writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
        writer.writerow(["TITLE", "COMPANY", "LOCATION", "LINK"])


    # run the scraper to extract the job data from the website
    jobs = extract_data(interest, location, radius, no_of_jobs)

    # writing the job data to the CSV-file
    for job in jobs:
        job.write_to_file(f"{directory}/output/{csv_file_name}")

    for idx, job in enumerate(jobs):
        with open(f"{directory}/output/job{idx}.txt", mode="w", encoding="utf8") as txt_file:
            # get the resume
            txt_file.write(get_letter(job))

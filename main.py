import csv
import os
import scraper

if __name__ == "__main__":
    # search queries
    interest = input("Interest: ").strip()
    location = input("Location: ").strip()
    radius = int(input("Radius: "))

    no_of_pages = int(input("#Pages: "))

    # Creating the Main Directory
    directory = os.getcwd() + "/"
    if not os.path.exists(directory):
        os.mkdir(directory)
        print(f"Directory added at {directory}")


    # creating the CSV-file
    file_name = interest.title() + "_" + location.title() + "_Jobs.csv"
    file_path = directory + file_name

    # writing the labels to the CSV-file
    with open(file_path, mode="w", encoding="utf8") as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        writer.writerow(["TITLE", "COMPANY", "LOCATION", "LINK", "TEXT"])

    jobs = scraper.extract_data(interest, location, radius, no_of_pages)

    # writing the job data to the CSV-file
    for job in jobs:
        job.write_to_file(file_path)

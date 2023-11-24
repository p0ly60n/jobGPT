import os
import csv
import requests
from bs4 import BeautifulSoup

headers = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.stepstone.de"

def extract_data():

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

    # writing to the CSV-file
    with open(file_path, mode="w", encoding="utf8") as file:
        writer = csv.writer(file, delimiter=",", lineterminator="\n")
        # adding labels to the CSV-file
        writer.writerow(
            ["TITLE", "COMPANY", "LOCATION", "LINK", "TEXT"])

        # requesting the given URL
        print("\nScraping...\n")
        for page in range(no_of_pages):
            url = f"{BASE_URL}/jobs/{interest}/in-{location}?radius={radius}/page={page + 1}"
            response = requests.get(url, headers=headers, timeout=5)

            # assert that the request was successful and returned with error code < 400
            assert response.ok

            # Scrapping the contents of the url for needed information
            soup = BeautifulSoup(response.text, "html.parser")

            jobs = soup.find_all("article", {"class": "res-j5y1mq"})

            for job in jobs:
                job_id = job["id"]
                job_link = BASE_URL + "/" + job.find("a", {"class": "res-y456gn"})["href"]
                job_title = job.find("div", {"class": "res-nehv70"}).text.strip()
                job_company = job.find("div", {"class": "res-1r68twq"}).find("span", {"class": "res-btchsq"}).text.strip()
                job_location = job.find("div", {"class": "res-qchjmw"}).find("span", {"class": "res-btchsq"}).text.strip()
                job_text = extract_specific_text(job_link)

                # Writing to CSV-file the extracted data
                writer.writerow(
                    [job_title, job_company, job_location, job_link, job_text])

    print(f"Jobs data written to {file_name} successfully.")


def extract_specific_text(link):
    response = requests.get(link, headers=headers, timeout=5)
    assert response.ok

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.find_all("span", {"class": "listing-content-provider-14ydav7"})
    
    company_text = text[0].text.strip()
    assignments = text[1].text.strip()
    requirements = text[2].text.strip()
    benefits = text[3].text.strip()
    try:
        extras = text[4].text.strip()
    except IndexError:
        extras = "keine Extra Infos"

    return f"Unternehmenstext:\n{company_text}\n\nAufgaben:\n{assignments}\n\nAnforderungen an den Bewerber:\n{requirements}\n\nBenefits:\n{benefits}\n\nExtras:\n{extras}"

def send_GPT_Query():
    pass

if __name__ == "__main__":
    extract_data()
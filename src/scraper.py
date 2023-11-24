import os
import requests
from bs4 import BeautifulSoup

from job import Job

HEADERS = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.stepstone.de"

def extract_data(interest, location, radius, no_of_pages):

    # requesting the given URL
    print("\nScraping...\n")

    # list of job instances
    jobs = []

    for page in range(no_of_pages):
        url = f"{BASE_URL}/jobs/{interest}/in-{location}?radius={radius}/page={page + 1}"
        response = requests.get(url, headers=HEADERS, timeout=5)

        # assert that the request was successful and returned with error code < 400
        assert response.ok

        # Scrapping the contents of the url for needed information
        soup = BeautifulSoup(response.text, "html.parser")

        jobs_soup = soup.find_all("article", {"class": "res-j5y1mq"})

        for job_soup in jobs_soup:
            job_id = job_soup["id"]
            job_link = BASE_URL + "/" + job_soup.find("a", {"class": "res-y456gn"})["href"]
            job_title = job_soup.find("div", {"class": "res-nehv70"}).text.strip()
            job_company = job_soup.find("div", {"class": "res-1r68twq"}).find("span", {"class": "res-btchsq"}).text.strip()
            job_location = job_soup.find("div", {"class": "res-qchjmw"}).find("span", {"class": "res-btchsq"}).text.strip()
            job_text = extract_specific_text(job_link)

            # Creating Job Instance and appending it to the jobs list
            jobs.append(Job(job_title, job_company, job_location, job_link, job_text))

    return jobs


def extract_specific_text(link):
    response = requests.get(link, headers=HEADERS, timeout=5)
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

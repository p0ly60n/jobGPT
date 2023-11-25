import os
import requests
from bs4 import BeautifulSoup

from src.job import Job

HEADERS = {
    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.stepstone.de"

def extract_data(interest: str, location: str, radius: int, no_of_jobs:int = 1):
    # list of job instances
    jobs = []

    site_index = 1

    while (len(jobs) < no_of_jobs):
        url = f"{BASE_URL}/jobs/{interest}/in-{location}?radius={radius}" + ("/page={site_index}" if site_index > 1 else "")
        response = requests.get(url, headers=HEADERS, timeout=5)

        # assert that the request was successful and returned with error code < 400
        assert response.ok

        # Scrapping the contents of the url for needed information
        soup = BeautifulSoup(response.text, "html.parser")

        jobs_soup = soup.find_all("article", {"class": "res-j5y1mq"})

        for job_index, job_soup in enumerate(jobs_soup):
            if (len(jobs) >= no_of_jobs):
                break
            job_id = job_soup["id"]
            job_company = job_soup.find("div", {"class": "res-1r68twq"}).find("span", {"class": "res-btchsq"}).text.strip()

            print(f"Scraping Job{job_index + 1} @ {job_company}...")

            job_link = BASE_URL + "/" + job_soup.find("a", {"class": "res-y456gn"})["href"]
            job_title = job_soup.find("div", {"class": "res-nehv70"}).text.strip()
            job_location = job_soup.find("div", {"class": "res-qchjmw"}).find("span", {"class": "res-btchsq"}).text.strip()
            job_text = extract_specific_text(job_link)

            # Creating Job Instance and appending it to the jobs list
            jobs.append(Job(job_title, job_company, job_location, job_link, job_text))

        site_index += 1

    return jobs


def extract_specific_text(link: str):
    response = requests.get(link, headers=HEADERS, timeout=5)
    assert response.ok

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.find_all("span", {"class": "listing-content-provider-14ydav7"})

    try:
        company_text = text[0].text.strip()
    except IndexError:
        company_text = "kein Unternehmens Text gefunden"
        print("-> kein Unternehmens Text gefunden")
    try:
        assignments = text[1].text.strip()
    except IndexError:
        assignments = "keine Aufgaben gefunden"
        print("-> keine Aufgaben gefunden")
    try:
        requirements = text[2].text.strip()
    except IndexError:
        requirements = "keine Anforderungen gefunden"
        print("-> keine Anforderungen gefunden")
    try:
        benefits = text[3].text.strip()
    except IndexError:
        benefits = "keine Benefits gefunden"
        print("-> keine Benefits gefunden")
    try:
        extras = text[4].text.strip()
    except IndexError:
        extras = "keine Extra Infos gefunden"
        print("-> keine Extra Infos gefunden")

    return \
        f"""Unternehmenstext:
        {company_text}
        
        Aufgaben:
        {assignments}
        
        Anforderungen an den Bewerber:
        {requirements}
        
        Benefits:
        {benefits}
        
        Extras:
        {extras}"""

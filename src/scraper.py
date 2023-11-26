import os
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

from src.job import Job


class Scraper (ABC):
    HEADERS = {
        "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    def __init__(self, interest: str, location: str, radius: int, no_of_jobs: int):
        self.interest = interest
        self.location = location
        self.radius = radius
        self.no_of_jobs = no_of_jobs
        self.jobs = []

    @classmethod
    @property
    @abstractmethod
    def BASE_URL(self) -> str:
        pass
    
    @abstractmethod
    def get_url(self, site_index) -> str:
        pass
    
    @abstractmethod
    def get_job_by_info(self, job_soup, job_index) -> Job:
        pass

    @abstractmethod
    def get_job_elements(self, soup) -> BeautifulSoup:
        pass
    
    def scrape(self) -> list[Job]:
        # list of job instances
        site_index = 1

        left_jobs = self.no_of_jobs

        while (left_jobs > 0):
            url = self.get_url(site_index)
            response = requests.get(url, headers=self.HEADERS, timeout=5)

            # log the error if the response is not ok
            self.check_status(response)

            # Scrapping the contents of the url for needed information
            job_elements = self.get_job_elements(BeautifulSoup(response.text, "html.parser"))

            for job_index, job_soup in enumerate(job_elements):
                if (left_jobs > 0):
                    self.get_job_by_info(job_soup, job_index)
                    left_jobs -= 1
                else:
                    break

            site_index += 1

        return self.jobs

    def check_status(self, response: requests.Response) -> bool:
        if (response.status_code != 200):
            print(f"Error: {response.status_code} - {response.reason} for summary-url: {response.url}")
            return False
        else:
            return True



class StepstoneScraper (Scraper):
    BASE_URL = "https://www.stepstone.de"

    def get_url(self, site_index) -> str:
        return f"{self.BASE_URL}/jobs/{self.interest}/in-{self.location}?radius={self.radius}" + \
                ("/page={site_index}" if site_index > 1 else "") + "&sort=2&action=sort_publish"

    def get_job_elements(self, soup: BeautifulSoup) -> BeautifulSoup:
        return soup.find_all("article", {"class": "res-j5y1mq"})

    def get_job_by_info(self, job_soup, job_index):
        job_id = job_soup["id"]
        job_company = job_soup.find("div", {"class": "res-1r68twq"}).find("span", {"class": "res-btchsq"}).text.strip()

        print(f"Scraping Job{job_index} @ {job_company}...")

        job_link = self.BASE_URL + job_soup.find("a", {"class": "res-y456gn"})["href"]
        job_title = job_soup.find("div", {"class": "res-nehv70"}).text.strip()
        job_location = job_soup.find("div", {"class": "res-qchjmw"}).find("span", {"class": "res-btchsq"}).text.strip()
        job_text = self.extract_joblisting(job_link)

        # Creating Job Instance and appending it to the jobs list
        self.jobs.append(Job(job_title, job_company, job_location, job_link, job_text))


    def extract_joblisting(self, link: str):
        response = requests.get(link, headers=self.HEADERS, timeout=5)

        # log the error if the response is not ok
        if (response.status_code != 200):
            print(f"Error: {response.status_code} - {response.reason} for specific job-listing: {link}")

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
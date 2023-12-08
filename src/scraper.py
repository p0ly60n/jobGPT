import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from abc import ABC, abstractmethod

from src.job import Job


class Scraper (ABC):
    def __init__(self, interest: str, location: str, radius: int, no_of_jobs: int):
        self.interest = interest
        self.location = location
        self.radius = radius
        self.no_of_jobs = no_of_jobs
        self.jobs = []
        self.browser = None

    @classmethod
    @property
    @abstractmethod
    def BASE_URL(self) -> str:
        pass
    
    @abstractmethod
    def get_summary_url(self, site_index) -> str:
        pass

    @abstractmethod
    def get_job_urls(self) -> list[str]:
        pass
    
    @abstractmethod
    def get_job(self, url) -> Job:
        pass
    
    def scrape(self) -> list[Job]:
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1080")

        self.browser = webdriver.Chrome(options=options)
        # list of job instances
        site_index = 1

        left_jobs = self.no_of_jobs

        while (left_jobs > 0):
            url = self.get_summary_url(site_index)
            self.browser.get(url)
            self.browser.implicitly_wait(5)
            self.browser.find_element(By.CSS_SELECTOR, "div#ccmgt_explicit_accept").click()
            assert self.interest in self.browser.title

            # Scrapping the contents of the url for needed information
            job_urls = self.get_job_urls()

            for job_index, job_url in enumerate(job_urls):
                if (left_jobs > 0):
                    print(f"Scraping Job{job_index}...")
                    self.get_job(job_url)
                    left_jobs -= 1
                else:
                    break

            site_index += 1

        self.browser.quit()

        return self.jobs



###################################################################################################



class StepstoneScraper (Scraper):
    BASE_URL = "https://www.stepstone.de"

    def get_summary_url(self, site_index) -> str:
        return f"{self.BASE_URL}/jobs/{self.interest}/in-{self.location}?radius={self.radius}" + \
                ("&page={site_index}" if site_index > 1 else "") + "&sort=2&action=sort_publish&rsearch=3"

    def get_job_urls(self) -> list:
        element = self.browser.find_elements(By.CSS_SELECTOR, "a.res-y456gn")
        return [x.get_attribute("href") for x in element]

    def get_job(self, url) -> Job:
        self.browser.get(url)
        job_company = self.browser.find_element(By.CSS_SELECTOR, "span.listing-content-provider-lxa6ue").text.strip()
        job_link = url
        job_title = self.browser.find_element(By.CSS_SELECTOR, "span.listing-content-provider-bewwo").text.strip()
        job_location = self.browser.find_element(By.CSS_SELECTOR, "span.listing-content-provider-1whr5zf").text.strip()
        job_text = self.extract_joblisting()

        # Creating Job Instance and appending it to the jobs list
        self.jobs.append(Job(job_title, job_company, job_location, job_link, job_text))

    def extract_joblisting(self) -> str:
        element_list = self.browser.find_elements(By.CSS_SELECTOR, "span.listing-content-provider-14ydav7")

        try:
            company_text = element_list[0].text.strip()
        except IndexError:
            company_text = "kein Unternehmens Text gefunden"
            print("-> kein Unternehmens Text gefunden")
        try:
            assignments = element_list[1].text.strip()
        except IndexError:
            assignments = "keine Aufgaben gefunden"
            print("-> keine Aufgaben gefunden")
        try:
            requirements = element_list[2].text.strip()
        except IndexError:
            requirements = "keine Anforderungen gefunden"
            print("-> keine Anforderungen gefunden")
        try:
            benefits = element_list[3].text.strip()
        except IndexError:
            benefits = "keine Benefits gefunden"
            print("-> keine Benefits gefunden")
        #try:
        #    extras = element_list[4].text.strip()
        #except IndexError:
        #    extras = "keine Extra Infos gefunden"
        #    print("-> keine Extra Infos gefunden")

        return f"""Unternehmenstext:
            {company_text}
            
            Aufgaben:
            {assignments}
            
            Anforderungen an den Bewerber:
            {requirements}
            
            Benefits:
            {benefits}"""
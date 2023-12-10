import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from abc import ABC, abstractmethod

from src.job import Job
from selenium.common.exceptions import NoSuchElementException


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

    def click_to_enter(self):
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
            self.click_to_enter()
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



#####################################################################################################



class StepstoneScraper (Scraper):
    BASE_URL = "https://www.stepstone.de"

    def get_summary_url(self, site_index) -> str:
        return f"{self.BASE_URL}/jobs/{self.interest}/in-{self.location}?radius={self.radius}" + \
                (f"&page={site_index}" if site_index > 1 else "") + "&sort=2&action=sort_publish&rsearch=3"

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

        return f"""Unternehmenstext:
            {company_text}
            
            Aufgaben:
            {assignments}
            
            Anforderungen an den Bewerber:
            {requirements}
            
            Benefits:
            {benefits}"""

    def click_to_enter(self):
        try:
            self.browser.find_element(By.CSS_SELECTOR, "div#ccmgt_explicit_accept").click()
        except NoSuchElementException:
            pass



#####################################################################################################



class IndeedScraper (Scraper):
    BASE_URL = "https://de.indeed.com"

    def get_summary_url(self, site_index) -> str:
        return f"{self.BASE_URL}/jobs?q={self.interest}&l={self.location}&radius={self.radius}" + \
                f"&start={site_index}"

    def get_job_urls(self) -> list:
        element = self.browser.find_elements(By.CSS_SELECTOR, "a[class='jcs-JobTitle css-jspxzf eu4oa1w0']")
        return [x.get_attribute("href") for x in element]

    def get_job(self, url) -> Job:
        self.browser.get(url)
        job_company = self.browser.find_element(By.CSS_SELECTOR, "span.css-1cxc9zk.e1wnkr790").text.strip()
        job_link = url
        job_title = self.browser.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title.css-1hwk56k.e1tiznh50").text.strip()
        job_location = self.browser.find_element(By.CSS_SELECTOR, "div.css-6z8o9s.eu4oa1w0").text.strip()
        job_text = self.extract_joblisting()

        # Creating Job Instance and appending it to the jobs list
        self.jobs.append(Job(job_title, job_company, job_location, job_link, job_text))

    def extract_joblisting(self) -> str:
        return self.browser.find_element(By.CSS_SELECTOR, "div#jobDescriptionText").text.strip()

    def click_to_enter(self):
        try:
            self.browser.find_element(By.CSS_SELECTOR, "button#onetrust-accept-btn-handler").click()
        except NoSuchElementException:
            pass
        try:
            self.browser.find_element(By.CSS_SELECTOR, "svg.css-1xqhio.eac13zx0").click()
        except NoSuchElementException:
            pass

import os
from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException
from src.job import Job


class Scraper (ABC):
    """
    Abstract base class for web scraping job listings.
    """

    def __init__(self, interest: str, location: str, radius: int, no_of_jobs: int):
        """
        Initializes the Scraper object.

        Parameters:
        - interest (str): The job interest or keyword.
        - location (str): The job location.
        - radius (int): The search radius in kilometers.
        - no_of_jobs (int): The number of jobs to scrape.
        """
        self.interest = interest
        self.location = location
        self.radius = radius
        self.no_of_jobs = no_of_jobs
        self.jobs = []
        self.browser = None

    @classmethod
    @property
    @abstractmethod
    def BASE_URL(cls) -> str:
        """
        The base URL of the job listing website.
        """

    @abstractmethod
    def get_display_url(self, site_index: int) -> str:
        """
        Returns the URL of the job display page for a given site index.

        Parameters:
        - site_index (int): The index of the job display page.

        Returns:
        - str: The URL of the job display page.
        """

    @abstractmethod
    def get_job_urls(self) -> list[str]:
        """
        Returns a list of job URLs on the current job display page.

        Returns:
        - list[str]: A list of job URLs.
        """

    @abstractmethod
    def extract_job(self, url):
        """
        Scrapes the job details from a given job url and appends it to "jobs".

        Parameters:
        - url (str): The URL of the job listing.
        """

    def click_to_enter(self):
        """
        Performs any necessary actions to enter the job listing page.
        """
        return
    
    def scrape(self) -> list[Job]:
        """
        Scrapes the job listings and returns a list of Job objects.

        Returns:
        - list[Job]: A list of Job objects representing the scraped job listings.
        """
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1080")

        self.browser = webdriver.Chrome(options=options)
        site_index = 1
        left_jobs = self.no_of_jobs

        while (left_jobs > 0):
            url = self.get_display_url(site_index)
            self.browser.get(url)
            self.browser.implicitly_wait(5)
            self.click_to_enter()
            #assert self.interest in self.browser.title

            job_urls = self.get_job_urls()

            for job_index, job_url in enumerate(job_urls):
                if (left_jobs > 0):
                    print(f"Scraping Job{job_index}...")
                    self.extract_job(job_url)
                    left_jobs -= 1
                else:
                    break

            site_index += 1

        self.browser.quit()

        return self.jobs


class StepstoneScraper (Scraper):
    """
    Scraper implementation for Stepstone job listings.
    """

    BASE_URL = "https://www.stepstone.de"

    def get_display_url(self, site_index) -> str:
        return f"{self.BASE_URL}/jobs/{self.interest}/in-{self.location}?radius={self.radius}" + \
                (f"&page={site_index}" if site_index > 1 else "") + "&sort=2&action=sort_publish&rsearch=3"

    def get_job_urls(self) -> list:
        element = self.browser.find_elements(By.CSS_SELECTOR, "a.res-y456gn")
        return [x.get_attribute("href") for x in element]

    def extract_job(self, url):
        self.browser.get(url)
        job_company = self.browser.find_element(By.CSS_SELECTOR, "span.listing-content-provider-lxa6ue").text.strip()
        job_link = url
        job_title = self.browser.find_element(By.CSS_SELECTOR, "span.listing-content-provider-bewwo").text.strip()
        job_location = self.browser.find_element(By.CSS_SELECTOR, "span.listing-content-provider-1whr5zf").text.strip()
        job_text = self.extract_joblisting()

        self.jobs.append(Job(job_title, job_company, job_location, job_link, job_text))

    def extract_joblisting(self) -> str:
        """
        Extracts the job listing details from the current page.

        Returns:
        - str: The extracted job listing details.
        """
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


class IndeedScraper (Scraper):
    """
    Scraper implementation for Indeed job listings.
    """

    BASE_URL = "https://de.indeed.com"

    def get_display_url(self, site_index) -> str:
        return f"{self.BASE_URL}/jobs?q={self.interest}&l={self.location}&radius={self.radius}" + \
                f"&start={site_index}"

    def get_job_urls(self) -> list:
        element = self.browser.find_elements(By.CSS_SELECTOR, "a[class='jcs-JobTitle css-jspxzf eu4oa1w0']")
        return [x.get_attribute("href") for x in element]

    def extract_job(self, url):
        self.browser.get(url)
        job_company = self.browser.find_element(By.CSS_SELECTOR, "span.css-1cxc9zk.e1wnkr790").text.strip()
        job_link = url
        job_title = self.browser.find_element(By.CSS_SELECTOR, "h1.jobsearch-JobInfoHeader-title.css-1hwk56k.e1tiznh50").text.strip()
        job_location = self.browser.find_element(By.CSS_SELECTOR, "div.css-6z8o9s.eu4oa1w0").text.strip()
        job_text = self.extract_joblisting()

        self.jobs.append(Job(job_title, job_company, job_location, job_link, job_text))

    def extract_joblisting(self) -> str:
        """
        Extracts the job listing details from the current page.

        Returns:
        - str: The extracted job listing details.
        """
        return self.browser.find_element(By.CSS_SELECTOR, "div#jobDescriptionText").text.strip()

    def click_to_enter(self):
        try:
            self.browser.find_element(By.CSS_SELECTOR, "button#onetrust-accept-btn-handler").click()
        except NoSuchElementException:
            pass
        try:
            self.browser.find_element(By.CSS_SELECTOR, "button.css-yi9ndv.e8ju0x51").click()
        except NoSuchElementException:
            pass

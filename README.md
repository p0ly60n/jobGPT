# jobGPT

## Description

This project scrapes Job websites like [`stepstone.de`](https://www.stepstone.de) or [`indeed.de`](https://de.indeed.com) for job listings matching the entered search criteria using Selenium and generates a Cover letter for them. The scraped information is then saved to a `.csv` file. You can select the jobs you want to have a cover letter generated to and the program then generates a cover letter for them with the job data. If a CV / Resume `.pdf`/`.txt` was submitted, it also extracts the personal information and therefore personalizes the cover letter texts.

## Installation

This program requires tkinter and Python 3.6+
1) Clone this repository
2) Install the required packages using the command [`pip install -r requirements.txt`](requirements.txt).
3) Rename the file [`config_default.cfg`](config_default.cfg) to `config.cfg` and insert your OpenAI API key under [`api_key`](config_default.cfg). Also change the used GPT-Model to the one you like (e.g. gpt-3.5-turbo [default], gpt-4)

## Usage

Run the [`main.py`](main.py) script to start the project and input the needed information to start the query. If a CV/Resume should be used to extract the personal information, select it. Using the Dropdown-Menu you can choose the website to scrape. Scraping can take some time due to selenium being quite slow, so grab a coffee and come back later :) Sometimes the program breaks because of spam protection captchas. The output will be in the [`output/`](/output/) folder containing the single `.csv`-file and several cover letters named after the job corresponding to the `.csv`-file.

## Modifying

This tool scrapes german websites and also generates german cover letters. If you want this tool to use your native language feel free to edit the starting-prompt at [`src/gpt.py`](/src/gpt.py) and the website Scraping Classes at [`src/scraper.py`](/src/scraper.py).

You can also add other not yet supported websites by creating a new class in [`src/scraper.py`](/src/scraper.py) that extends the abstract class `Scraper`. To do that implement the following methods:
- `BASE_URL` -> class-attribute which is the main domain of your website (e.g. https://www.stepstone.de)
- `get_display_url` -> method for calculating the url of all joblistings for each page-index
- `get_job_urls` -> method for retrieving link to the job descriptions for each job
- `extract_job` -> method for retrieving the job information like company name, location, personal profile, etc...
- `click_to_enter` [optional] -> method for handling cookie-accept banners or pop-up messages

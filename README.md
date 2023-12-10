# jobGPT

## Description

This project scrapes Job websites like [`stepstone.de`](https://www.stepstone.de) or [`indeed.de`](https://de.indeed.com) for job listings matching the entered search criteria using Selenium. The information is then saved to a `.csv` file. Afterwards you can select the jobs you want to have a cover letter generated to and generates a cover letter for them with the job data. If a CV / Resume `.pdf` was submitted, it also extracts the personal information and therefore personalizes the cover letter texts.

## Installation

1. Install the required packages using the command [`pip install -r requirements.txt`](requirements.txt).
2. Rename the file [`config_default.cfg`](config_default.cfg) to `config.cfg` and insert your OpenAI API key under [`api_key`](config_default.cfg). Also change the used GPT-Model to the one you like (e.g. gpt-3.5-turbo [default], gpt-4)

## Usage

If a CV/Resume should be used to extract the personal information, place it in the root directory. Run the [`main.py`](main.py) script to start the project and input the needed information to start the query. Select the website using the checkbox. In case of a Resume-pdf supplied, enter the filename including the `.pdf` ending. It due to selenium being quite slow, so grab a coffee and come back later :) The output will be in the [`output/`](/output/) folder containing the single `.csv`-file and several cover letters named after the job corresponding to the `.csv`-file.

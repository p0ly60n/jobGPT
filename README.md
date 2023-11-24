# jobGPT

## Description

This project scrapes "stepstone.de" for job listings matching the entered search criterea and saves it in a `.csv` file. Afterwards it calls the openAI API with the given job data to create a cover letter suiting the job.

## Installation

1. Install the required packages using the command `pip install -r requirements.txt`.
2. Rename the file `keys_default.cfg` to `keys.cfg` and insert your OpenAI API key under `api_key`.

## Usage

Run the `main.py` script to start the project. It takes a while due to the generation being limited by openAI and the ethernet requests, so grab a coffee and come back later :) The output will be in the `/output` folder containing the single `.csv`-file and a cover letter corresponding to the order of the jobs in the `.csv`-file.

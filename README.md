# jobGPT

## Description

This project scrapes [`stepstone.de`](https://www.stepstone.de) for job listings matching the entered search criteria and saves it in a `.csv` file. Afterwards, it calls the OpenAI API with the given job data to create a cover letter suiting the job.

## Installation

1. Install the required packages using the command [`pip install -r requirements.txt`](requirements.txt).
2. Rename the file [`keys_default.cfg`](keys_default.cfg) to `keys.cfg` and insert your OpenAI API key under [`api_key`](keys_default.cfg).

## Usage

Run the [`main.py`](main.py) script to start the project and input the needed information to start the query. It takes a while due to it being limited by OpenAIs text-generation and internet requests, so grab a coffee and come back later :) The output will be in the [`output/`](/output/) folder containing the single `.csv`-file and several cover letters named after the job-Index in the `.csv`-file.

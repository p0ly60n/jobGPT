from configparser import ConfigParser
from openai import OpenAI

from src.job import Job

def get_letter(job: Job):
    # loading the config file
    config = ConfigParser()
    config.read("keys.cfg")
    api_key = config.get("openAI", "api_key")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein Ersteller eines Anschreibens und formulierst ein passendes Anschreiben für die Stelle die dir gegeben wird."
            },
            {
                "role": "user",
                "content": f"Erstelle das Anschreiben für diese Stelle: \n{job.formatted()}"
            }
        ],
        max_tokens=1024,
    )

    return response.choices[0].message.content
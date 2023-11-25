from configparser import ConfigParser
from openai import OpenAI

from src.job import Job

def get_letter(job: Job, personal_info: str = ""):
    # loading the config file
    config = ConfigParser()
    config.read("config.cfg")
    api_key = config.get("openAI", "api_key")
    model = config.get("openAI", "model")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Du bist ein Ersteller eines Anschreibens und" \
                    "formulierst ein passendes Anschreiben für die Stelle die dir gegeben wird, "\
                    "wobei die Fähigkeiten, Profil und Erfolge die im Lebenslauf vorhanden sind, "\
                    "mit eingebracht wird und auf die Stelle bezogen wird"
            },
            {
                "role": "user",
                "content": f"Erstelle das Anschreiben für diese Stelle: \n{job.formatted()}.\n\n" \
                    f"Der Lebenslauf und die Fähigkeiten: \n{personal_info}"
            }
        ],
        max_tokens=1024,
    )

    print(f"Used Tokens: {response.usage.total_tokens}")

    return response.choices[0].message.content
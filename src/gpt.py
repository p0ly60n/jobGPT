from configparser import ConfigParser
from openai import OpenAI

from src.job import Job

def get_letter(job: Job, personal_info: str = ""):
    """
    Generates a cover letter for a given job using OpenAI's chat completions API.

    Args:
        job (Job): The job object containing the job details.
        personal_info (str, optional): The personal information to be included in the letter. Defaults to "".

    Returns:
        dict: A dictionary containing the generated cover letter, input tokens used, and output tokens used.
    """
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
        timeout=30
    )

    return \
        {"message": response.choices[0].message.content, \
        "input_tokens": response.usage.prompt_tokens, \
        "output_tokens": response.usage.completion_tokens}
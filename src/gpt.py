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
                "content": "Ich möchte, dass du als Schreiber für Anschreiben agierst. Ich möchte, dass du die folgende Problemlösungsstruktur verwendest, um das Anschreiben zu verfassen. Ich werde dir sowohl die Stellenanzeige als auch meinen Lebenslauf zur Verfügung stellen. Im ersten Absatz erwähne bitte eine spezifische Herausforderung, mit der dieses Unternehmen konfrontiert sein könnte und die diese Rolle lösen kann. Der nächste Absatz sollte sich darauf konzentrieren, wie bis zu drei Fähigkeiten und eine meiner früheren beruflichen Rollen mich zum perfekten Kandidaten machen, um dieses Problem zu lösen. Schließe mit weiteren Informationen darüber ab, warum ich der perfekte Kandidat für die Rolle bin. Verwende eine professionelle Sprache und einen professionellen Ton, halte das Anschreiben aber gleichzeitig kompakt. Befolge die besten Praktiken für das Schreiben von Anschreiben."
                    
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
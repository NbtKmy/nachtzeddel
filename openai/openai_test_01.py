from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
  api_version="2024-02-15-preview"
)

def get_chat_completion(prompt, model="zb-lab-gpt-4o"):
  
   # Creating a message as required by the API
   messages = [{"role": "user", "content": prompt}]
  
   # Calling the ChatCompletion API
   response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.8,
        max_tokens=1200,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
   )

   # Returning the extracted response
   return response.choices[0].message.content


response = get_chat_completion("Schreibe in Schweizerdeutsch eine kurze Geschichte zum Thema: Die Bibliotheksinformatik der Zentralbibliothek Zürich hat viele schlaue Mitarbeitende!")

print(f"\n\n{response}\n\n")


#response = client.embeddings.create(input = "Your text string goes here", model= "zb-embedding-01")

#print(response.model_dump_json(indent=2))

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

def geracao_de_texto_stream(messages, model="gpt-4o-mini", temperature=0, max_tokens=1000):
  completions = client.chat.completions.create(
    messages=messages,
    model=model,
    temperature=temperature,
    max_tokens=max_tokens,
    stream=True
  )

  texto_completo = ""
  print('Assistente: ', end="")
  for stream_resposta in completions:
    texto = stream_resposta.choices[0].delta.content
    if texto:
      print(texto, end="")
      texto_completo += texto
  
  messages.append({"role": "assistant", "content": texto_completo})
  return messages

messages = []
print('Bem-vindo ao chatbot! Digite "sair" para sair.')
while True:
  prompt = input("user: ")
  if prompt == "sair":
    break

  messages .append(
    {"role": "user", "content": prompt},
  )

  messages = geracao_de_texto_stream(messages)    

  print("\n")
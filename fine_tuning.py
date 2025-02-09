import json
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

with open('arquivos/chatbot_respostas.json', encoding='utf-8') as f:
  chatbot_respostas = json.load(f)

with open('arquivos/chatbot_respostas.jsonl','w') as f:
  for entrada in chatbot_respostas:
    resposta = {
      'resposta': entrada['resposta'],
      'categoria': entrada['categoria'],
      'fonte': 'AsimovBot'
    }
    entrada_jsonl = {
      'messages': [
        {'role': 'user', 'content': entrada['pergunta']},
        {'role': 'assistant', 'content': json.dumps(resposta)}
      ]
    }
    json.dump(entrada_jsonl, f, ensure_ascii=False)
    f.write('\n')

file = client.files.create(
  file=open('arquivos/chatbot_respostas.jsonl', 'rb'),
  purpose='fine-tune'
)

client.fine_tuning.jobs.create(
  training_file=file.id,
  model='gpt-4o-mini'
)

messagens = [
  {'role': 'user', 'content': 'O que é uma equação quadrática?'},
]

resposta = client.chat.completions.create(
  messages=messagens,
  model='ft:gpt-3.5-turbo-0125:codedfmpc::AyqAto19',
  temperature=0,
  max_tokens=1000
)
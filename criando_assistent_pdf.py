import time
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

vector_store = client.beta.vector_stores.create(
  name="Apostlias Asimov Aula 15",
)

files = [
  'arquivos/Explorando a API da OpenAI.pdf'
  'arquivos/Explorando o Universo das IAs com Hugging Face.pdf'
]

file_stream = [open(f, 'rb') for f in files]

file_batch =  client.beta.vector_stores.file_batches.create_and_poll(
  vector_store_id=vector_store.id,
  files=file_stream
)

assistant = client.beta.assistants.create(
  name="Tutor asimov",
  instructions="você é um tutor de uma escola de programação. \
    Você é ótimo para responder peruntas teóricas sobre a api \
    da OpenAI e sobre a atualização da biblioteca Hugging Face \
    com Python. Você utiliza as apostilas dos cursos para basear \
    suas respostas. Caso você não encontre as respostas nas apostilas \
    informadas, você fala que nao sabe responder.",
  tools=[
    { "type": "file_search" }
  ],
  tool_resources={
    'file_search':
      {
        'vector_store_ids': [vector_store.id]
      }
    },
  model="gpt-4o-mini"
)

thread = client.beta.threads.create()

prompt = 'O que é o Hugging Face?'

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt
)

run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="O nome do usuário é Adriano Soares e ele é usuario premium",
)

while run.status in ['queued', 'in_progress', 'cancelling']:
  time.sleep(1)
  run = client.beta.threads.runs.retrieve(
    thread_id=thread.id,
    run_id=run.id
  )

if run.status == 'completed':
  mensagens = client.beta.threads.messages.list(
    thread_id=thread.id
  )
  print(mensagens)
else:
  print('Erro ao executar o código', run.status)

print(mensagens.data[0].content[0].text.value)

run_steps = client.beta.threads.runs.steps.list(
  thread_id=thread.id,
  run_id=run.id
)

for step in run_steps.data[::-1]:
  print('\n=== steps',step.step_details)
  if step.step_details.type == 'tool_calls':
    for tool_call in step.step_details.tool_calls:
      if tool_call.type == 'file_search':
        print('------')
        print(tool_call)
        print('------')
      if tool_call.type == 'code_interpreter':
        print('------')
        print(tool_call.code_interpreter.input)
        print('------')
        print('Result')
        print(tool_call.code_interpreter.outputs[0].logs)
  if step.step_details.type == 'message_creation':
    mensagens = client.beta.threads.messages.retrieve(
      thread_id=thread.id,
      message_id=step.step_details.message_creation.message_id
    )
    print(mensagens.content[0].text.value)
    

mensagens = client.beta.threads.messages.list(
  thread_id=thread.id
)
message = list(mensagens)[0].content[0].text
anotacoes = message.annotations
citacoes = []

for index, anotacao in enumerate(anotacoes):
  message.value = message.value.replace(anotacao.text, f'[{index}]')
  if file_cit := getattr(anotacao, 'file_citation', None):
    file = client.files.retrieve(file_cit.file_id)
    citacoes.append(f'[{index}] {file.filename}')

citacoes = '\n'.join(citacoes)
message.value = f'{message.value}\n{citacoes}'
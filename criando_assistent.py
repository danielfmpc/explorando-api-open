import time
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

assistant = client.beta.assistants.create(
  name="Tutor de matemática da asimove",
  instructions="Você é um tutor pessoal de matemática da empresa Asimov. Escreva e exeecute códigos para responder as perguntas de matemática.",
  tools=[
    { "type": "code_interpreter" }
  ],
  model="gpt-4o-mini"
)

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content="Se eu jogar um dado honesto 1000 vezes, qual é a probabilidade de eu obter 150 vezes o número 6? Resolva com um código"
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

run_steps = client.beta.threads.runs.steps.list(
  thread_id=thread.id,
  run_id=run.id
)

for step in run_steps.data[::-1]:
  print('\n=== steps',step.step_details)
  if step.step_details.type == 'tool_calls':
    for tool_call in step.step_details.tool_calls:
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
    

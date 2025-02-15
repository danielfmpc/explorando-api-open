import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

dataset = pd.read_csv('arquivos/supermarket_sales.csv')
_ = load_dotenv(find_dotenv())

client = OpenAI()

file = client.files.create(
  file=open('arquivos/supermarket_sales.csv', 'rb'),
  purpose='assistants'
)

assistant = client.beta.assistants.create(
  name="Analista financeiro",
  instructions="Você é um analista financeiro de um supermercado. Você deve utilizar os dados .csv informadoso realtivos as vendas do supermercado para realizar as suas analses",  
  tools=[
    { "type": "code_interpreter" }
  ],
  tool_resources={
    'code_interpreter': {
      'file_ids': [file.id]
    }
  },
  model="gpt-4o-mini"
)

thread = client.beta.threads.create()

prompt = 'Qual é o rating médio das vendas do supermercado? O arquivo está no formato CSV.'
prompt = 'Gere um gráfico pizza com o percentual de vendas por meio de pagamento'

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

run_steps = client.beta.threads.runs.steps.list(
  thread_id=thread.id,
  run_id=run.id
)

for step in run_steps.data[::-1]:
  print('\n=== steps',step.step_details)
  if step.step_details.type == 'tool_calls':
    for tool_call in step.step_details.tool_calls:
      print('```')
      print(tool_call.code_interpreter.input)
      print('```')
      print('Result')
      if tool_call.code_interpreter.outputs[0].type == 'logs':
        print('Result')
        print(tool_call.code_interpreter.outputs[0].logs)
  if step.step_details.type == 'message_creation':
    mensagens = client.beta.threads.messages.retrieve(
      thread_id=thread.id,
      message_id=step.step_details.message_creation.message_id
    )
    if message.content[0].type == 'text':
      print(message.content[0].text.value)

    if message.content[0].type == 'image_file':
      file_id = message.content[0].image_file.file_id
      image_data = client.files.content(file_id)

      with open(f'arquivos/{file_id}.png', 'wb') as file:
          file.write(image_data.read())

      img = mpimg.imread(f'arquivos/{file_id}.png')
      fig, ax = plt.subplots()
      ax.set_axis_off()
      ax.imshow(img)
      plt.show()
    

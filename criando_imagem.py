import requests
import PIL as Image
from openai import OpenAI
from  dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

model = "dall-e-3"
prompt = "Crie uma imagem de duas senhoras conversando em \
  um bosque ampo com árvores floridas"
size = "1024x1024"
quality = "standard"
style = "natural"
n = 1

resposta = client.images.generate(
  model=model,
  prompt=prompt,
  size=size,
  quality=quality,
  style=style,
  n=n,
)

print(resposta.data[0].revised_prompt)
print(resposta.data[0].url)

nome_arquivo = "arquivos/{nome}_{modelo}_{qualidade}_{style}.png"
image_url = resposta.data[0].url
image_data = requests.get(image_url).content

with open(nome_arquivo, "wb") as f:
  f.write(image_data)


image = Image.open(nome_arquivo)
image.show()  


## Editando a imagem

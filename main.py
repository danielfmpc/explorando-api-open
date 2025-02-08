from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

def geracao_de_texto(prompt, model="gpt-4o-mini", temperature=0, max_tokens=1000):
    response = client.chat.completions.create(
        messages=prompt, 
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )
    prompt.append(response.choices[0].message.model_dump(exclude_none=True))
    return prompt


def geracao_de_texto_stream(prompt, model="gpt-4o-mini", temperature=0, max_tokens=1000):
    response = client.chat.completions.create(
        messages=prompt, 
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )

    return response

messages=[
    {"role": "user", "content": "explique o q é uma maça com 5 palavras"},
]

# completion= geracao_de_texto(messages)
# print(completion)

completions= geracao_de_texto_stream(messages)
resposta_completa = ''
for stream_resposta in completions:
    texto = stream_resposta.choices[0].delta.content
    if texto:
        resposta_completa += texto

print(resposta_completa)


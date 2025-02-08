import json
import yfinance as yf
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

client = OpenAI()

#  1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
def retorna_cotacao_acao_historica(ticker: str, periodo='1mo'):
  print(f'Buscando dados de {ticker}...')

  if not ticker.endswith('.SA'):
    ticker = f'{ticker}.SA'
    
  ticker_obj = yf.Ticker(ticker)
  hist = ticker_obj.history(period=periodo)
  if hist.empty:
    return 'Não foi possível encontrar dados para o ticker informado.'
  hist_close = hist['Close']
  hist_close.index = hist_close.index.strftime('%Y-%m-%d')
  hist_close = round(hist_close, 2)
  if len(hist_close) > 30:
    slice_size = int(len(hist_close) / 30)
    hist_close = hist_close.iloc[::-slice_size][::-1]
  return hist_close.to_json()

tools = [
  {
    'type': 'function',
    'function': {
      'name': 'retorna_cotacao_acao_historica',
      'description': 'Retorna a cotação histórica de uma ação',
      'parameters': {
        'type': 'object',
        'properties': {
          'ticker': {
            'type': 'string',
            'description': 'O ticker da ação. Ex.: "ABEV3" para ambev, "PETR4" para petrobras, etc.'
          },
          'periodo': {
            'type': 'string',
            'description': 'Período da cotação histórica. \
                            Ex.: "1d" é igual a 1 dia, "1mo" é igual a 1 mês, "1y" é igual a 1 ano, etc.',
            'enum': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
          }
        }
      }
    }
  }
]

funcoes_disponiveis = {
  'retorna_cotacao_acao_historica': retorna_cotacao_acao_historica
}

def gera_texto(mensagens):
  resposta = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=mensagens,
    tools=tools,
    tool_choice="auto"
  )

  tool_calls = resposta.choices[0].message.tool_calls

  if tool_calls:
    mensagens.append(resposta.choices[0].message)
    for tool_call in tool_calls:
      func_name = tool_call.function.name
      function_to_call = funcoes_disponiveis[func_name]
      function_args = json.loads(tool_call.function.arguments)
      function_response = function_to_call(**function_args)
      mensagens.append({
        'tool_call_id': tool_call.id,
        'role': 'tool',
        'name': func_name,
        'content': function_response
      })
    resposta_final = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=mensagens,
    )
    mensagens.append(resposta_final.choices[0].message)
  print(f'Assistente: {mensagens[-1].content}')

if __name__ == '__main__':
  print('Bem-vindo ao chatbot! Digite "sair" para sair.')
  while True:
    input_usuario = input('user: ')
    if input_usuario == 'sair':
      break
    messages = [{ 'role': 'user', 'content': input_usuario }]
    messages = gera_texto(messages)
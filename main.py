import os
import requests
import telebot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

import matplotlib
matplotlib.use('Agg') # backend não interativo

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
city = "Bom Jesus do Itabapoana"

bot = telebot.TeleBot(TOKEN)

print("River Bot is running...")

def get_river_level():
    url = "http://alertadecheias.inea.rj.gov.br/alertadecheias/214109520.html"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup.prettify())
        elements = soup.find_all("span", {"class": "count_top"})
        for element in elements:
            if "Nível as" in element.text:
                div_with_nivel = element.find_next("div", {"class": "count"})
                if div_with_nivel:
                    level = div_with_nivel.text.strip()
                    return f"O nível atual do rio é de {level} m"
    else:
        return "Erro ao acessar o site."

def get_quota():
    url = "http://alertadecheias.inea.rj.gov.br/alertadecheias/214109520.html"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.find_all("span", {"class": "count_top"})
        for element in elements:
            if "Cota de transbordamento" in element.text:
                div_with_quota = element.find_next("div", {"class": "count"})
                if div_with_quota:
                    quota = div_with_quota.text.strip()
                    return f"A cota de transbordamento atual é de {quota}"
    else:
        return "Erro ao acessar o site."

def get_river_data():
    url = "http://alertadecheias.inea.rj.gov.br/alertadecheias/214109520.html"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", {"id": "Table"})
        
        if table:
            data = []
            rows = table.find_all("tr")
            
            for row in rows:
                columns = row.find_all("td")
                row_data = [col.text.strip() for col in columns]
                if row_data:
                    data.append(row_data)
            
            return data
        else:
            print("Tabela não encontrada.")
            return []
    else:
        print("Erro ao acessar o site.")
        return []

def save_to_excel(data, filename="dados.xlsx"):
    df = pd.DataFrame(data, columns=[
        "Data e Hora", "Chuva (mm) - Último", "Chuva (mm) - 1h", "Chuva (mm) - 4h", 
        "Chuva (mm) - 24h", "Chuva (mm) - 96h", "Chuva (mm) - 30d", "Nível do rio (m) - Último"
    ])
    df.to_excel(filename, index=False)
    return df

def plot_daily_river_level(df):
    # filtrando as colunas necessárias
    df_filtered = df[["Data e Hora", "Nível do rio (m) - Último"]].copy()
    
    df_filtered["Data e Hora"] = pd.to_datetime(df_filtered["Data e Hora"], format="%d/%m/%Y %H:%M")
    
    today = datetime.today().date()
    df_today = df_filtered[df_filtered["Data e Hora"].dt.date == today].copy()

    df_today["Nível do rio (m) - Último"] = df_today["Nível do rio (m) - Último"].replace("Dado Nulo", pd.NA)
    
    # extraindo a hora e o último nível para o gráfico
    df_today["Hora"] = df_today["Data e Hora"].dt.strftime("%H:%M")
    df_today["Último Nível"] = pd.to_numeric(df_today["Nível do rio (m) - Último"], errors="coerce")
    
    plt.figure(figsize=(10, 5))
    plt.plot(df_today["Hora"], df_today["Último Nível"], marker='o', color='#2F57FF', label='Último Nível')
    plt.title('Nível do Rio nas Últimas 24 Horas')
    plt.xlabel('Hora')
    plt.ylabel('Último Nível (m)')
    plt.ylim(0, 3)
    plt.xticks(rotation=45)
    plt.gca().invert_xaxis()
    plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))
    plt.legend()
    
    grafico_path = './data/grafico_diario.png'
    plt.savefig(grafico_path)
    plt.close()
    
    return grafico_path

def get_weather(city):
    link = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&lang=pt_br"
    response = requests.get(link)
    if response.status_code == 200:
        data = response.json()
        descricao = data['weather'][0]['description']
        temperatura = data['main']['temp'] - 273.15  # Kelvin to Celsius
        umidade = data['main']['humidity']
        vento = data['wind']['speed']
        
        return {
            "descricao": descricao,
            "temperatura": temperatura,
            "umidade": umidade,
            "vento": vento
        }
    else:
        return None

@bot.message_handler(commands=["nivel"])
def nivel(message):
    river_level = get_river_level()
    bot.send_message(message.chat.id, river_level)
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["cota"])
def cota(message):
    flood_quota = get_quota()
    bot.send_message(message.chat.id, "A cota de transbordamento é o nível crítico de altura da água em um rio. Ela indica o ponto em que as inundações se tornam iminentes ou começam a ocorrer.\n\n " + flood_quota)
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["grafico_diario"])
def grafico_diario(message):

    dados = get_river_data()
    if dados:
        df = save_to_excel(dados)
        grafico_path = plot_daily_river_level(df)
    
        with open(grafico_path, 'rb') as graph:
            bot.send_photo(message.chat.id, graph)
        bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["grafico"])
def grafico(message):
    bot.send_message(message.chat.id, "Exibindo o gráfico do historico...")
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["camera"])
def camera(message):
    bot.send_message(message.chat.id, "Câmera de monitoramento disponível em: https://aguasdocaparao.com.br/bom-jesus-do-itabapoana/")
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["opcao1"])
def opcao1(message):
    text = """
    O que você quer? (Clique em uma opção)
    /nivel Consultar o nível do rio
    /cota Consultar a cota de transbordamento
    /grafico_diario Exibir gráfico do nível do rio nas últimas 24 horas
    /grafico Exibir gráfico do histórico do nível do rio
    /camera Acessar a câmera de monitoramento"""
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, "Clique aqui para voltar: /inicio")

@bot.message_handler(commands=["temperatura"])
def temperatura(message):
    clima = get_weather(city)

    if clima:
        resposta = f"Clima em {city.capitalize()}: {clima['descricao']}. Temperatura: {clima['temperatura']:.2f}ºC"
        bot.send_message(message.chat.id, resposta)
    else:
        bot.send_message(message.chat.id, "Erro ao acessar a API do clima.")
    
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao2")

@bot.message_handler(commands=["umidade"])
def umidade(message):
    clima = get_weather(city)

    if clima:
        resposta = f"Clima em {city.capitalize()}: {clima['descricao']}. Umidade: {clima['umidade']}%"
        bot.send_message(message.chat.id, resposta)
    else:
        bot.send_message(message.chat.id, "Erro ao acessar a API do clima.")
    
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao2")

@bot.message_handler(commands=["vento"])
def vento(message):
    clima = get_weather(city)

    if clima:
        resposta = f"Clima em {city.capitalize()}: {clima['descricao']}. Velocidade do vento: {clima['vento']:.2f} m/s"
        bot.send_message(message.chat.id, resposta)
    else:
        bot.send_message(message.chat.id, "Erro ao acessar a API do clima.")
    
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao2")

def get_5_day_forecast():
    lat = -21.1339
    lon = -41.6797
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()

        temperatures = []
        dates = []
        
        for entry in data['list']:
            temperatures.append(entry['main']['temp'])
            dates.append(entry['dt_txt'])
        
        return temperatures, dates
    else:
        print("Erro:", response.status_code, response.json())
        return None, None

def plot_temperature_forecast():
    temperatures, dates = get_5_day_forecast()
    
    if temperatures and dates:
        dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in dates]
        
        plt.figure(figsize=(10, 5))
        plt.plot(dates, temperatures, marker='o', color='#f38600', label='Temperatura Média')
        
        plt.title('Previsão de Temperatura para os Próximos 5 Dias')
        plt.ylabel('Temperatura (°C)')

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))

        plt.grid()
        plt.legend()
        plt.tight_layout()

        grafico_path = './data/grafico_previsao.png'
        plt.savefig(grafico_path)
        plt.close()
        
        return grafico_path
    else:
        return None

@bot.message_handler(commands=["previsao"])
def previsao(message):
    grafico_path = plot_temperature_forecast()
    
    if grafico_path:
        with open(grafico_path, 'rb') as graph:
            bot.send_photo(message.chat.id, graph)
    else:
        bot.send_message(message.chat.id, "Não foi possível obter os dados de temperatura.")
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao2")

@bot.message_handler(commands=["opcao2"])
def opcao2(message):
    text = """
    O que você quer? (Clique em uma opção)
    /temperatura Consultar a temperatura atual
    /umidade Consultar a umidade do ar
    /vento Consultar a velocidade do vento
    /previsao Consultar a previsão dos próximos 5 dias"""
    bot.send_message(message.chat.id, text)
    bot.send_message(message.chat.id, "Clique aqui para voltar: /inicio")

def check(message):
    return True

@bot.message_handler(func=check)
def inicio(message):
    text = """
    Escolha uma opção para continuar (Clique no item):
    /opcao1 Obter informações do rio Itabapoana
    /opcao2 Obter informações do clima local"""
    bot.reply_to(message, text)

bot.polling()
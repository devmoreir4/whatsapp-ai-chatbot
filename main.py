import os
import requests
import telebot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

import matplotlib
matplotlib.use('Agg') # backend não interativo

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

dados_modificados = None

def load_and_replace_data():
    global dados_modificados
    arquivo_xlsx = 'river_data.xlsx'
    df = pd.read_excel(arquivo_xlsx)
    dados_modificados = df.replace({"Dado Nulo": np.nan, 999999.0: np.nan})
    print("Data loaded and replaced.")

load_and_replace_data()

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

def generate_daily_graph():

    global dados_modificados

    dados_filtrados = dados_modificados.tail(48)

    plt.figure(figsize=(10, 5))
    plt.plot(dados_filtrados['Hora'], dados_filtrados['Último Nível'], marker='o', color='#2F57FF', label='Último Nível')
    plt.title('Nível do Rio nas Últimas 24 Horas')
    plt.xlabel('Hora')
    plt.ylabel('Último Nível (m)')
    plt.ylim(0, 3)
    plt.xticks(rotation=45)
    plt.legend()
    
    grafico_path = './data/daily_graph.png'
    plt.savefig(grafico_path)
    plt.close()
    
    return grafico_path

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
    # Filtrando apenas as colunas "Data e Hora" e "Nível do rio (m) - Último"
    df_filtered = df[["Data e Hora", "Nível do rio (m) - Último"]].copy()
    
    # Convertendo a coluna "Data e Hora" para o formato datetime
    df_filtered["Data e Hora"] = pd.to_datetime(df_filtered["Data e Hora"], format="%d/%m/%Y %H:%M")
    
    # Filtrando apenas os dados da data atual
    today = datetime.today().date()
    df_today = df_filtered[df_filtered["Data e Hora"].dt.date == today]
    
    # Extraindo a hora e o último nível para o gráfico
    df_today["Hora"] = df_today["Data e Hora"].dt.strftime("%H:%M")
    df_today["Último Nível"] = pd.to_numeric(df_today["Nível do rio (m) - Último"], errors="coerce")
    
    # Plotando o gráfico
    plt.figure(figsize=(10, 5))
    plt.plot(df_today["Hora"], df_today["Último Nível"], marker='o', color='#2F57FF', label='Último Nível')
    plt.title('Nível do Rio nas Últimas 24 Horas')
    plt.xlabel('Hora')
    plt.ylabel('Último Nível (m)')
    plt.ylim(0, 3)
    plt.xticks(rotation=45)
    plt.legend()
    
    # Salvando o gráfico
    grafico_path = './data/grafico_diario.png'
    plt.savefig(grafico_path)
    plt.close()
    
    return grafico_path

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

    river_data = get_river_data()
    if river_data:
        df = save_to_excel(river_data)
        grafico_path = plot_daily_river_level(df)
        print(f"Gráfico salvo em: {grafico_path}")

    # grafico_path = generate_daily_graph()
    
    # with open(grafico_path, 'rb') as graph:
    #     bot.send_photo(message.chat.id, graph)
    # bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

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

def check(message):
    return True

@bot.message_handler(func=check)
def responder(message):
    text = """
    Escolha uma opção para continuar (Clique no item):
    /opcao1 Obter informações do rio Itabapoana
    /opcao2 Obter informações do clima local"""
    bot.reply_to(message, text)

bot.polling()
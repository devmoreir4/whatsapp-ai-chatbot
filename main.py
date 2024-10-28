import os
import requests
import telebot
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

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

@bot.message_handler(commands=["grafico"])
def grafico(message):
    bot.send_message(message.chat.id, "Exibindo o gráfico do histórico...")
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["grafico_anual"])
def grafico(message):
    bot.send_message(message.chat.id, "Exibindo o gráfico anual...")
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["grafico_mensal"])
def grafico(message):
    bot.send_message(message.chat.id, "Exibindo o gráfico mensal...")
    bot.send_message(message.chat.id, "Clique aqui para voltar: /opcao1")

@bot.message_handler(commands=["grafico_semanal"])
def grafico(message):
    bot.send_message(message.chat.id, "Exibindo o gráfico dos ultimos 7 dias...")
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
    /grafico Exibir gráfico do histórico do nível do rio
    /grafico_anual Exibir gráfico do nível do rio no último ano
    /grafico_mensal Exibir gráfico do nível do rio nos últimos 30 dias
    /grafico_semanal Exibir gráfico do nível do rio nos últimos 7 dias
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
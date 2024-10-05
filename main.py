import os
import telebot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["nivel"])
def nivel(message):
    bot.send_message(message.chat.id, "O nível do rio é de 1.5m")

@bot.message_handler(commands=["grafico"])
def grafico(message):
    bot.send_message(message.chat.id, "Exibindo o gráfico, clique aqui para iniciar: /iniciar")

@bot.message_handler(commands=["camera"])
def camera(message):
    bot.send_message(message.chat.id, "Câmera de monitoramento disponível em: https://aguasdocaparao.com.br/bom-jesus-do-itabapoana/")

@bot.message_handler(commands=["opcao1"])
def opcao1(message):
    text = """
    O que você quer? (Clique em uma opção)
    /nivel Consultar o nível do rio
    /grafico Gráfico do nível do rio
    /camera Acessar a câmera de moitoramento"""
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
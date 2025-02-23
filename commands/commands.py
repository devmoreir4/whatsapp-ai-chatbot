import os
import requests

from bs4 import BeautifulSoup
import pandas as pd

import matplotlib
matplotlib.use('Agg')  # backend não interativo
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.dates as mdates
from datetime import datetime


SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# ------- informações do rio -------

def get_river_level():
    url = "http://alertadecheias.inea.rj.gov.br/alertadecheias/214109520.html"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all("span", {"class": "count_top"})
            for element in elements:
                if "Nível as" in element.text:
                    div = element.find_next("div", {"class": "count"})
                    if div:
                        level = div.text.strip()
                        return f"O nível atual do rio é de {level} m"
        return "Erro ao acessar o site."
    except Exception as e:
        return f"Erro: {e}"

def get_quota():
    url = "http://alertadecheias.inea.rj.gov.br/alertadecheias/214109520.html"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            elements = soup.find_all("span", {"class": "count_top"})
            for element in elements:
                if "Cota de transbordamento" in element.text:
                    div = element.find_next("div", {"class": "count"})
                    if div:
                        quota = div.text.strip()
                        return f"A cota de transbordamento atual é de {quota}"
        return "Erro ao acessar o site."
    except Exception as e:
        return f"Erro: {e}"

def get_river_data():
    url = "http://alertadecheias.inea.rj.gov.br/alertadecheias/214109520.html"
    try:
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
                return None
        else:
            return None
    except Exception as e:
        return None

def save_to_excel(data, filename="dados.xlsx"):
    columns = [
        "Data e Hora", "Chuva (mm) - Último", "Chuva (mm) - 1h", 
        "Chuva (mm) - 4h", "Chuva (mm) - 24h", "Chuva (mm) - 96h", 
        "Chuva (mm) - 30d", "Nível do rio (m) - Último"
    ]
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(filename, index=False)
    return df

def plot_daily_river_level(df, output_path='./commands/images/grafico_diario.png'):
    try:
        df_filtered = df[["Data e Hora", "Nível do rio (m) - Último"]].copy()
        df_filtered["Data e Hora"] = pd.to_datetime(df_filtered["Data e Hora"], format="%d/%m/%Y %H:%M")
        today = datetime.today().date()
        df_today = df_filtered[df_filtered["Data e Hora"].dt.date == today].copy()
        df_today["Nível do rio (m) - Último"] = pd.to_numeric(
            df_today["Nível do rio (m) - Último"].replace("Dado Nulo", pd.NA), errors="coerce"
        )
        df_today["Hora"] = df_today["Data e Hora"].dt.strftime("%H:%M")

        plt.figure(figsize=(10, 5))
        plt.plot(df_today["Hora"], df_today["Nível do rio (m) - Último"], marker='o', color='#2F57FF', label='Último Nível')
        plt.title('Nível do Rio nas Últimas 24 Horas')
        plt.xlabel('Hora')
        plt.ylabel('Último Nível (m)')
        plt.ylim(0, 3)
        plt.xticks(rotation=45)
        plt.gca().invert_xaxis()
        plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=10))
        plt.legend()
        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path)
        plt.close()

        return output_path
    
    except Exception as e:
        return None

# ------- informações do clima -------

def get_weather(city):
    if not OPENWEATHER_API_KEY:
        return None
    
    link = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&lang=pt_br"
    
    try:
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
    except Exception as e:
        return None

def get_5_day_forecast():
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not OPENWEATHER_API_KEY:
        return None, None
    lat = -21.1339
    lon = -41.6797
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    try:
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
            return None, None
    except Exception as e:
        return None, None

def plot_temperature_forecast(output_path='./commands/images/grafico_previsao.png'):
    temperatures, dates = get_5_day_forecast()
    if temperatures and dates:
        try:
            dates = [datetime.strptime(date, "%Y-%m-%d %H:%M:%S") for date in dates]
            plt.figure(figsize=(10, 5))
            plt.plot(dates, temperatures, marker='o', color='#f38600', label='Temperatura Média')
            plt.title('Previsão de Temperatura para os Próximos 5 Dias')
            plt.ylabel('Temperatura (°C)')
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))
            plt.grid()
            plt.legend()
            plt.tight_layout()
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            plt.savefig(output_path)
            plt.close()

            return output_path
        
        except Exception as e:
            return None
    else:
        return None

# ------- handlers dos comandos -------

def handle_nivel(waha, chat_id):
    response_message = get_river_level() + "\n"
    waha.send_message(chat_id, response_message)

def handle_cota(waha, chat_id):
    response_message = get_quota() + "\n"
    waha.send_message(chat_id, response_message)

def handle_grafico_diario(waha, chat_id):
    data = get_river_data()
    if data:
        df = save_to_excel(data)
        grafico_path = plot_daily_river_level(df)
        if grafico_path:
            filename = os.path.basename(grafico_path)
            image_url = f"{SERVER_URL}/images/{filename}"
            waha.send_message(chat_id, f"Visualize o gráfico diário do nível do rio: {image_url}")
        else:
            waha.send_message(chat_id, "Não foi possível gerar o gráfico diário.")
    else:
        waha.send_message(chat_id, "Não foi possível obter os dados do rio.")

def handle_camera(waha, chat_id):
    url_camera = "https://aguasdocaparao.com.br/bom-jesus-do-itabapoana/"
    message = f"Câmera de monitoramento disponível em: {url_camera}"
    waha.send_message(chat_id, message)

def handle_temperatura(waha, chat_id):
    city = "Bom Jesus do Itabapoana"
    clima = get_weather(city)
    if clima:
        response_message = f"Clima em {city.capitalize()}: {clima['descricao']}. Temperatura: {clima['temperatura']:.2f}ºC"
    else:
        response_message = "Erro ao acessar a API do clima."
    waha.send_message(chat_id, response_message)

def handle_umidade(waha, chat_id):
    city = "Bom Jesus do Itabapoana"
    clima = get_weather(city)
    if clima:
        response_message = f"Clima em {city.capitalize()}: {clima['descricao']}. Umidade: {clima['umidade']}%"
    else:
        response_message = "Erro ao acessar a API do clima."
    waha.send_message(chat_id, response_message)

def handle_vento(waha, chat_id):
    city = "Bom Jesus do Itabapoana"
    clima = get_weather(city)
    if clima:
        response_message = f"Clima em {city.capitalize()}: {clima['descricao']}. Velocidade do vento: {clima['vento']:.2f} m/s"
    else:
        response_message = "Erro ao acessar a API do clima."
    waha.send_message(chat_id, response_message)

def handle_previsao(waha, chat_id):
    grafico_path = plot_temperature_forecast()
    if grafico_path:
        filename = os.path.basename(grafico_path)
        image_url = f"{SERVER_URL}/images/{filename}"
        waha.send_message(chat_id, f"Visualize o gráfico da previsão de temperatura: {image_url}")
    else:
        waha.send_message(chat_id, "Não foi possível obter os dados de temperatura.")


def handle_command(waha, chat_id, message):
    if message.startswith("/nivel"):
        handle_nivel(waha, chat_id)
    elif message.startswith("/cota"):
        handle_cota(waha, chat_id)
    elif message.startswith("/grafico_diario"):
        handle_grafico_diario(waha, chat_id)
    elif message.startswith("/camera"):
        handle_camera(waha, chat_id)
    elif message.startswith("/temperatura"):
        handle_temperatura(waha, chat_id)
    elif message.startswith("/umidade"):
        handle_umidade(waha, chat_id)
    elif message.startswith("/vento"):
        handle_vento(waha, chat_id)
    elif message.startswith("/previsao"):
        handle_previsao(waha, chat_id)
    else:
        return False
    return True

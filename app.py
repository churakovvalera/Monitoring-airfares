import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

app = Flask(__name__)

def get_flight_data(origin, destination, date):
    try:
        # Преобразуем строку в объект datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        # Преобразуем дату в нужный формат
        formatted_date = date_obj.strftime("%d%m")
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return []

    # Формируем корректную ссылку
    url = f"https://www.aviasales.ru/search/{origin}{formatted_date}{destination}1"


    # Настраиваем веб-драйвер
    driver = webdriver.Chrome()  # Убедитесь, что у вас установлен ChromeDriver и он находится в PATH
    driver.get(url)

    try:
        # Увеличиваем время ожидания
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ticket-desktop'))
        )
    except Exception as e:
        print(f"Error waiting for page to load: {e}")
        driver.quit()
        return []

    # Извлекаем данные страницы
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    flights = []
    for flight in soup.find_all('div', class_='ticket-desktop'):
        try:
            price = flight.find('div', {'data-test-id': 'price'}).text.strip()
            departure_time = flight.find_all('div', {'data-test-id': 'text'})[0].text.strip()
            departure_airport = flight.find_all('div', {'data-test-id': 'text'})[1].text.strip()
            arrival_time = flight.find_all('div', {'data-test-id': 'text'})[2].text.strip()
            arrival_airport = flight.find_all('div', {'data-test-id': 'text'})[3].text.strip()

            flights.append({
                'price': price,
                'departure_time': departure_time,
                'departure_airport': departure_airport,
                'arrival_time': arrival_time,
                'arrival_airport': arrival_airport,
                'date': date
            })
        except AttributeError as e:
            print(f"Error parsing flight data: {e}")
            continue

    print(f"Found {len(flights)} flights")
    for flight in flights:
        print(flight)

    return flights
def create_table():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT,
            price TEXT,
            flight_number TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_to_db(flights):
    create_table()  # Создаем таблицу перед вставкой данных
    conn = sqlite3.connect('flights.db')
    df = pd.DataFrame(flights)
    df.to_sql('flights', conn, if_exists='append', index=False)
    conn.close()


def analyze_data():
    conn = sqlite3.connect('flights.db')
    df = pd.read_sql('SELECT * FROM flights', conn)
    conn.close()

    # Пример простого анализа: средняя цена по датам
    df['price'] = df['price'].str.replace('₽', '').str.replace(' ', '').astype(float)
    avg_prices = df.groupby('date')['price'].mean()
    return avg_prices


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    origin = request.form['origin']
    destination = request.form['destination']
    date = request.form['date']

    flights = get_flight_data(origin, destination, date)
    save_to_db(flights)

    return render_template('results.html', flights=flights)


if __name__ == '__main__':
    app.run(debug=True)

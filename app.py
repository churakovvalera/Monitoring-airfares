from datetime import datetime
import sqlite3
import pandas as pd
from flask import Flask, request, render_template
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def get_flight_data(origin, destination, date):
    try:
        # Преобразуем строку в объект datetime
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        # Преобразуем дату в нужный формат для Aviasales (ddmm)
        formatted_date = date_obj.strftime("%d%m")
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return []

    # Формируем корректную ссылку
    url = f"https://www.aviasales.ru/search/{origin}{formatted_date}{destination}1"
    print(f"URL: {url}")

    # Установка драйвера для Chrome
    service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    # Для скрытия окна браузера используйте:
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url)

    max_wait_time = 60  # Увеличиваем время ожидания до 1 минуты

    try:
        # Ждем появления элементов с информацией о рейсах
        WebDriverWait(driver, max_wait_time).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.ticket-desktop'))
        )

        flight_elements = driver.find_elements(By.CSS_SELECTOR, '.ticket-desktop')

        flights = []
        for flight in flight_elements:
            try:
                price = flight.find_element(By.CSS_SELECTOR, '[data-test-id="price"]').text.strip()
                departure_time = flight.find_element(By.CSS_SELECTOR, '[data-test-id="time-departure"]').text.strip()
                departure_airport = flight.find_element(By.CSS_SELECTOR, '[data-test-id="airport-departure"]').text.strip()
                arrival_time = flight.find_element(By.CSS_SELECTOR, '[data-test-id="time-arrival"]').text.strip()
                arrival_airport = flight.find_element(By.CSS_SELECTOR, '[data-test-id="airport-arrival"]').text.strip()

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

    except TimeoutException:
        print("Timed out waiting for flight elements to appear")
        return []

    finally:
        driver.quit()

def create_table():
    conn = sqlite3.connect('flights.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price TEXT,
            departure_time TEXT,
            departure_airport TEXT,
            arrival_time TEXT,
            arrival_airport TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(flights):
    create_table()  # Создаем таблицу перед вставкой данных
    conn = sqlite3.connect('flights.db')
    try:
        df = pd.DataFrame(flights)
        df['price'] = df['price'].str.replace('₽', '').str.replace(' ', '').astype(float)
        df.to_sql('flights', conn, if_exists='append', index=False)
    except Exception as e:
        print(f"Error saving to DB: {e}")
    finally:
        conn.close()

def analyze_data():
    conn = sqlite3.connect('flights.db')
    try:
        df = pd.read_sql('SELECT * FROM flights', conn)
        df['price'] = df['price'].str.replace('₽', '').str.replace(' ', '').astype(float)
        avg_prices = df.groupby('date')['price'].mean()
        return avg_prices
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    origin = request.form['origin']
    destination = request.form['destination']
    date = request.form['date']

    flights = get_flight_data(origin, destination, date)
    if flights:
        save_to_db(flights)
        return render_template('results.html', flights=flights)
    else:
        return "No flights found."

if __name__ == '__main__':
    app.run(debug=True)

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from flask import Flask, request, render_template

app = Flask(__name__)


def get_flight_data(origin, destination, date):
    url = f"https://www.aviasales.ru/search/{origin}{destination}{date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    flights = []
    for flight in soup.find_all('div', class_='ticket-desktop'):
        try:
            time = flight.find('div', class_='segment__time').text.strip()
            price = flight.find('div', class_='price').text.strip()
            flight_number = flight.find('span', class_='flight__number').text.strip()

            flights.append({
                'time': time,
                'price': price,
                'flight_number': flight_number,
                'date': date
            })
        except AttributeError:
            continue

    return flights


def save_to_db(flights):
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

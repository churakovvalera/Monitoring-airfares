import requests
from bs4 import BeautifulSoup


def parse_aviasales(date, origin, destination):
    # Форматируем дату в нужный для сайта Aviasales формат "DDMM"
    formatted_date = date[5:7]+ date[8:]  # получаем "DDMM"

    url = f'https://www.aviasales.ru/search/{origin}{formatted_date}{destination}1'
    print(url)
    response = requests.get(url)

    # Проверяем успешность запроса
    if response.status_code != 200:
        print(f"Failed to retrieve data from Aviasales. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')  # используем 'html.parser'
    tickets = soup.find_all('div', class_='ticket-desktop')

    if not tickets:
        print("No tickets found for the given date and route.")
        return

    for ticket in tickets:
        time = ticket.find('time', class_='ticket-flight-time').text.strip()
        price = ticket.find('span', class_='price').text.strip()
        link = 'https://www.aviasales.ru' + ticket.find('a', class_='buy-button')['href']

        print(f"Time: {time}, Price: {price}, Link: {link}")
        print("----------------------------------------------------------")


if __name__ == '__main__':
    date = input("Enter date (YYYY-MM-DD): ")
    origin = input("Enter origin airport code: ")
    destination = input("Enter destination airport code: ")

    parse_aviasales(date, origin, destination)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Настройка ChromeOptions
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск в фоновом режиме

# Установка ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL сайта
url = "https://avia.tema.ru/flights/TOF1610AER1"

# Загрузка страницы
driver.get(url)

# Извлечение данных
flight_details = driver.find_element(By.CLASS_NAME, 'flight-details')

# Город вылета
departure_city_elem = flight_details.find_element(By.CLASS_NAME, 'flight-brief-city')
departure_city = departure_city_elem.text.strip()

# Время вылета
departure_time_elem = flight_details.find_element(By.CLASS_NAME, 'flight-brief-time')
departure_time = departure_time_elem.text.strip()

# Город пересадки
layover_city_elem = flight_details.find_element(By.CLASS_NAME, 'flight-brief-layover__iata')
layover_city = layover_city_elem.text.strip()

# Время пересадки
layover_time_elem = flight_details.find_element(By.CLASS_NAME, 'flight-details-layover__time')
layover_time = layover_time_elem.text.strip()

# Город прибытия
arrival_city_elems = flight_details.find_elements(By.CLASS_NAME, 'flight-brief-city')
arrival_city = arrival_city_elems[-1].text.strip()

# Время прибытия
arrival_time_elems = flight_details.find_elements(By.CLASS_NAME, 'flight-brief-time')
arrival_time = arrival_time_elems[-1].text.strip()

# Цена
price_elem = driver.find_element(By.CLASS_NAME, 'currency_font.currency_font--rub')
price = price_elem.text.strip()

# Вывод данных в табличном виде
print(f"1) Город вылета: {departure_city}")
print(f"2) Время вылета: {departure_time}")
print(f"3) Город пересадки: {layover_city}")
print(f"4) Время пересадки: {layover_time}")
print(f"5) Город прибытия: {arrival_city}")
print(f"6) Время прибытия: {arrival_time}")
print(f"7) Цена: {price}")

# Закрытие драйвера
driver.quit()
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from pytest import fixture

import string
import random


@fixture(scope="function")
def driver(request):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

    request.cls.driver = driver 
    
    yield driver

    driver.quit()

@fixture(scope="function")
def user_info():
    """
    Данные для регистрации тестового пользователя.
    Email генерируется случайно.
    """
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=5))
    
    return (f"test_user{random_string}@mail.ru", "12345")

@fixture(scope="function")
def university_names():
    return {"ГУАП", "СПБГЭТУ ЛЭТИ", "МПУ", "МТУСИ", "СПБПУ"}
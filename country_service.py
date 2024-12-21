import re
import requests
from utils import translate_to_russian, set_prefix, headers

list_country = []

with open('country.txt') as f:
    for i in f:
        list_country.append(re.match(r'^[^\(]+(?=\s?\()', i).group(0).strip())

COUNTRIES_API = "https://restcountries.com/v3.1/"
COUNTRY_INFO = "translation/"
BORDERS_INFO = "alpha/"
ALL_INFO = "all/"


def countries_requests(country_name):
    response = requests.get(f"{COUNTRIES_API}{COUNTRY_INFO}{country_name}", headers=headers)
    response.raise_for_status()
    return response.json()[0]

def get_country_info(country_name):
    country = countries_requests(country_name)
    name = country.get("translations", {}).get("rus", {}).get("common", "Неизвестно")
    capital = ", ".join((country.get("capital", ["Неизвестно"])))
    population = set_prefix(country.get("population", "Неизвестно"))
    area = set_prefix(country.get("area", "Неизвестно"))
    region = country.get("region", "Неизвестно")
    subregion = country.get("subregion", "Неизвестно")
    flag_url = country.get("flags", {}).get("png", "")
    currencies = ", ".join([f"{v['name']} ({k})" for k, v in country.get("currencies", {}).items()])
    languages = ", ".join([lang for lang in country.get("languages", {}).values()])
    info = (f"Информация о стране:\n"
            f"Название: {name}\n"
            f"Столица: {capital}\n"
            f"Население: {population}\n"
            f"Площадь: {area} км²\n"
            f"Регион: {region}\n"
            f"Субрегион: {subregion}\n"
            f"Языки: {languages}\n"
            f"Валюта: {currencies}")
    return translate_to_russian(info), flag_url    
        
def get_neighbors(country_name):
    country = countries_requests(country_name)
    neighbors = country.get("borders", [])
    if not neighbors:
        return "У этой страны нет соседей."
    neighbor_names = []
    for neighbor in neighbors:
        response = requests.get(f"{COUNTRIES_API}{BORDERS_INFO}{neighbor}", headers=headers)
        response.raise_for_status()
        neighbor_data = response.json()
        neighbor_names.append(neighbor_data[0]["translations"]["rus"]["common"])
    return f"Соседние страны: {', '.join(neighbor_names)}"
        

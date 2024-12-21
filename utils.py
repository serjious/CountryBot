import requests

TRANSLATE_API = "https://ftapi.pythonanywhere.com/translate?sl=en&dl=ru&text="
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

def translate_to_russian(text):
    try:
        response = requests.get(f"{TRANSLATE_API}{text}", headers=headers)
        response.raise_for_status()
        return response.json()["destination-text"]
    except Exception as e:
        return text 
        
def set_prefix(value: int) -> str:
    prefix = {1E9: "млрд", 1E6: "млн", 1E3: "тыс"}
    for divisor, label in prefix.items():
        if value >= divisor:
            result = round(value / divisor, 2) 
            return f"{result} {label}"
    return str(value)


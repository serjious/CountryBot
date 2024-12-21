import re
import random
from country_service import list_country, get_country_info

def generate_batch():
    four_coun = random.sample(list_country,4)
    win_coun = random.choice(four_coun)
    info, flag_url = get_country_info(win_coun)
    return flag_url, four_coun, win_coun

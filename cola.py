import requests
from bs4 import BeautifulSoup
from datetime import datetime

def calculate_total_pay_month(loc_code: str, rank: str, depend: int, service: str, barracks: str) -> float:
    total_pay_month = 0
    s = requests.Session()

    now = datetime.now()
    month = now.month - 1 if now.month > 1 else 12
    year = now.year if now.month > 1 else now.year - 1
    
    days = ["01", "16"]

    for day in days:
        url = f"https://www.defensetravel.dod.mil/pdcgi/cola-oha/o_cola4.cgi?year={year}&month={month}&day={day}&LOCCODE={loc_code}&LOCCODE2=&CINDEX2=&RANK={rank}&DEPEND={depend+2}&SERVICE={service}&BARRACK={barracks}&submit1=CALCULATE"

        res = s.get(url)

        html_doc = res.text

        soup = BeautifulSoup(html_doc, 'html.parser')

        total_pay_element = soup.find('b', string='TOTAL PAY PERIOD ALLOWANCE:')
        if total_pay_element is not None:
            total_pay = total_pay_element.find_next('b').text.strip()
            total_pay_month += float(total_pay.strip('$'))

    return total_pay_month

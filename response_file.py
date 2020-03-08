from bs4 import BeautifulSoup
def fun(html):
    soup  = BeautifulSoup(html.decode('utf-8'), 'html.parser')
    text = soup.text
    return True


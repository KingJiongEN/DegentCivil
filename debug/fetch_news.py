import requests
from bs4 import BeautifulSoup

def fetch_bbc_sports_news():
    url = 'https://www.bbc.co.uk/sport'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        with open('tmp/sout_result.html', 'w') as f:
            f.write(soup.prettify())
        #class="ssrcss-zmz0hi-PromoLink exn3ah91" ssrcss-bnuh0n-PromoSwitchLayoutAtBreakpoints et5qctl0
        news_sections = soup.find_all('div', class_='ssrcss-bnuh0n-PromoSwitchLayoutAtBreakpoints et5qctl0') 
        for section in news_sections:
            __import__('pdb').set_trace()
            articles = section.find_all('a')  # Assuming articles are links within the section
            for article in articles:
                title = article.text.strip()
                link = article['href']
                print(f"Title: {title}\nURL: {link}\n")
    else:
        print("Failed to access the mystical realms of BBC Sport.")

if __name__ == '__main__':
    fetch_bbc_sports_news()

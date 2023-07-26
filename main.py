from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

website = 'https://global.abb/group/en/media/releases/stories?&offset=0'
options = Options()
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.51 Safari/537.35'
options.add_argument(f'user-agent={user_agent}')
options.add_experimental_option("detach", True)

website_driver = webdriver.Chrome(
    service=Service(
    ChromeDriverManager(driver_version='114.0.5735.90').install()
    ),
    options=options
)
website_driver.get(website)

accept_cookies_xpath = '//a[@id="btnSelectAllCheckboxes"]'
WebDriverWait(website_driver, 10).until(
    EC.presence_of_element_located((By.XPATH, accept_cookies_xpath))
)
accept_all_cookies = website_driver.find_element(By.XPATH, accept_cookies_xpath)
accept_all_cookies.click()

news_hyperlinks = website_driver.find_elements(By.XPATH, '//a[@class="cmp-news-archive__header__link"]')

links = [hlink.get_attribute('href') for hlink in news_hyperlinks]

website_driver.quit()

all_articles = []
for l in links:
    print('sleep . . .')
    time.sleep(20)
    print(l)
    story_driver = webdriver.Chrome(
                service=Service(
                ChromeDriverManager(driver_version='114.0.5735.90').install()
                ),
                options=options
            )

    story_driver.get(l)
    deny_cookies_xpath = '//div[@class="cmp-abb-cta"][2]'
    WebDriverWait(story_driver, 20).until(
        EC.presence_of_element_located((By.XPATH, deny_cookies_xpath))
    )
    print('sleep . . .')
    time.sleep(10)
    refuse_all_cookies = story_driver.find_element(By.XPATH, deny_cookies_xpath)
    try:
        refuse_all_cookies.click()
    except:
        pass

    title = story_driver.find_element(By.XPATH, '//h1[@class="oneabb-newsbank-news-Header-title"]').text
    genre = story_driver.find_element(By.XPATH, '//span[@property="genre"]').text
    dateline = story_driver.find_element(By.XPATH, '//span[@property="dateline"]').text
    date_published = story_driver.find_element(By.XPATH, '//time[@property="datePublished"]').text
    
    try:
        description = story_driver.find_element(By.XPATH, '//p[@property="description"]').text
    except:
        description = ''
    
    paragraphs = story_driver.find_elements(By.XPATH, '//p[@class="oneabb-newsbank-news-ArticleTypography-paragraph"]')

    article_text = '\n'.join([p.text for p in paragraphs])

    all_articles.append({
        'title': title,
        'genre': genre,
        'dateline': dateline,
        'date_published': date_published,
        'description': description,
        'article_link': l,
        'article_text': article_text
    })
    story_driver.quit()

df = pd.DataFrame(all_articles)
print(df)
df.to_excel('articles.xlsx', index=False)
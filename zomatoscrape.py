import pandas as pd
import time
from collections import OrderedDict
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

start = time.time()

headers = {
    'authority': 'scrapeme.live',
    'dnt': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'none',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cookie': 'G_AUTHUSER_H=0; PHPSESSID=c6a8fd7d09d51eeb86404674f53f6aae; fre=0; rd=1380000; zl=en; fbtrack=9c61342575c9519af32c7f3719d90235; _gcl_au=1.1.1969674177.1660285909; cid=2c4e3ed9-0308-4d16-a237-3a5c99f7e944; G_ENABLED_IDPS=google; uspl=true; ltv=30776; lty=30776; locus={"addressId":0,"lat":18.56608625,"lng":73.77851125,"cityId":5,"ltv":30776,"lty":"zomato_place_v2","fetchFromGoogle":false,"dszId":8472,"fen":"Baner,+Balewadi+Phata,+Baner,+India"}; dpr=1; _fbp=fb.1.1660801754528.604803115; expab=2; _gid=GA1.2.183807741.1660928682; _ga_2XVFHLPTVP=GS1.1.1660928682.14.0.1660928682.0.0.0; _ga=GA1.1.342986048.1660285910; AWSALBTG=hgmgcuBo0lqIkzf/KxklaKEiwnbZdsSE7rqbBO638Cn+kGVcjjCGQWoMI9FYCD+9GdHCXDzPqQV9Z/N8Gk7EPsYVFAyWKXADhSsKNfOLjc4VAn8s0tbimuJ3J26w/0hTezXR1XBH9wSPHxSJI820tP8JXTHUV7V31BQllz5+U1Je; AWSALBTGCORS=hgmgcuBo0lqIkzf/KxklaKEiwnbZdsSE7rqbBO638Cn+kGVcjjCGQWoMI9FYCD+9GdHCXDzPqQV9Z/N8Gk7EPsYVFAyWKXADhSsKNfOLjc4VAn8s0tbimuJ3J26w/0hTezXR1XBH9wSPHxSJI820tP8JXTHUV7V31BQllz5+U1Je; AKA_A2=A; fbcity=4; csrf=f57e7b709bfd439dbd92f33724657aff; zat=4I4H4cAy881XFnhfua3dTcaFMgfSsQ3CVMqo9pFqfhw.YgKr6Ls58SVzxjXVKiQNyptbUEJBHRNPUGK9XrkGbPw; ttaz=1663520740',
}

driver = webdriver.Chrome("./chromedriver")  # this might need a change since i am working in pycharm you might need to import os

driver.get(
    "https://www.zomato.com/pune/delivery")  # url of the website of particular cities you want to scrap.

time.sleep(2)  # Allow 2 seconds for the web page to (open depends on you)
scroll_pause_time = 3  # You can set your own pause time. dont slow too slow that might not able to load more data
screen_height = driver.execute_script("return window.screen.height;")  # get the screen height of the web
i = 1

while True:
    # scroll one screen height each time
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    # Break the loop when the height we need to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        break

# creating soup
soup = BeautifulSoup(driver.page_source, "html.parser")
divs = soup.findAll('div', class_='jumbo-tracker')

# create all the list here according to data needs
urls = []
rest_name = []
ratings = []
price = []
crusine = []
for parent in divs:  # zomato is very anti-scrapping website it changes class of the data dynamically (jumbo tracker is the only fixed things i can find)

    #  name of the restaurant is stored in the h4 tags and luckily it was unique in main class
    name_tag = parent.find("h4")

    # appending the name to rest_name list
    try:
        rest_name.append(name_tag.text)
    except AttributeError:
        continue

    #  links of the restaurants are in a tags hence we are using it find and then getting href where links are stored
    link_tag = parent.find("a")

    base = "https://www.zomato.com"  # since we don not get whole link https attached we need to join the link with base
    try:
        if 'href' in link_tag.attrs:
            link = link_tag.get('href')
    except:
        pass
    url = urljoin(base, link)
    urls.append(url)


    rating_tag = parent.div.a.next_sibling.div.div.div.div.div.div.div.text
    price_tag = parent.div.a.next_sibling.p.next_sibling.text
    crusine_tag = parent.div.a.next_sibling.p.text
    ratings.append(rating_tag)
    price.append(price_tag)
    crusine.append(crusine_tag)

out_df2 = pd.DataFrame({'links': urls, 'names': rest_name, 'ratings': ratings, 'price for one': price, 'crusine': crusine})
# we need to create a data frame to neatly view the data in csv format, just add the lists below

# noinspection PyTypeChecker
out_df2.to_csv("Pune_test.csv")
#  creating csv for information
driver.close()

zomato = pd.read_csv('Pune_test.csv')
links = []
fields = ['Menu', 'Price']
filename = "pune.csv"
fo = open(filename, "w")
csvwriter = csv.writer(fo)
csvwriter.writerow(fields)

for i in range(len(urls)):
    link = zomato['links'][i]
    links.append(link)
    print(link)
    link = "https://www.zomato.com/pune/mh-12-pav-bhaji-rasta-peth/order"
    req = requests.get(link, headers=headers)
    soup = BeautifulSoup(req.text, "lxml")

    # Menu categories
    menu_dict = OrderedDict()
    menu = soup.findAll('p', class_="sc-1hez2tp-0")
    for i in menu:
        if '(' in i.text:
            key = ((i.text).split('('))[0]
            value = ((i.text).split('('))[-1]
            value= int(value.strip(')'))
            menu_dict[key] = value
    print(menu_dict)

    # Offers
    coupons = []
    offers = soup.findAll('div', class_='sc-1a03l6b-2 gerWzu')
    for offer in offers:
        print(offer.text)
        if '%' in offer.text:
            off = ((offer.text).split('%'))[0] + "%"
        elif 'Flat' in offer.text:
            off = ((offer.text).split('OFF'))[0].strip()
        else:
            off = ""
        coupon = ((offer.text).split('code'))[-1].strip()

        try:
            upto = ((((offer.text).split('use'))[0]).split('to'))[1]
        except IndexError:
            upto = ""

        coupon_dict = {}
        coupon_dict['off']= off
        coupon_dict['coupon']= coupon
        coupon_dict['upto']= upto
        coupons.append(coupon_dict)
    print(coupons)

    items = soup.findAll("div", class_="sc-1s0saks-17 bGrnCu")
    for item in items:
        name = item.find('h4', class_="sc-1s0saks-15 iSmBPS").text
        print(name)
        price = item.find('span', class_="sc-17hyc2s-1 cCiQWA").text
        print(price)

        try:
            try:
                status = item.find('div', class_="sc-1tx3445-0 kcsImg sc-1s0saks-0 jcidl")['type']
            except TypeError:
                status = item.find('div', class_="sc-1tx3445-0 kcsImg sc-1s0saks-6 eEOGnT")['type']
        except:
            status = 'unknown'
        print(status)

        try:
            description = item.find('p', class_="sc-1s0saks-12 hcROsL").text
            print(description)
        except AttributeError:
            description = ""
        ratings = item.find('div', class_="sc-z30xqq-3 bewuUV")
        try:
            stars = ratings.findAll('i')
            for index,star in enumerate(stars):
                x = star.find('lineargradient')
                if x:
                    y = x.findAll('stop')[1]['offset']
                    rating = index+((int(y.strip('%')))/100)
                    print(rating)
        except AttributeError:
            rating = 0
    break

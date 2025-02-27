import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import pickle
from datetime import datetime

from datetime import datetime, time
import smtplib, ssl

from dotenv import load_dotenv
load_dotenv()

import schedule
import time as tm

import os
SECRET_KEY = os.getenv("EMAIL")
my_email = os.getenv("MYEMAIL")

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def cleanhtml(raw_html):
  cleanr = re.compile('&amp;')
  cleantext = re.sub(cleanr, '&', raw_html)
  return cleantext

def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def get_list(meal):
    for element in meal:
        string = cleanhtml(element.get_attribute('innerHTML'))
        string = string.replace("*", "")
        list = string.split("<br>")
        for item in range(len(list)):
            list[item] = list[item].strip()
        
    return list

def send_text(message,tolist,password):
    for to in tolist:
        sender_email = my_email
        server = smtplib.SMTP( "smtp.gmail.com", 587 )

        server.starttls()

        server.login( sender_email, SECRET_KEY )

        # Send text message through SMS gateway of destination number
        server.sendmail( 'Haverford Menu', to, message )

def getmenu_new():
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    driver = webdriver.Chrome('/Users/johnf/Documents/Haverford/Projects/Menu/chromedriver', options=chrome_options)  # Optional argument, if not specified will search path.

    driver.get('https://www.haverford.edu/dining-services/dining-center')
    
    try:
        mealone = driver.find_elements_by_xpath('//*[@id="today_menu_1"]/div[1]')
        mealtwo = driver.find_elements_by_xpath('//*[@id="today_menu_1"]/div[2]')
        mealthree = driver.find_elements_by_xpath('//*[@id="today_menu_1"]/div[3]')
    except:
        mealone = driver.find_elements_by_xpath('//*[@id="today_menu_1"]/div[1]')
        mealtwo = driver.find_elements_by_xpath('//*[@id="today_menu_1"]/div[2]')

    menudict = {}

    for meal in [mealone, mealtwo, mealthree]:

        for element in meal:
            mealinfo = element.text.replace("*", "")
            mealinfo = mealinfo.splitlines()
            text = mealinfo

        i = 0
        mealtype = ""
        for smalltext in text:
            if i == 0:
                mealtype = smalltext
            if not smalltext or smalltext == "Add to calendar" or i == 0:
                text.remove(smalltext)
            i += 1

        menudict[mealtype] = text
    
    return menudict

def get_today_menu_new():
    open('./obj/menu-info.pkl', 'w').close()
    date = datetime.today().strftime('%Y-%m-%d')
    save_obj({date: getmenu_new()}, "menu-info")

def get_today_menu():
    open('./obj/menu-info.pkl', 'w').close()
    chrome_options = Options()  
    chrome_options.add_argument("--headless")  
    driver = webdriver.Chrome('/Users/johnf/Documents/Haverford/Projects/Menu/chromedriver')  # Optional argument, if not specified will search path.

    driver.get('https://www.haverford.edu/dining-services/dining-center')
    breakfast = driver.find_elements_by_xpath("/html/body/div[2]/main/div/div[2]/div/div[4]/div/div/div/div[3]/div[17]/div/div/div/div/div/div/dl/dd/div[1]/div/div[1]/div/div/div/div[1]/div[1]/p")
    lunch = driver.find_elements_by_xpath("/html/body/div[2]/main/div/div[2]/div/div[4]/div/div/div/div[3]/div[17]/div/div/div/div/div/div/dl/dd/div[1]/div/div[1]/div/div/div/div[1]/div[2]/p")
    dinner = driver.find_elements_by_xpath("/html/body/div[2]/main/div/div[2]/div/div[4]/div/div/div/div[3]/div[17]/div/div/div/div/div/div/dl/dd/div[1]/div/div[1]/div/div/div/div[1]/div[3]/p")

    breaky = get_list(breakfast)
    lunchy = get_list(lunch)
    dinny = get_list(dinner)  

    driver.quit()

    date = datetime.today().strftime('%Y-%m-%d')
    todaymeal = {date: {"breakfast": breaky, "lunch": lunchy, "dinner": dinny}}

    save_obj(todaymeal, "menu-info")

def main():
    EMAIL_LIST = os.getenv("EMAIL_LIST").split(",")
    get_today_menu_new()
    try:
        menuinfo = load_obj("menu-info")
        print(menuinfo)
        date = datetime.today().strftime('%Y-%m-%d')

        if len(menuinfo[date]) == 0:
            get_today_menu_new()
    except:
        get_today_menu()
        menuinfo = load_obj("menu-info")
        date = datetime.today().strftime('%Y-%m-%d')

    #do magic
    menuinfo = load_obj("menu-info")
    date = datetime.today().strftime('%Y-%m-%d')

    if len(menuinfo[date]) == 3:
        if is_time_between(time(7,00), time(8,00)):
            count = 1
            msg = """\nBreakfast: """
            for item in menuinfo[date]["Breakfast"]:
                if count == len(menuinfo[date]["Breakfast"]):
                    msg = msg + "and " + str(item)
                else:
                    msg = msg + str(item) + ", "
                count += 1
            send_text(msg, EMAIL_LIST, SECRET_KEY)
        elif is_time_between(time(11,00), time(12,00)):
            count = 1
            msg = """\nLunch: """
            for item in menuinfo[date]["Lunch"]:
                if count == len(menuinfo[date]["Lunch"]):
                    msg = msg + "and " + str(item)
                else:
                    msg = msg + str(item) + ", "
                count += 1
            send_text(msg, EMAIL_LIST, SECRET_KEY)
        elif is_time_between(time(17,00), time(18,00)):
            count = 1
            msg = """\nDinner: """
            for item in menuinfo[date]["Dinner"]:
                if count == len(menuinfo[date]["Dinner"]):
                    msg = msg + "and " + str(item)
                else:
                    msg = msg + str(item) + ", "
                count += 1
            send_text(msg, EMAIL_LIST, SECRET_KEY)
    elif len(menuinfo[date]) == 2:
        if is_time_between(time(7,00), time(8,00)):
            count = 1
            msg = """\Brunch: """
            for item in menuinfo[date]["Brunch"]:
                if count == len(menuinfo[date]["Brunch"]):
                    msg = msg + "and " + str(item)
                else:
                    msg = msg + str(item) + ", "
                count += 1
            send_text(msg, EMAIL_LIST, SECRET_KEY)
        elif is_time_between(time(11,00), time(12,00)):
            count = 1
            msg = """\Dinner: """
            for item in menuinfo[date]["Dinner"]:
                if count == len(menuinfo[date]["Dinner"]):
                    msg = msg + "and " + str(item)
                else:
                    msg = msg + str(item) + ", "
                count += 1
            send_text(msg, EMAIL_LIST, SECRET_KEY)
    else:
        # send dinner
        print("Nothing")
        # send_text("\nSubject new message!",EMAIL_LIST,SECRET_KEY)

schedule.every().hour.at(":01").do(main)

while True:
    schedule.run_pending()
    tm.sleep(1)
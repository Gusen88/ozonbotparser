import time
from sched import scheduler
from selenium_stealth import stealth
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from aiogram import Bot, Dispatcher, types, executor
import asyncio
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import pymysql
from config import db_name,user,password,host
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup



try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print("Connection succeful")
    try:
        # with connection.cursor() as cursor:
        #     insert_query = "INSERT INTO `users` (tid, link2) VALUES ('1121', 'https://www.ozon.ru/product/pogruzhnoy-blender-philips-hr2657-90-7-v-1-s-ovoshcherezkoy-spiralayzerom-stakanom-485330788/?avtc=1&avte=4&avts=1701774049');"
        #     cursor.execute(insert_query)
        #     connection.commit()


        with connection.cursor() as cursor:
            select_all_rows = "SELECT * FROM `users`"
            cursor.execute(select_all_rows)
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            print("#" * 20)
    except Exception as ex:
        print("bad")
        print(ex)
except Exception as ex:
    print("bad")
    print(ex)

#Настройка вебдрайвера
# PROXY = "172.67.11.143:80"
options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--ignore_ssl")
# options.add_argument(f'--proxy-server={PROXY}')

s = Service(executable_path='C:\\Users\\User\\PycharmProjects\\ozonbot\\chromedriver.exe')
#Настройка клавиатуры
button_1 = KeyboardButton('Добавить ссылку')
button_2 = KeyboardButton('Мои ссылки')
button_3 = KeyboardButton('Удалить ссылку')
button_4 = KeyboardButton('Изменить процент')
keyb = ReplyKeyboardMarkup(resize_keyboard=True)
keyb.add(button_1)
keyb.add(button_2)
keyb.add(button_3)
keyb.add(button_4)
#Настройка бота
bot = Bot(token='6797957063:AAFzUgD4ZksCxPmi_JBUkOpq7JF-EIdOFjI')
dp = Dispatcher(bot, storage=MemoryStorage())




class States(StatesGroup):
    delete2 = State()
    parse2 = State()
    perc = State()

def checkemptylink(tid):
        with connection.cursor() as cursor:
            select_all_rows = f"SELECT link1,link2,link3 FROM `users` WHERE tid = {tid}"
            cursor.execute(select_all_rows)
            rows = cursor.fetchall()
            rowsst = f"{rows}"
            linksnumber = 0
            for row in rowsst[1:len(rowsst)-2].split(','):
                linksnumber += 1
                rowst = f"{row}"
                linkstart = rowst.find(": ")
                linkend = rowst.find("}")
                print(rowst[linkstart+2:])
                if rowst[linkstart+2:] == 'None':
                    print(f'PUSTO {linksnumber}')
                    return linksnumber

def checktoregister(tid):
    with connection.cursor() as cursor:
        select_all_rows = "SELECT tid FROM `users`"
        cursor.execute(select_all_rows)
        rows = cursor.fetchall()
        for row in rows:
            rowst = f"{row}"
            linkstart = rowst.find(": ")
            linkend = rowst.find("}")
            if int(rowst[linkstart + 2:linkend]) == tid:
                return 1
def addusertodb(tid):
    try:
        with connection.cursor() as cursor:
            insert_query = f"INSERT INTO `users` (tid) VALUES ({tid});"
            cursor.execute(insert_query)
            connection.commit()
    except Exception as ex:
            print("bad")
            print(ex)

def columnscount():
    with connection.cursor() as cursor:
        request = f"SELECT * from `users`"
        cursor.execute(request)
        columns = cursor.fetchall()
        for column in columns:
            column = f"{column}"
        print(column)
        columnscount = int((column.count("':") - 4)/4)
        print(f"COLUMNSCOUNT = {columnscount}")
        return columnscount


def alllinkscount(tid):
    with connection.cursor() as cursor:
        request = f"SELECT * from `users`"
        cursor.execute(request)
        columns = cursor.fetchall()
        alllinks = "link1"
        for column in columns:
            column = f"{column}"
        print(column)
        columnscount = int((column.count("':") - 4)/4)
        print(f"COLUMNSCOUNT = {columnscount}")
        for i in range(columnscount - 1):
            alllinks += f",link{i + 2}"

        print(alllinks)
        connection.commit()

        select_all_rows = f"SELECT {alllinks} FROM `users` WHERE tid = {tid}"
        cursor.execute(select_all_rows)
        rows = cursor.fetchall()
        rowsst = f"{rows}"
        linksnumber = 1
        for row in rowsst[1:len(rowsst) - 2].split(','):
            rowst = f"{row}"
            linkstart = rowst.find(": ")
            linkend = rowst.find("}")
            # print(rowst[linkstart+2:])
            if rowst[linkstart + 2:] == 'None':
                print(f'PUSTO {linksnumber}')
                break
            linksnumber += 1

        connection.commit()

        print(columnscount)
        print(linksnumber)
        if linksnumber > columnscount:
            pricewithcard = "pricewithcard"
            pricewithoutcard = "pricewithoutcard"
            link = "link"
            name = "name"
            create_new_column = f"ALTER TABLE `users` ADD {link + str(linksnumber)} VARCHAR(512)"
            cursor.execute(create_new_column)
            connection.commit()
            create_new_column = f"ALTER TABLE `users` ADD {pricewithcard + str(linksnumber)} INT"
            cursor.execute(create_new_column)
            connection.commit()
            create_new_column = f"ALTER TABLE `users` ADD {pricewithoutcard + str(linksnumber)} INT"
            cursor.execute(create_new_column)
            connection.commit()
            create_new_column = f"ALTER TABLE `users` ADD {name + str(linksnumber)} VARCHAR(255)"
            cursor.execute(create_new_column)
            connection.commit()
        return linksnumber
def addlink(tid,link,number,pwc,pwoc,name):
    linksnumber = 'link' + str(number)
    try:
        with connection.cursor() as cursor:
            insert_addlinktousers = f"UPDATE `users` SET `{linksnumber}` = '{link}' WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
            insert_addlinktousers = f"UPDATE `users` SET `{'pricewithcard' + str(number)}` = '{int(pwc[:len(pwc)-1])}' WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
            insert_addlinktousers = f"UPDATE `users` SET `{'pricewithoutcard' + str(number)}` = '{int(pwoc[:len(pwoc)-1])}' WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
            insert_addlinktousers = f"UPDATE `users` SET `{'name' + str(number)}` = '{name}' WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
    except Exception as ex:
            print("error in def addlink")
            print(ex)

def changelink(tid,number):
    with connection.cursor() as cursor:
        select_nextlink = f"SELECT {'link' + str(number+1)} FROM `users` WHERE tid = {tid}"

        cursor.execute(select_nextlink)
        link = f"{cursor.fetchall()}"
        linkstart = link.find("':")
        link = (link[linkstart + 3:len(link) - 2])
        stringlink = f"{link}"
        print(f"stringlink : {stringlink}")
        names,priceswcard,priceswocard,links,linkscount = mylink(tid)
        if stringlink != "None":
            try:
                insert_addlinktousers = f"UPDATE `users` SET `{'link' + str(number)}` = '{links[number]}' WHERE (`tid` = '{tid}');"
                cursor.execute(insert_addlinktousers)
                connection.commit()
                insert_addlinktousers = f"UPDATE `users` SET `{'pricewithcard' + str(number)}` = '{priceswcard[number]}' WHERE (`tid` = '{tid}');"
                cursor.execute(insert_addlinktousers)
                connection.commit()
                insert_addlinktousers = f"UPDATE `users` SET `{'pricewithoutcard' + str(number)}` = '{priceswocard[number]}' WHERE (`tid` = '{tid}');"
                cursor.execute(insert_addlinktousers)
                connection.commit()
                insert_addlinktousers = f"UPDATE `users` SET `{'name' + str(number)}` = '{names[number]}' WHERE (`tid` = '{tid}');"
                cursor.execute(insert_addlinktousers)
                connection.commit()
                changelink(tid,number+1)
            except Exception as ex:
                print(ex)
        else:
            dellink(tid,number)


def dellink(tid,number):
    try:
        with connection.cursor() as cursor:
            insert_addlinktousers = f"UPDATE `users` SET `{'link' + str(number)}` = null WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
            insert_addlinktousers = f"UPDATE `users` SET `{'pricewithcard' + str(number)}` = null WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
            insert_addlinktousers = f"UPDATE `users` SET `{'pricewithoutcard' + str(number)}` = null WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
            insert_addlinktousers = f"UPDATE `users` SET `{'name' + str(number)}` = null WHERE (`tid` = '{tid}');"
            cursor.execute(insert_addlinktousers)
            connection.commit()
    except Exception as ex:
        print(ex)

def mylink(tid):
    names = []
    links = []
    priceswocard = []
    priceswcard = []
    linkscount = 0
    with connection.cursor() as cursor:
        try:
            for i in range(1, alllinkscount(tid)):
                selectname = f"SELECT {'name' + str(i)} FROM `users` WHERE tid = '{tid}'"
                cursor.execute(selectname)
                name = cursor.fetchall()
                if name != "None":
                    linkscount += 1
                    name = f"{name}"
                    namestart = name.find("':")
                    names.append(name[namestart+4:len(name)-3])
                    selectpwc = f"SELECT {'pricewithcard' + str(i)} FROM `users` WHERE tid = '{tid}'"
                    cursor.execute(selectpwc)
                    pwc = f"{cursor.fetchall()}"
                    pwcstart = pwc.find("':")
                    priceswcard.append(pwc[pwcstart+3:len(pwc)-2])
                    selectpwoc = f"SELECT {'pricewithoutcard' + str(i)} FROM `users` WHERE tid = '{tid}'"
                    cursor.execute(selectpwoc)
                    pwoc = f"{cursor.fetchall()}"
                    pwocstart = pwoc.find("':")
                    priceswocard.append(pwoc[pwocstart+3:len(pwoc)-2])
                    selectlink = f"SELECT {'link' + str(i)} FROM `users` WHERE tid = '{tid}'"
                    cursor.execute(selectlink)
                    link = f"{cursor.fetchall()}"
                    linkstart = link.find("':")
                    links.append(link[linkstart+4:len(link)-3])

            connection.commit()
        except Exception as ex:
            print(ex)
    return names,priceswcard,priceswocard,links,linkscount


def parseprice(URL,times):
    try:
        times +=1
        # PROXY = "185.158.114.235:29140"

        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 OPR/104.0.0.0 (Edition Yx GX)")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore_ssl")
        # options.add_argument(f'--proxy-server={PROXY}')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        s = Service(executable_path='C:\\Users\\User\\PycharmProjects\\ozonbot\\chromedriver.exe')

        driver = webdriver.Chrome(options=options,service=s,)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
          '''
        })


        stealth(driver,
                languages="[ru-RU,ru,en-US,en]",
                vendor="Google Inc.",
                platform="Win64",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True)

        driver.get(url=URL)
        time.sleep(10)
        try:
            elementname = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[2]/div/div/div[1]/div")
            name = (BeautifulSoup(elementname.text,"html.parser")).text
        except Exception as ex:
            print(ex)

        try:
            elementwcard = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span")
        except:
            try:
                elementwcard = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[3]/div[3]/div/div[11]/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span")
            except:
                elementwcard = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[3]/div[2]/div[2]/div/div[1]/div[1]/div/div/div[1]/div/div/div[1]/span[1]")
        pricewcard = (((BeautifulSoup(elementwcard.text, "html.parser")).text).replace('\u2009', ''))
        print("Цена с картой : "+ pricewcard)
        try:
            elementwocard = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[3]/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]")
        except:
            try:
                elementwocard = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[3]/div[3]/div/div[11]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]")
            except:
                elementwocard = driver.find_element("xpath","/html/body/div[1]/div/div[1]/div[4]/div[3]/div[2]/div[2]/div/div[1]/div[1]/div/div/div[1]/div/div/div[1]/span[1]")
        pricewocard = (((BeautifulSoup(elementwocard.text, "html.parser")).text).replace('\u2009', ''))
        print("\nЦена без карты : "+pricewocard)
        #driver.save_full_page_screenshot("ozon.png")
        driver.close()
        return pricewcard,pricewocard,name,times
    except Exception as ex:
        try:
            driver.close()
        except:
            pass
        print(ex)
        return 0,0,0,times

def setperc(tid,perc):
    try:
        with connection.cursor() as cursor:
            req = f"UPDATE `users` SET `percent` = {perc} WHERE (`tid` = '{tid}')"
            cursor.execute(req)
            connection.commit()
    except Exception as ex:
        print(ex)

@dp.message_handler(commands=['test'])
async def test(message:types.Message):
    driver = webdriver.Chrome(service=s, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
              '''
    })
    driver.get(url="https://2ip.ru")
    # driver.get(url="https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html")
    time.sleep(20)
    driver.close()
@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    if checktoregister(message.from_user.id) != 1:
        addusertodb(message.from_user.id)
        print("Добавляю в бд")
        await message.answer("Это бот для отслеживания цены товаров на Озон\nУкажите процент изменения цены, при котором Вам буду присылаться сообщения", reply_markup=keyb)
        await States.perc.set()
    else:
        print("Данный пользователь уже есть в бд")
        await message.answer("Рад снова Вас видеть!",reply_markup=keyb)

@dp.message_handler(state = States.perc)
async def percent(message:types.message,state:FSMContext):
    try:
        perc = int(message.text)
        setperc(message.from_user.id,perc)
        await message.answer(f"Вы установили процент : {perc}%")
    except Exception as ex:
        print(ex)
        await message.answer("Ошибка. Попробуйте снова")
    await state.finish()

@dp.message_handler(text = "Изменить процент")
async def changeperc(message:types.message):
    await message.answer(f"Укажите процент")
    await States.perc.set()

@dp.message_handler(text = "Мои ссылки")
async def mylinks(message:types.Message):
    names,pwc,pwoc,links,a = mylink(message.from_user.id)
    if a != 0:
        strlink = ""
        for i in range(a):
            strlink += (str(i+1) + " : " + names[i] + "\n" + "Цена по карте: " + pwc[i] + "\nЦена без карты: " + pwoc[i] + "\nСсылка: " + links[i]+"\n\n")
        await message.answer(strlink)
    else:
        await message.answer(f"Вы ещё не добавляли ссылки")

@dp.message_handler(text = "Удалить ссылку")
async def delete(message:types.Message):
    await States.delete2.set()
    await message.answer("Введите номер товара, который хотите удалить")

@dp.message_handler(state = States.delete2)
async def delete2(message:types.Message, state:FSMContext):
    await message.answer(f"Товар удалён")
    await state.finish()
    number = int(message.text)
    changelink(message.from_user.id,number)

@dp.message_handler(text = 'Добавить ссылку')
async def parse(message:types.Message):
    await message.answer("Отправьте ссылку")
    @dp.message_handler()
    async def parse2(message:types.Message):
        emtylinksnumber = alllinkscount(message.from_user.id)
        link = message.text
        print(link)
        pwc, pwoc, name, times = parseprice(link,0)
        while times <= 5:
            if (pwc or pwoc or name) == 0 and times <= 5:
                await asyncio.sleep(10)
                pwc, pwoc, name, times = parseprice(link, times)
            else:
                times = 6
        else: print(f"Ошибка не получилось спарсить товар")
        if (pwc == 0 or pwoc == 0 or name == 0):
            await message.answer(f"Ошибка. Попробуйте позже")
        else:
            await message.answer(f"Товар: {name}\nЦена с картой : {pwc}\nЦена без карты : {pwoc}")
            addlink(message.from_user.id,link,emtylinksnumber,pwc,pwoc,name)
async def checkprice():
    while True:
        try:
            with connection.cursor() as cursor:
                rowscount = cursor.execute("SELECT * FROM users")
                columns = columnscount()
                print(f"{rowscount} : {columns}")
                for i in range(1,rowscount+1):
                    for k in range(1,columns+1):
                        error = 0
                        select_nextlink = f"SELECT {'link' + str(k)} FROM `users` WHERE id = {i}"
                        cursor.execute(select_nextlink)
                        link = f"{cursor.fetchall()}"
                        linkstart = link.find("':")
                        linknone = (link[linkstart + 3:len(link) - 2])
                        stringlink = f"{linknone}"
                        print(f"stringlink : {stringlink}")
                        if stringlink != "None":
                            link = (link[linkstart + 4:len(link) - 3])
                            pwc, pwoc, name, times = parseprice(link,0)
                            while times <= 5:
                                if (pwc or pwoc or name) == 0 and times <= 5:
                                    await asyncio.sleep(10)
                                    pwc, pwoc, name, times = parseprice(link, times)
                                else:
                                    times = 6
                            else:
                                error = 1
                                print(f"Ошибка не получилось спарсить товар")

                            if error != 1:
                                select_price = f"SELECT {'pricewithcard' + str(k)} FROM `users` WHERE id = {i}"
                                cursor.execute(select_price)
                                price = f"{cursor.fetchall()}"
                                pricestart = price.find("':")
                                price = int(price[pricestart + 3:len(price) - 2])
                                print(f"price : {price}")
                                select_pricewoc = f"SELECT {'pricewithoutcard' + str(k)} FROM `users` WHERE id = {i}"
                                cursor.execute(select_pricewoc)
                                pricewoc = f"{cursor.fetchall()}"
                                pricewocstart = pricewoc.find("':")
                                pricewoc = int(pricewoc[pricewocstart + 3:len(pricewoc) - 2])
                                print(f"pricewoc : {pricewoc}")
                                select_perc = f"SELECT percent FROM `users` WHERE id = {i}"
                                cursor.execute(select_perc)
                                perc = f"{cursor.fetchall()}"
                                percstart = perc.find("':")
                                perc = int(perc[percstart + 3:len(perc) - 2])
                                print(f"percent : {perc}")
                                select_tid = f"SELECT tid FROM `users` WHERE id = {i}"
                                cursor.execute(select_tid)
                                tid = f"{cursor.fetchall()}"
                                tidstart = tid.find("':")
                                tid = int(tid[tidstart + 3:len(tid) - 2])
                                print(f"tid : {tid}")
                                if float(pwc[:len(pwc)-1]) < (float(price) - (perc/100)):
                                    print(f"Нужно отправить сообщение")
                                    await bot.send_message(tid,f"Цена по товару {name} изменилась. Теперь она составляет : \nПо карте - {pwc}\nБез карты - {pwoc}")
                                    request_change_pricewc = f"UPDATE `users` SET `{'pricewithcard' + str(k)}` = {int(pwc[:len(pwc)-1])} WHERE (`id` = '{i}');"
                                    cursor.execute(request_change_pricewc)
                                    connection.commit()
                                    request_change_pricewoc = f"UPDATE `users` SET `{'pricewithoutcard' + str(k)}` = {int(pwoc[:len(pwoc)-1])} WHERE (`id` = '{i}');"
                                    cursor.execute(request_change_pricewoc)
                                    connection.commit()

                        else:
                            break

        except Exception as ex:
            print(ex)
        await asyncio.sleep(10)

async def main():
    bot = Bot(token='6797957063:AAFzUgD4ZksCxPmi_JBUkOpq7JF-EIdOFjI')
    asyncio.create_task(checkprice())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

connection.close()
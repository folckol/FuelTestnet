import os
import random
import shutil
import time
import traceback

import ua_generator
from logger import logger

from playwright.sync_api import sync_playwright

class PWModel:

    def __init__(self,number, twoCaptcha, proxy=None):
        self.playwright = sync_playwright().start()

        self.number = number
        self.proxy = proxy
        self.twoCaptcha = twoCaptcha

        EX_path, EX_path_2 = "FuelWallet", "2Captcha"

        user_data_dir = f"{os.getcwd()}\\dataDir"

        self.context = self.playwright.chromium.launch_persistent_context(user_data_dir,
                                                                          user_agent=ua_generator.generate(device="desktop", browser="chrome").text,
                                                                     proxy={
            "server": f"{proxy.split(':')[0]}:{proxy.split(':')[1]}",
            "username": f"{proxy.split(':')[2]}",
            "password": f"{proxy.split(':')[3]}",
        } if proxy != None else None,headless=False, devtools=False, args=[f'--load-extension={os.getcwd()}\\{EX_path},{os.getcwd()}\\{EX_path_2}',
                                               f'--disable-extensions-except={os.getcwd()}\\{EX_path},{os.getcwd()}\\{EX_path_2}'
                                               ])

        self.page = self.context.new_page()

        self.page.set_default_timeout(60000)

    def TwoCaptchaActivation(self):
        self.CaptchaPage = self.context.new_page()

        self.CaptchaPage.wait_for_timeout(3000)
        self.CaptchaPage.bring_to_front()
        self.CaptchaPage.goto('chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html')
        self.CaptchaPage.wait_for_selector('[name="apiKey"]').fill(self.twoCaptcha)
        self.CaptchaPage.wait_for_timeout(1000)
        self.CaptchaPage.wait_for_selector('button[data-lang="login"]').click()
        self.CaptchaPage.wait_for_timeout(3000)

        logger.success(f"{self.number} | Плагин 2Captcha успешно активирован")


    def CreateNewWallet(self):

        for page in self.context.pages:
            if page.url == "chrome-extension://dldjpboieedgcmpkchcjcbijingjcgok/index.html#/sign-up/welcome":
                self.page = page
                break

        self.page.bring_to_front()

        self.page.wait_for_selector('xpath=//*[@id="root"]/main/div/div/div[3]/article[1]').click()
        self.page.wait_for_selector('button[id="agreeTerms"]').click()
        self.page.wait_for_timeout(1000)
        self.page.wait_for_selector('xpath=//*[@id="root"]/main/div/div/div[5]/button[2]').click()

        self.page.wait_for_selector('button[aria-label="Copy button"]')
        self.mnemonic = []
        for i in range(12):
            self.mnemonic.append(self.page.query_selector(f'[data-idx="{i+1}"]').text_content())

        self.page.wait_for_selector('[role="checkbox"]').click()
        self.page.wait_for_timeout(1000)
        self.page.wait_for_selector('xpath=//*[@id="root"]/main/div/div/div[2]/div[3]/button[2]').click()

        self.page.wait_for_selector('input[role="textbox"]')
        c = 0
        for element in self.page.query_selector_all('input[role="textbox"]'):
            element.fill(self.mnemonic[c])
            c+=1
        self.page.wait_for_selector('xpath=//*[@id="root"]/main/div/div/div[3]/div[2]/button[2]').click()

        self.page.wait_for_selector('input[name="password"]').fill('Password123123123!')
        self.page.wait_for_selector('input[name="confirmPassword"]').fill('Password123123123!')
        self.page.wait_for_selector('xpath=//*[@id="root"]/main/div/form/div/div[3]/div[2]/button[2]').click()

        self.page.wait_for_timeout(5000)

        logger.success(f"{self.number} | Кошелек создан")

    def Faucet(self):

        self.page.goto("https://app.swaylend.com/#/faucet")

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[1]/div[1]/header/div[3]/div/button').click()
        self.page.wait_for_timeout(2000)

        pages = len(self.context.pages)
        self.page.wait_for_selector('xpath=/html/body/div[3]/div/div[2]/div/div[2]/div/div/div[6]').click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")

        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[3]/button[2]').click()
        self.page.wait_for_timeout(1000)
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[3]/button[2]').click()

        self.page.wait_for_timeout(5000)

        pages = len(self.context.pages)

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[1]/div[2]/div/span/div/div[1]/table/tbody/tr[1]/td[4]/button').click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")

        self.faucetPage = self.context.pages[-1]

        self.faucetPage.bring_to_front()
        self.faucetPage.wait_for_selector('div.captcha-solver').click()

        f = 0
        while f < 200:
            try:
                res = self.faucetPage.query_selector('div.captcha-solver-info').text_content()
                if res == "ERROR_ZERO_BALANCE":
                    logger.error("Пополните капчу")
                    return "Error"
                elif res == "Капча решена!":
                    logger.success(f"{self.number} | Капча успешно решена")
                    break
                else:

                    continue
            except:
                pass

            f+=1

        if f >= 200:
            logger.error("Слишком долгое ожидание решения")
            return "Error"

        self.faucetPage.wait_for_selector('input[value="Give me Ether"]').click()
        self.faucetPage.wait_for_selector('xpath=//*[@id="explorer-link"]')

        self.page.bring_to_front()

        d = [2, 3, 4, 5, 6, 7]
        random.shuffle(d)
        for i in d:
            self.page.bring_to_front()
            pages = len(self.context.pages)
            self.page.wait_for_selector(f'xpath=//*[@id="root"]/div[1]/div[2]/div/span/div/div[1]/table/tbody/tr[{i}]/td[4]/button').click()
            _ = 0
            while pages == len(self.context.pages) and _ < 60:
                self.page.wait_for_timeout(1000)

            if _ >= 60:
                raise Exception("Превышено время ожидания")

            self.walletPage = self.context.pages[-1]
            self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

            self.page.wait_for_timeout(6000)
            self.walletPage = self.context.pages[-1]
            self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()
            self.page.wait_for_timeout(random.randint(1000, 8000))

        # self.page.wait_for_timeout(2000000)
        logger.success(f"{self.number} | Все токены успешно получены")

    def Staking(self):

        self.page.goto("https://app.swaylend.com/#/dashboard")

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[1]/div[2]/div/div[3]/div[1]/div/div[2]/div[3]/div[2]')

        self.page.wait_for_timeout(random.randint(2000,6000))

        for i in range(random.randint(3, 8)):
            elements = self.page.query_selector_all('[alt="symbol"]')

            a = 0
            while a < 2:

                try:
                    elem = random.randint(1, 4) * 2 - 2
                    elements[elem].click()

                    self.page.wait_for_timeout(1000)
                    quantity = float(self.page.wait_for_selector(
                        'div[id*="react-collapsed-panel"] > div > div > p[type="secondary"]').text_content().split(' ')[
                                         0])

                    self.page.wait_for_timeout(1000)

                    self.page.wait_for_selector('input[type="number"]').fill(str(quantity*(random.randint(9,20)/100)))

                    self.page.wait_for_timeout(2000)
                    self.page.wait_for_selector('xpath=//button[text()="Supply"]', timeout=5000).click()

                    self.page.wait_for_timeout(2000)
                    self.walletPage = self.context.pages[-1]
                    self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

                    break
                except:
                    pass

                a+=1


            self.page.wait_for_timeout(random.randint(10000, 18000))
            self.page.wait_for_selector('div[id*="react-collapsed-panel"] > div > button')

        logger.success(f"{self.number} | Стейкинг совершен")

    def SwaySwap(self):

        self.page.goto("https://fuellabs.github.io/swayswap/welcome/connect")

        pages = len(self.context.pages)
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/div/section/div/div/button').click()
        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")

        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[3]/button[2]').click()
        self.page.wait_for_timeout(2000)
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[3]/button[2]').click()

        self.page.wait_for_timeout(2000)
        pages = len(self.context.pages)
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/div/section/div/div/button').click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")

        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

        self.page.wait_for_timeout(4000)

        pages = len(self.context.pages)

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/div/section/div/div/button').click()

        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")

        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

        self.page.wait_for_selector('input[aria-label="Accept the use agreement"]').click()
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/div/section/div/div/button').click()

        self.page.wait_for_selector('input[inputmode="decimal"]')

        if random.choice([1,2]) == 1:
            self.Swaps()
            self.Pools()
        else:
            self.Pools()
            self.Swaps()

        logger.success(f"{self.number} | SwaySwap все действия выполнены")


    def Swaps(self):

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/main/div[2]/div[2]/div/button[1]').click()
        self.page.wait_for_timeout(random.randint(2000, 5000))

        for i in range(random.randint(2,6)):
            swap_from, swap_to = self.page.query_selector_all('input[inputmode="decimal"]')
            balance_from = float(self.page.query_selector(
                'xpath=//*[@id="root"]/div[2]/main/div[3]/div/div[3]/div[1]/div/div[2]/div').text_content().split(' ')[
                                     -1])

            swap_from.fill(str(balance_from*(random.randint(5,20)/100)))
            pages = len(self.context.pages)
            self.page.wait_for_selector('button[aria-label="Swap button"]').click()
            _ = 0
            while pages == len(self.context.pages) and _ < 60:
                self.page.wait_for_timeout(1000)
            if _ >= 60:
                raise Exception("Превышено время ожидания")

            self.walletPage = self.context.pages[-1]
            self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

            self.page.wait_for_timeout(random.randint(9000,26000))
            self.page.wait_for_selector('button[aria-label="Invert coins"]').click()

            swap_from, swap_to = self.page.query_selector_all('input[inputmode="decimal"]')
            balance_from = float(self.page.query_selector(
                'xpath=//*[@id="root"]/div[2]/main/div[3]/div/div[3]/div[1]/div/div[2]/div').text_content().split(' ')[-1])

            swap_from.fill(str(balance_from * (random.randint(5, 20) / 100)))
            pages = len(self.context.pages)
            self.page.wait_for_selector('button[aria-label="Swap button"]').click()
            _ = 0
            while pages == len(self.context.pages) and _ < 60:
                self.page.wait_for_timeout(1000)
            if _ >= 60:
                raise Exception("Превышено время ожидания")
            self.walletPage = self.context.pages[-1]
            self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

            self.page.wait_for_timeout(random.randint(9000, 26000))
            self.page.wait_for_selector('button[aria-label="Invert coins"]').click()

        self.page.wait_for_timeout(random.randint(9000, 26000))

        logger.success(f"{self.number} | SwaySwap свапы выполнены")

    def Pools(self):

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/main/div[2]/div[2]/div/button[2]').click()
        self.page.wait_for_timeout(random.randint(2000, 5000))

        self.page.wait_for_selector('button[aria-label="header-add-liquidity-btn"]').click()
        self.page.wait_for_timeout(random.randint(2000, 5000))

        balance = float(self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/main/div[3]/div/div[3]/div[1]/div[1]/div[2]/div').text_content().split(' ')[-1])
        self.page.wait_for_selector('input[aria-label="Coin from input"]').fill(str(balance * (random.randint(5, 20) / 100)))
        pages = len(self.context.pages)
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/main/div[3]/div/div[3]/button').click()
        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")
        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()
        
        self.page.wait_for_timeout(random.randint(9000, 26000))

        logger.success(f"{self.number} | SwaySwap пулы ликвидности пополнены")

    def NftActions(self):

        self.page.goto("https://fuelart.io/")

        self.page.wait_for_timeout(3000)
        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[3]/button[2]').click()
        self.walletPage.wait_for_timeout(1000)
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[3]/button[2]').click()

        pages = len(self.context.pages)
        self.page.wait_for_selector("xpath=/html/body/div[3]/div/div/div[2]/div/div/div/button").click()
        _ = 0
        while pages == len(self.context.pages) and _ < 60:
            self.page.wait_for_timeout(1000)
        if _ >= 60:
            raise Exception("Превышено время ожидания")
        self.walletPage = self.context.pages[-1]
        self.walletPage.wait_for_selector('xpath=//*[@id="root"]/main/div/div[2]/div[2]/button[2]').click()

        self.page.wait_for_selector("xpath=/html/body/div[3]/div/div/div[2]/div/div/div/button", state="hidden").click()

        self.page.goto("https://fuelart.io/create-item")

        self.page.wait_for_selector('input[placeholder="Item Name"]').fill(self.random_name)
        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/div/div/div/div[2]/div/div/div/div/textarea').fill(self.random_description)
        self.page.wait_for_selector('input[name="file"]').fill(f"{os.getcwd()}\\{random.choice(os.listdir(f'{os.getcwd()}/media'))}")

        self.page.wait_for_selector('xpath=//*[@id="root"]/div[2]/div/div/div/div[2]/div/div/div/div/div/button').click()

    def close(self):
        self.playwright.stop()

def generate_random_lists(L, n, k):
    result_lists = []

    while len(L) >= k:
        sublist_length = random.randint(n, k)
        sublist = L[:sublist_length]
        result_lists.append(sublist)
        L = L[sublist_length:]

    if len(L) >= n:
        sublist_length = random.randint(n, len(L))
        sublist = L[:sublist_length]
        result_lists.append(sublist)

    return result_lists

if __name__ == '__main__':

    print(' ___________________________________________________________________\n'
          '|                       Rescue Alpha Soft                           |\n'
          '|                   Telegram - @rescue_alpha                        |\n'
          '|                   Discord - discord.gg/438gwCx5hw                 |\n'
          '|___________________________________________________________________|\n\n\n')

    try:
        shutil.rmtree(f"{os.getcwd()}/dataDir")
    except:
        pass

    api_2captcha = ""
    delay = (15, 30)

    try:
        with open('config', 'r') as file:
            for i in file:
                if '2captcha=' in i.rstrip():
                    api_2captcha = i.rstrip().split('2captcha=')[-1]
                elif 'delay' in i.rstrip():
                    delay = (int(i.rstrip().split('delay=')[-1].split('-')[0]), int(i.rstrip().split('delay=')[-1].split('-')[1]))
    except:
        logger.error("Вы неправильно заполнили конфиг, проверьте данные и повторите запуск")
        input()
        exit(1)

    if api_2captcha == "":
        logger.error("Вы неправильно прописали ключ от 2captcha")
        input()
        exit(1)


    proxies = []
    with open('InputData/Proxies.txt', 'r') as file:
        for i in file:
            proxies.append(i.rstrip())

    if len(proxies) != 0 and proxies[0] != "":

        logger.warning("Вы запустили скрипт с проксями")
        time.sleep(1)
        print('')

        for i in range(len(proxies)):

            try:
                shutil.rmtree(f"{os.getcwd()}/dataDir")
            except:
                pass

            try:
                model = PWModel(i+1,api_2captcha, proxies[i])

                model.TwoCaptchaActivation()
                model.CreateNewWallet()
                model.Faucet()

                if random.choice([True, False]) == True:
                    model.Staking()
                    model.SwaySwap()
                else:
                    model.SwaySwap()
                    model.Staking()

            except Exception as e:
                traceback.print_exc()
                # model.page.wait_for_timeout(100000000)
                logger.error(f"{i+1} | Произошла ошибка ({str(e)})")


            try:
                with open("result.txt", "a+") as file:
                    mnemonic = ""
                    for m in model.mnemonic:
                        mnemonic+= m+' '
                    file.write(mnemonic+'|'+proxies[i]+'\n')
            except:
                pass

            try:
                model.close()
            except:
                pass



            time.sleep(random.randint(delay[0], delay[1]))
            print('')

    else:

        logger.warning("Вы запустили скрипт без проксей")
        time.sleep(5)
        print('')

        c = 0
        while True:

            try:
                shutil.rmtree(f"{os.getcwd()}/dataDir")
            except:
                pass

            try:
                model = PWModel(c+1, api_2captcha)

                model.TwoCaptchaActivation()
                model.CreateNewWallet()
                model.Faucet()

                if random.choice([True, False]) == True:
                    model.Staking()
                    model.SwaySwap()
                else:
                    model.SwaySwap()
                    model.Staking()

            except Exception as e:
                traceback.print_exc()
                # model.page.wait_for_timeout(100000000)
                logger.error(f"{c+1} | Произошла ошибка ({str(e)})")

            try:
                with open("result.txt", "a+") as file:
                    mnemonic = ""
                    for m in model.mnemonic:
                        mnemonic+= m+' '
                    file.write(mnemonic+'|'+proxies[i]+'\n')
            except:
                pass

            try:
                model.close()
            except:
                pass

            c+=1

            time.sleep(random.randint(delay[0], delay[1]))
            print('')


    logger.warning("Скрипт успешно завершил свою работу")
    input()


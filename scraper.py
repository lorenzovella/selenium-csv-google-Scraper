import csv
import selenium
import random
import time
#import logging
import sys
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions
#logging.basicConfig(level=logging.DEBUG)
#pyinstaller --noconfirm --onefile --console scraper.py --add-binary "C:\Users\Lorenzo Vella\Documents\alecbrabo\Selenium-csv-google-Scraper\chromedriver.exe;./"
class Scraper():
    # proxylist.txt should be in format: http://login:pass@host:port
    proxy = lambda x: random.choice(list(open('proxylist.txt')))

    def __init__(self):
        options = ChromeOptions()
        wireoptions = {
            'verify_ssl': False,
            'proxy': {
                'http': self.proxy()
            }
        }
        self.driver = Chrome(self.chrome(), options=options, seleniumwire_options=wireoptions)
        self.driver.set_page_load_timeout(30)
    def data(self, q):
        self.driver.get('https://www.google.com/search?q='+q+" hotel")
        if self.googleBlock():
            self.resetProxy();
        return {
            'phone': self.phone(),
            'address': self.address(),
            'url': self.url(),
            'newName': self.newName()
            }
    def phone(self):
        try:
            return self.driver.find_element_by_css_selector("[data-attrid='kc:/collection/knowledge_panels/has_phone:phone']>div>div>span:last-of-type>span>a>span").get_attribute('innerHTML')
        except selenium.common.exceptions.NoSuchElementException:
            return ""
    def address(self):
        try:
            return self.driver.find_element_by_css_selector("[data-attrid='kc:/location/location:address']>div>div>span:last-of-type").get_attribute('innerHTML')
        except selenium.common.exceptions.NoSuchElementException:
            return ""
    def url(self):
        try:
            return self.driver.find_element_by_css_selector("[rel='prerender']").get_attribute('href')
        except selenium.common.exceptions.NoSuchElementException:
            return ""
    def newName(self):
        try:
            return self.driver.find_element_by_css_selector("[data-attrid='title']>span").get_attribute('innerHTML')
        except selenium.common.exceptions.NoSuchElementException:
            return ""
    def googleBlock(self):
        try:
            self.driver.find_element_by_css_selector("html[itemtype='http://schema.org/SearchResultsPage']")
            return False
        except selenium.common.exceptions.NoSuchElementException:
            return True
    def resetProxy(self):
        self.driver.close()
        self.__init__()
        # newProxy = self.proxy().split(':')
        # self.driver.proxy._master.options.update(
        #     mode="upstream:"+(":").join((newProxy[0],newProxy[1],newProxy[-1])),
        #     upstream_auth=(":").join(newProxy[2].split("@"))
        # )
        raise Exception("Atualizando proxy")
    def chrome(self):
        try:
            return ChromeDriverManager().install()
        except Exception as e:
            print(e)
            time.sleep(5)
            return self.chrome()

def runReader(startFrom=0):
    with open(inputFile) as csvDataFile:
        csvReader = csv.DictReader(csvDataFile, delimiter=csvDelimiter)
        for index, row in enumerate(csvReader):
            if index <= startFrom-1:
                continue
            scrapedData = scraperInstance.data(row[hotelNameCol])
            newData.append(scrapedData)
            print("Processando "+str(len(newData))+" de "+str(numberOfLines)+" | "+scrapedData['newName'][:15]+"... | "+scrapedData['address'][:15]+"... | "+scrapedData['url'][:15]+"... | "+scrapedData['phone'][:15])

def add_column_in_csv(input_file_param, output_file):
    with open(input_file_param, 'r') as read_obj, \
            open(output_file, 'w', newline='', encoding="utf-8") as write_obj:
        csv_reader = csv.reader(read_obj, delimiter=csvDelimiter)
        csv_writer = csv.writer(write_obj, delimiter=csvDelimiter)
        for row in csv_reader:
            if csv_reader.line_num-2 < len(newData):
                transform_row(row, csv_reader.line_num)
                csv_writer.writerow(row)
    print("Arquivo "+output_file+" convertido com sucesso.")

def transform_row(row, lineNum):
    if lineNum == 1:
        row.extend(['phone','address','url','newName'])
    else:
        row.extend([
            newData[lineNum-2]['phone'],
            newData[lineNum-2]['address'],
            newData[lineNum-2]['url'],
            newData[lineNum-2]['newName']
        ])
newData = []
csvDelimiter = ";"
hotelNameCol = 'name'
scraperInstance = Scraper()
while(True):
    inputFile = input("Nome arquivo original: ")
    if inputFile != "":
        numberOfLines = sum(1 for line in open(inputFile))-1
        while len(newData) != numberOfLines:
            try:
                runReader(len(newData))
            except Exception as e:
                print(e)
                print("Retomando conversão a partir da linha "+str(len(newData)))
            except KeyboardInterrupt as e:
                print("Pesquisa interrompida e salva com "+str(len(newData))+" resultados")
                # add_column_in_csv(inputFile, inputFile.replace('.','OutputRestored-'+str(len(newData))+'.',1))
                break
        add_column_in_csv(inputFile, inputFile.replace('.','Output-'+str(len(newData))+'.',1))
        newData.clear()

import csv
import selenium
import random
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
        #options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = Chrome(ChromeDriverManager().install(), options=options, seleniumwire_options=wireoptions)
        self.driver.set_page_load_timeout(30)

    def data(self, q):
        self.driver.get('https://www.google.com.br/search?q='+q+" hotel")
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
        print("Atualizando proxy")
        newProxy = self.proxy().split(':')
        self.driver.proxy._master.options.update(
            mode="upstream:"+(":").join((newProxy[0],newProxy[1],newProxy[-1])),
            upstream_auth=(":").join(newProxy[2].split("@"))
        )
    def close(self):
        self.driver.close()
def runReader(startFrom=0):
    scraperInstance = Scraper()
    try:
        for row in csvReader:
            scrapedData = scraperInstance.data(row[hotelNameCol])
            newData.append(scrapedData)
            print("Processando "+str(len(newData))+" de "+numberOfLines+" | "+scrapedData['newName'][:15]+"... | "+scrapedData['address'][:15]+"... | "+scrapedData['url'][:15]+"... | "+scrapedData['phone'][:15])
        add_column_in_csv(inputFile, inputFile.replace('.','Output-'+str(len(newData))+'.',1),startFrom)
    except Exception as e:
        print(e)
        print("Retomando conversão a partir da linha "+str(len(newData)))
        scraperInstance.close()
        runReader(len(newData))
def add_column_in_csv(input_file, output_file, startFrom=0):
    with open(input_file, 'r') as read_obj, \
            open(output_file, 'w', newline='', encoding="utf-8") as write_obj:
        csv_reader = csv.reader(read_obj, delimiter=csvDelimiter)
        csv_writer = csv.writer(write_obj, delimiter=csvDelimiter)
        for row in csv_reader:
            if csv_reader.line_num-2 < len(newData) and csv_reader.line_num-2 >= startFrom:
                transform_row(row, csv_reader.line_num)
                csv_writer.writerow(row)
    newData.clear()
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

while(True):
    inputFile = input("Nome arquivo original: ")
    if inputFile != "":
        try:
            numberOfLines = str(sum(1 for line in open(inputFile))-1)
            with open(inputFile) as csvDataFile:
                csvReader = csv.DictReader(csvDataFile, delimiter=csvDelimiter)
                runReader()
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            print("Houve um erro e a pesquisa foi salva com "+str(len(newData))+" resultados")
            add_column_in_csv(inputFile, inputFile.replace('.','Output-'+str(len(newData))+'.',1))

import csv
import selenium
import random
# import logging
from seleniumwire import webdriver
# logging.basicConfig(level=logging.DEBUG)

class Scraper():

    # proxylist.txt should be in format: http://login:pass@host:port
    proxy = lambda x: random.choice(list(open('proxylist.txt')))

    def __init__(self):
        options = webdriver.ChromeOptions()
        wireoptions = {
            'verify_ssl': False,
             'connection_timeout': 15,
            'proxy': {
                'http': self.proxy()
            }
        }
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe',options=options, seleniumwire_options=wireoptions)

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

def add_column_in_csv(input_file, output_file):
    with open(input_file, 'r') as read_obj, \
            open(output_file, 'w', newline='', encoding="utf-8") as write_obj:
        csv_reader = csv.reader(read_obj, delimiter=csvDelimiter)
        csv_writer = csv.writer(write_obj, delimiter=csvDelimiter)
        for row in csv_reader:
            if csv_reader.line_num-2 < len(newData):
                transform_row(row, csv_reader.line_num)
                csv_writer.writerow(row)
    print("Arquivo "+output_file+" convertido com sucesso.")
def runReader():
    try:
        for row in csvReader:
            scrapedData = scraperInstance.data(row[hotelNameCol])
            newData.append(scrapedData)
            print("Processando "+str(len(newData))+" de "+numberOfLines+" | "+scrapedData['newName'][:15]+"... | "+scrapedData['address'][:15]+"... | "+scrapedData['url'][:15]+"... | "+scrapedData['phone'][:15])
        add_column_in_csv(inputFile, inputFile.replace('.','Output.',1))
    except Exception as e:
        print(e)
        add_column_in_csv(inputFile, inputFile.replace('.','OutputRestored.',1))

newData = []
csvDelimiter = ";"
hotelNameCol = 'name'
scraperInstance = Scraper()

while(True):
    inputFile = input("Nome arquivo original: ")
    if inputFile != "":
        numberOfLines = str(sum(1 for line in open(inputFile))-1)
        with open(inputFile) as csvDataFile:
            csvReader = csv.DictReader(csvDataFile, delimiter=csvDelimiter)
            runReader()

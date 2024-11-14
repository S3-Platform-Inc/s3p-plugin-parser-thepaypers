import datetime
import time

from s3p_sdk.plugin.payloads.parsers import S3PParserBase
from s3p_sdk.types import S3PRefer, S3PDocument
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class THEPAYPERS(S3PParserBase):
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    HOST = "https://thepaypers.com/news/all"

    def __init__(self, refer: S3PRefer, web_driver: WebDriver, max_count_documents: int = None,
                 last_document: S3PDocument = None):
        super().__init__(refer, max_count_documents, last_document)

        # Тут должны быть инициализированы свойства, характерные для этого парсера. Например: WebDriver
        self._driver = web_driver
        self._wait = WebDriverWait(self._driver, timeout=20)
        ...

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -

        self.driver.get(url=self.HOST)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.index_group')))

        while True:

            links = self.driver.find_elements(By.CLASS_NAME, 'details_rows')

            for link in links:

                web_link = link.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('href')
                pub_date = dateparser.parse((link.find_element(By.CLASS_NAME, 'source').text.split(' | ')[1]))
                self.driver.execute_script("window.open('');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                self.driver.get(web_link)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.article')))
                self.logger.debug(f'Entered: {web_link}')

                title = self.driver.find_element(By.TAG_NAME, 'h1').text
                abstract = None
                text_content = self.driver.find_element(By.ID, 'pageContainer').text
                cat_list = self.driver.find_elements(By.XPATH,
                                                     '//table[contains(@class,\'category_table\')]//td[@class = \'source\']')
                for cat in cat_list:
                    # self.logger.debug(cat.text)
                    if cat.text == 'Keywords:':
                        try:
                            keywords = cat.find_element(By.XPATH, './following-sibling::td').text
                        except:
                            self.logger.exception('Keywords error')
                            keywords = ''
                    if cat.text == 'Categories:':
                        try:
                            categories = cat.find_element(By.XPATH, './following-sibling::td').text
                        except:
                            categories = ''
                    if cat.text == 'Companies:':
                        try:
                            companies = cat.find_element(By.XPATH, './following-sibling::td').text
                        except:
                            companies = ''
                    if cat.text == 'Countries:':
                        try:
                            countries = cat.find_element(By.XPATH, './following-sibling::td').text
                        except:
                            countries = ''

                other_data = {'keywords': keywords,
                              'categories': categories,
                              'companies': companies,
                              'countries': countries}

                doc = S3PDocument(id=None,
                                   title=title,
                                   abstract=abstract,
                                   text=text_content,
                                   link=web_link,
                                   storage=None,
                                   other=other_data,
                                   published=pub_date,
                                   loaded=datetime.now())

                self._find(doc)

                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

            try:
                next_pg_btn = self.driver.find_element(By.XPATH, '//a[@class = \'next\']')
                self.driver.execute_script('arguments[0].click()', next_pg_btn)
                time.sleep(3)
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.index_group')))
            except:
                self.logger.debug('No NEXT button')
                break
        # ---
        # ========================================
        ...
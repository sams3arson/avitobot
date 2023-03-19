from dataclasses import dataclass
from typing import Literal 
from bs4 import BeautifulSoup as BSoup
from time import sleep
from typing import TypedDict
import settings

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import undetected_chromedriver as chromedriver

@dataclass(slots=True, frozen=True)
class Request:
    query: str
    city: str
    min_price: int
    max_price: int
    page_limit: int
    sorting: Literal[0, 1, 2, 3]


@dataclass(slots=True, frozen=True)
class Product:
    name: str
    description: str
    price: int
    avito_id: str
    url: str


@dataclass(slots=True, frozen=True)
class RequestResult:
    min_price: int
    max_price: int
    avg_price: int
    ads_count: int
    ads_list: list[Product]
    url: str


class Payload(TypedDict):
    name: str
    pmin: int
    pmax: int


class Avito:
    def __init__(self) -> None:
        self.driver = self._setup_driver()

    def _setup_driver(self) -> chromedriver.Chrome:
        driver = chromedriver.Chrome()
        return driver

    def process_request(self, request: Request) -> RequestResult:
        # в результате запроса будет:
        # мин цена, макс цена, ср цена, колво объявлений, можно список объявлений
        # (первые 20)
        base_url = self._format_url(request)
        self.driver.get(base_url)
        url = self._get_proper_url(request)
        response = self._get_avito_response(url)
        pages_amount = min(self._get_pages_amount(response),
                           settings.MAX_PAGE_LIMIT)
        if pages_amount > request.page_limit > 0:
            pages_amount = request.page_limit

        pages = [response]
        for page_number in range(2, pages_amount + 1):
            page_response = self._get_avito_response(self._add_page_url(url,
                                                                   page_number))
            if "items-extraTitle" in page_response: # ads from other cities
                response_local_only = page_response.split("items-extraTitle")[0]
                pages.append(response_local_only)
                break
            pages.append(page_response)

        products = list()
        for page in pages:
            sleep(3) # don't wanna get banned by Avito
            products.extend(self._parse_avito_response(page))
        
        prices = [prod.price for prod in products]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) // len(prices)

        return RequestResult(min_price=min_price, max_price=max_price,
                             avg_price=avg_price, ads_count=len(products),
                             ads_list=products, url=url)

    def check_city(self, city: str) -> bool:
        self.driver.get(settings.AVITO_CITY.format(city=city))
        if "Ой! Такой страницы на нашем сайте нет" in self.driver.page_source:
            return False
        return True

    def _get_avito_response(self, url: str) -> str:
        self.driver.get(url)
        return self.driver.page_source

    def _get_proper_url(self, request: Request) -> str:
        price_from = self.driver.find_element(By.CSS_SELECTOR, "input"
                                                "[data-marker='price/from']")
        wait = WebDriverWait(self.driver, timeout=5)
        wait.until(EC.element_to_be_clickable(price_from))
        if request.min_price:
            price_from.send_keys(str(request.min_price))
        if request.max_price:
            price_to = self.driver.find_element(By.CSS_SELECTOR, "input"
                                                "[data-marker='price/to']")
            price_to.send_keys(str(request.max_price))

        button = self.driver.find_element(By.CSS_SELECTOR, "button[data-marker="
                                              "'search-filters/submit-button']")
        button.click()
        return self.driver.current_url + "&localPriority=1"


    def _get_pages_amount(self, page_source: str) -> int:
        soup = BSoup(page_source, "lxml")
        pages_div = soup.find("div", {"data-marker": "pagination-button"})
        pg_buttons = pages_div.find_all("span")
        pg_numbers = [int(button.text) for button in pg_buttons if
                      button.text.strip().isdigit()]
        return pg_numbers[-1]

    def _parse_avito_response(self, page_source: str) -> list[Product]:
        soup = BSoup(page_source, "lxml")
        raw_products = soup.find_all("div", {"data-marker": "item"})

        products = [Product(
            name=product.find("h3", {"itemprop": "name"}).text.strip(),
            description=self._parse_description(product),
            price=int(product.find("meta", {"itemprop": "price"}).get("content").strip()),
            avito_id=product.find("a", {"itemprop": "url"}).get("href").split("/")[-1],
            url=settings.AVITO_BASE + product.find("a", {"itemprop": "url"}).get("href")
            ) for product in raw_products]

        return products

    def _parse_description(self, product) -> str:
        description = product.find("meta", {"itemprop": "description"})
        if description:
            return description.get("content").strip()
        return ""


    def _format_url(self, request: Request) -> str:
        return settings.AVITO_URL.format(
                city=request.city,
                query=request.query.strip().replace(" ", "+"),
                sorting=request.sorting
                )

    def _add_page_url(self, page_link: str, page_number: int) -> str:
        return page_link + "&p=" + str(page_number)


if __name__ == "__main__":
    req = Request(query="rx 580", city="ufa", min_price=2000, max_price=10000, 
                  page_limit=0, sorting=0)
    avito = Avito()
    print(avito._format_url(req))
    #with open("example.html", "r") as f:
    #    page = f.read()


from dataclasses import dataclass
from typing import Literal 
from bs4 import BeautifulSoup as BSoup
from typing import TypedDict
from avitobot import settings
import asyncio

import pyppeteer
from pyppeteer.browser import Browser
from pyppeteer.page import Page


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


class Avito:
    async def setup_browser(self) -> None:
        self.browser = await pyppeteer.launch()

    async def close_browser(self) -> None:
        await self.browser.close()

    async def process_request(self, request: Request) -> RequestResult:
        # в результате запроса будет:
        # мин цена, макс цена, ср цена, колво объявлений, можно список объявлений
        # (первые 20)
        page = await self.browser.newPage()
        base_url = self._format_url(request)
        await page.goto(base_url)
        url = await self._get_proper_url(page, request)
        raw_response = await self._get_avito_response(page, url)
        is_extra, response = self._cut_extra_response(raw_response)
        if not is_extra:
            pages_amount = min(self._get_pages_amount(response),
                               settings.MAX_PAGE_LIMIT)
            if pages_amount > request.page_limit > 0:
                pages_amount = request.page_limit
        else:
            pages_amount = 1

        pages = [response]
        for page_number in range(2, pages_amount + 1):
            page_response = await self._get_avito_response(page, 
                                        self._add_page_url(url, page_number))
            is_extra, page_response = self._cut_extra_response(page_response)
            if is_extra:
                pages.append(page_response)
                break

            pages.append(page_response)
            await asyncio.sleep(2) # don't wanna get banned by avito

        products = list()
        for avito_page in pages:
            products.extend(self._parse_avito_response(avito_page))
        
        prices = [prod.price for prod in products]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) // len(prices)

        await page.close()
        return RequestResult(min_price=min_price, max_price=max_price,
                             avg_price=avg_price, ads_count=len(products),
                             ads_list=products, url=url)

    async def check_city(self, city: str) -> bool:
        page = await self.browser.newPage()
        await page.goto(settings.AVITO_CITY.format(city=city))
        page_source = await page.content()
        await page.close()
        if "Ой! Такой страницы на нашем сайте нет" in page_source:
            return False
        return True

    async def _get_avito_response(self, page: Page, url: str) -> str:
        await page.goto(url)
        return await page.content()

    def _cut_extra_response(self, page_source: str) -> tuple[bool, str]:
        if "items-extraTitle" in page_source:
            return True, page_source.split("items-extraTitle")[0]
        return False, page_source

    async def _get_proper_url(self, page: Page, request: Request) -> str:
        await page.waitForSelector("input[data-marker='price/from']")
        if request.min_price:
            await page.type("input[data-marker='price/from']", 
                            str(request.min_price))
        if request.max_price:
            await page.type("input[data-marker='price/to']", 
                            str(request.max_price))

        await asyncio.gather(
                page.waitForNavigation(),
                page.click("button[data-marker='search-filters/submit-button']"),
                )
        return page.url + "&localPriority=1"

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


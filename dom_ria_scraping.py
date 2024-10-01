import asyncio
import csv
from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://dom.ria.com/uk"
URL = urljoin(BASE_URL, "/prodazha-kvartir/")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.3",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class Flat:
    city: str
    price: str
    price_for_square_metre: str
    total_area: str
    floor: str
    num_of_floors: int
    num_of_rooms: int
    address: str
    region: Optional[str] = None
    subway: Optional[str] = None
    apartment_complex: Optional[str] = None


def parse_single_flat(detailed_page_soup: BeautifulSoup, city: str, region: str, subway: str, address: str) -> Flat:
    description_for_totals_areas = detailed_page_soup.select("div.size18")
    description_for_floor = detailed_page_soup.select(
        ".bg_blue ul.main-list div.size18"
    )
    description_for_room = detailed_page_soup.select(
        ".bg_blue ul.main-list div.size18 span"
    )
    total_area, floor, num_of_floors, num_of_rooms = str(), str(), str(), str()

    for element in description_for_totals_areas:
        if "Загальна площа" in element.text:
            total_area = " ".join(element.text.strip().split()[2:4])
            break

    for element in description_for_floor:
        if "поверх" in element.text:
            floor = element.text.strip().split()[0]
            num_of_floors = int(element.text.strip().split()[-1])
            break
    for element in description_for_room:
        if "кімнат" in element.text:
            num_of_rooms = int(element.text.strip().split()[0])
            break

    try:
        apartment_complex = detailed_page_soup.select_one(
            "div.blockInfoNewbuild > div"
        ).text.strip()
        apartment_complex = (
            apartment_complex if apartment_complex.startswith("ЖК") else None
        )
    except AttributeError:
        apartment_complex = None

    flat = Flat(
        city=city,
        region=region,
        address=address,
        price=detailed_page_soup.select_one("b.size30").text.strip(),
        price_for_square_metre=" ".join(
            detailed_page_soup.select_one("div.p-rel > span.i-block")
            .text.strip()
            .split()[1:-2]
        ),
        total_area=total_area,
        floor=floor,
        num_of_floors=num_of_floors,
        num_of_rooms=num_of_rooms,
        subway=subway,
        apartment_complex=apartment_complex,
    )

    return flat


async def get_num_pages(client: httpx.AsyncClient) -> int:
    page = await client.get(URL)
    pages_soup = BeautifulSoup(page.content, "html.parser")

    if not pages_soup.select(".pagerMobileScroll"):
        return 1

    return int(pages_soup.select(".pagerMobileScroll > a")[-1].text)


def get_detailed_links_from_one_page(flat_soup: BeautifulSoup) -> List[str]:
    detailed_flat_pages_part_links = flat_soup.select(".realty-link")

    return [urljoin(BASE_URL, link["href"]) for link in detailed_flat_pages_part_links]


async def get_response_with_retry(
    client: httpx.AsyncClient, url: str, retries: int = 6, params: dict = None
) -> httpx.Response:
    for attempt in range(retries):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            print(f"HTTP error on attempt {attempt + 1}: {e}")
        except httpx.RequestError as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
        await asyncio.sleep(2**attempt)
    return httpx.Response(status_code=503)


async def get_one_page_flats(flat_soup: BeautifulSoup, extra_info: dict) -> List[Flat]:
    detailed_flat_page_full_links = get_detailed_links_from_one_page(flat_soup)
    one_page_flats = []
    counter = 0

    async with httpx.AsyncClient(
        timeout=10, headers=headers, follow_redirects=True
    ) as client:
        tasks = [
            get_response_with_retry(client, link)
            for link in detailed_flat_page_full_links
        ]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                one_page_flats.append(
                    parse_single_flat(
                        soup,
                        extra_info["city"][counter],
                        extra_info["region"][counter],
                        extra_info["subway"][counter],
                        extra_info["address"][counter]
                    )
                )
                counter += 1
            else:
                continue

    return one_page_flats


def get_extra_info(soup: BeautifulSoup) -> dict:
    extra_info = dict()
    city_list, region_list, subway_list, address_list = list(), list(), list(), list()
    flats = soup.select("div.wrap_desc")

    for flat in flats:
        city_list.append(flat.select_one('a[data-level="city"]').text.strip())
        address_list.append(flat.select_one("div.tit > a.bold").text.strip())
        try:
            region_list.append(flat.select('a[data-level="area"]')[-1].text.strip())
        except IndexError:
            region_list.append(None)
        if flat.select('a[data-level="metro"]'):
            subway_list.append(flat.select_one('a[data-level="metro"]').text.strip())
        else:
            subway_list.append(None)

    extra_info["city"] = city_list
    extra_info["region"] = region_list
    extra_info["subway"] = subway_list
    extra_info["address"] = address_list

    return extra_info


def write_titles_for_flats_csv() -> None:
    with open("test.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "city",
                "region",
                "address",
                "price",
                "price_for_square_metre",
                "total_area",
                "floor",
                "num_of_floors",
                "num_of_rooms",
                "subway",
                "apartment_complex",
            ]
        )


def write_one_page_flats_to_csv(flats: List[Flat]) -> None:
    with open("test.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for flat in flats:
            writer.writerow(
                [
                    flat.city,
                    flat.region,
                    flat.address,
                    flat.price,
                    flat.price_for_square_metre,
                    flat.total_area,
                    flat.floor,
                    flat.num_of_floors,
                    flat.num_of_rooms,
                    flat.subway,
                    flat.apartment_complex,
                ]
            )


async def main():
    start_page = 1
    end_page = 3
    if start_page == 1:
        write_titles_for_flats_csv()
    await write_all_flats_to_csv(start_page, end_page)
    print("Data is written!")


if __name__ == "__main__":
    asyncio.run(main())

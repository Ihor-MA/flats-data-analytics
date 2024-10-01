import asyncio
import csv
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

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


async def main():
    start_page = 1
    end_page = 3
    if start_page == 1:
        write_titles_for_flats_csv()
    await write_all_flats_to_csv(start_page, end_page)
    print("Data is written!")


if __name__ == "__main__":
    asyncio.run(main())

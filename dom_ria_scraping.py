import asyncio
import csv
from dataclasses import dataclass
from typing import Optional


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

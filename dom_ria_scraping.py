import asyncio


async def main():
    start_page = 1
    end_page = 3
    if start_page == 1:
        write_titles_for_flats_csv()
    await write_all_flats_to_csv(start_page, end_page)
    print("Data is written!")


if __name__ == "__main__":
    asyncio.run(main())

import time

import requests
from bs4 import BeautifulSoup
import os
import re

pagesAvailable = 212


def fetch_sticker_images(url, pages, output_folder="Complete collection"):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    total_downloaded_count = 0
    total_skipped_count = 0

    for page_num in range(1, pages + 1):
        time.sleep(2)
        page_url = f"{url}?page={page_num}"
        print(f"\rPage: {page_num}/{pages}, Downloaded: {total_downloaded_count}, Skipped: {total_skipped_count}", end='', flush=True)

        # Fetch the page content
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            sticker_divs = soup.find_all("div", class_="w-full sm:w-1/2 md:w-1/2 lg:w-1/3 xl:w-1/3 2xl:w-1/4 p-4 flex-none")

            downloaded_count = 0
            skipped_count = 0

            # Loop through sticker divs to find image URLs and save them
            for index, sticker_div in enumerate(sticker_divs, 1):
                image_url = sticker_div.find("img")["src"]
                item_name_span = sticker_div.find("span", class_="block text-lg leading-7 truncate")
                item_name = item_name_span.text.strip()
                collection_span = sticker_div.find("span", class_="block text-gray-400 text-sm truncate")
                collection_name = collection_span.text.strip()
                # Remove special characters from the sticker name and collection name
                item_name = re.sub(r'[^\w\s]', '', item_name)
                collection_name = re.sub(r'[^\w\s]', '', collection_name)
                image_name = f"{collection_name} - {item_name}.png"
                collection_folder = os.path.join(output_folder, collection_name)
                if not os.path.exists(collection_folder):
                    os.makedirs(collection_folder)
                image_path = os.path.join(collection_folder, image_name)

                # Check if image already exists and is not corrupted
                if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                    skipped_count += 1
                    total_skipped_count += 1
                    print(f"\rPage: {page_num}/{pages}, Downloaded: {total_downloaded_count}, Skipped: {total_skipped_count}, {collection_name} - {item_name}                                        ", end='', flush=True)
                    continue

                # Download the image
                with open(image_path, "wb") as f:
                    image_content = requests.get(image_url, headers=headers).content
                    if len(image_content) > 0:
                        f.write(image_content)
                        downloaded_count += 1
                        total_downloaded_count += 1
                        print(f"\rPage: {page_num}/{pages}, Downloaded: {total_downloaded_count}, Skipped: {total_skipped_count}, {collection_name} - {item_name}                                        ", end='', flush=True)
                    else:
                        print(f"\rFailed to download {image_name}, skipping", end='', flush=True)

        else:
            print(f"\rFailed to fetch page {page_num}. Status code: {response.status_code}")

    print("\nAll images downloaded.")


if __name__ == "__main__":
    base_url = "https://csgoskins.gg/"
    fetch_sticker_images(base_url, pagesAvailable)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd\
import time

def scrape_skincare_products(
    url="https://www.buymebeauty.com/skin-care/?mode=4&sort=alphaasc&limit=40",
    output_file="BuyMeBeauty_Skincare_Scrape.xlsx",
    product_limit=50,
    overfetch_limit=70,
    scroll_times=5,
    scroll_pause=2,
    chromedriver_path="C:/Users/Olajide.shittu/ds_task_1ab/venv/chromedriver-win64/chromedriver-win64/chromedriver.exe",
    chrome_binary_path="C:/Program Files/Google/Chrome/Application/chrome.exe"
):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    if chrome_binary_path:
        options.binary_location = chrome_binary_path
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    product_links = []
    page_num = 1
    while len(product_links) < overfetch_limit:
        page_url = url + f"&page={page_num}" if page_num > 1 else url
        driver.get(page_url)
        for _ in range(scroll_times):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
        product_cards = driver.find_elements(By.CSS_SELECTOR, ".card")
        for card in product_cards:
            try:
                link = card.find_element(By.CSS_SELECTOR, ".card-title a").get_attribute("href")
                if link and link not in product_links:
                    product_links.append(link)
                if len(product_links) >= overfetch_limit:
                    break
            except Exception as e:
                print(f"Error getting product link: {e}")
        if len(product_cards) == 0:
            break  # No more products/pages
        page_num += 1

    results = []
    for link in product_links:
        if len(results) >= product_limit:
            break
        try:
            driver.get(link)
            time.sleep(1)
            title = driver.find_element(By.CSS_SELECTOR, ".productView-title").text
            try:
                brand = driver.find_element(By.CSS_SELECTOR, ".productView-brand a").text
            except:
                brand = "N/A"
            barcode = "N/A"
            try:
                dt_tags = driver.find_elements(By.CSS_SELECTOR, "dt")
                for dt in dt_tags:
                    if "UPC" in dt.text:
                        barcode = dt.find_element(By.XPATH, "following-sibling::dd[1]").text
                        break
            except:
                pass
            try:
                main_image = driver.find_element(By.CSS_SELECTOR, ".productView-image").get_attribute("src")
            except:
                main_image = "N/A"
            all_images = []
            try:
                thumbs = driver.find_elements(By.CSS_SELECTOR, ".productView-thumbnail-link img")
                for img in thumbs:
                    all_images.append(img.get_attribute("src"))
            except:
                pass
            all_images_str = ", ".join(all_images) if all_images else main_image

            results.append({
                "Barcode": barcode,
                "Image Title": title,
                "Brand": brand,
                "Primary Image Link": main_image,
                "All Product Images": all_images_str,
                "Product Reference": link
            })
        except Exception as e:
            print(f"Error scraping product {link}: {e}")

    driver.quit()
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
    print(f"Scrape complete! File saved as {output_file}")

if __name__ == "__main__":
    scrape_skincare_products()

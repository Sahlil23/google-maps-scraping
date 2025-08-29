from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import pandas as pd
import re

# Setup driver
service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.google.com/maps/place/Pantai+BATAKAN+BARU/@-4.0243589,114.6548869,31532m/data=!3m1!1e3!4m18!1m9!3m8!1s0x2de71d9c5595170b:0x6bc953d389b8bd89!2sPantai+BATAKAN+BARU!8m2!3d-4.0842654!4d114.6287747!9m1!1b1!16s%2Fg%2F11kx67zhsr!3m7!1s0x2de71d9c5595170b:0x6bc953d389b8bd89!8m2!3d-4.0842654!4d114.6287747!9m1!1b1!16s%2Fg%2F11kx67zhsr?entry=ttu&g_ep=EgoyMDI1MDgxOS4wIKXMDSoASAFQAw%3D%3D"

try:
    driver.get(url)
    time.sleep(5)

    
    print("Mencari tab Reviews...")
    try:
        review_tab_selectors = [
            "//button[@data-value='Reviews']",
            "//button[contains(text(), 'Reviews')]",
            "//button[contains(text(), 'Ulasan')]",
            "//div[contains(@data-value, 'Reviews')]//button"
        ]
        
        clicked = False
        for selector in review_tab_selectors:
            try:
                review_tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                driver.execute_script("arguments[0].click();", review_tab)
                print("Berhasil klik tab Reviews")
                time.sleep(3)
                clicked = True
                break
            except:
                continue
                
        if not clicked:
            print("Tab Reviews tidak ditemukan, melanjutkan...")
            
    except Exception as e:
        print(f"Error saat mencari tab reviews: {e}")

    # Scroll untuk memuat ulasan
    print("Memuat ulasan dengan scroll...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(30):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        print(f"Scroll ke-{i+1}")

    # Cari dan klik tombol "Lainnya" untuk expand ulasan - PERBAIKAN SELECTOR
    print("Mengexpand ulasan panjang...")
    try:
        # Selector yang lebih akurat berdasarkan gambar
        more_button_selectors = [
            "//button[contains(@class, 'w8nwRe') and contains(text(), 'Lainnya')]",
            "//button[contains(@class, 'w8nwRe') and contains(text(), 'More')]",
            "//button[contains(@aria-label, 'See more')]",
            "//button[contains(@aria-label, 'Lihat selengkapnya')]",
            "//button[contains(text(), 'Lainnya')]",
            "//button[contains(text(), 'More')]"
        ]
        
        total_expanded = 0
        for selector in more_button_selectors:
            try:
                more_buttons = driver.find_elements(By.XPATH, selector)
                print(f"Selector {selector}: ditemukan {len(more_buttons)} tombol")
                
                for i, button in enumerate(more_buttons):
                    try:
                        # Scroll ke tombol terlebih dahulu
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # Klik tombol
                        driver.execute_script("arguments[0].click();", button)
                        total_expanded += 1
                        print(f"Berhasil expand ulasan ke-{total_expanded}")
                        time.sleep(0.3)
                    except Exception as e:
                        continue
                        
            except Exception as e:
                continue
                
        print(f"Total ulasan yang di-expand: {total_expanded}")
        
    except Exception as e:
        print(f"Error saat expand ulasan: {e}")

    # Tunggu sebentar setelah expand
    time.sleep(2)

    # Ambil source code halaman
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Cari container ulasan dengan berbagai selector
    review_containers = []
    
    selectors = [
        'div[data-review-id]',
        'div.jftiEf',
        'div.fontBodyMedium',
        'div[jsaction*="review"]'
    ]
    
    for selector in selectors:
        containers = soup.select(selector)
        if containers:
            review_containers = containers
            print(f"Menggunakan selector: {selector}, ditemukan {len(containers)} ulasan")
            break

    # Extract data
    data_list = []
    seen_reviews = set()

    for review in review_containers:
        try:
            # Ekstraksi nama
            nama = 'Anonim'
            name_selectors = ['div.d4r55', 'div.WNxzHc', 'span.X43Kjb']
            for sel in name_selectors:
                name_elem = review.select_one(sel)
                if name_elem:
                    nama = name_elem.get_text(strip=True)
                    break

            # Ekstraksi teks ulasan - PERBAIKAN UNTUK HANDLE ENTER
            teks = ''
            text_selectors = [
                'span.wiI7pd',
                'span[jsaction*="expand"]',
                'div.MyEned span',
                'span.review-full-text'
            ]
            for sel in text_selectors:
                text_elem = review.select_one(sel)
                if text_elem:
                    # Ambil teks dan replace newline dengan spasi
                    teks = text_elem.get_text(separator=' ', strip=True)
                    # Bersihkan multiple spasi
                    teks = re.sub(r'\s+', ' ', teks)
                    break

            # Ekstraksi rating
            rating = 'Tidak Tersedia'
            rating_selectors = [
                'span[aria-label*="star"]',
                'span[aria-label*="Star"]',
                'span[aria-label*="bintang"]',
                'div[aria-label*="star"]',
                'span.kvMYJc'
            ]
            for sel in rating_selectors:
                rating_elem = review.select_one(sel)
                if rating_elem and rating_elem.get('aria-label'):
                    rating = rating_elem['aria-label']
                    break

            # Hindari duplikat dan data kosong
            if nama and teks:
                review_id = f"{nama}_{hash(teks)}_{rating}"
                if review_id not in seen_reviews:
                    seen_reviews.add(review_id)
                    data_list.append([nama, teks, rating])

        except Exception as e:
            continue

    # Simpan ke CSV dengan quoting untuk handle comma dan newline
    if data_list:
        df = pd.DataFrame(data_list, columns=['Nama', 'Ulasan', 'Rating'])
        df.to_csv('ulasan_batakan.csv', index=False, encoding='utf-8', quoting=1)  # quoting=1 untuk quote semua field
        print(f"Berhasil mengambil {len(df)} ulasan")
        print("Data disimpan ke ulasan_batakan.csv")
    else:
        print("Tidak ada data ulasan yang berhasil diambil")

except Exception as e:
    print(f"Error: {e}")

finally:
    driver.quit()
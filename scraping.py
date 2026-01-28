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

service = Service()
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.google.com/maps/place/Pantai+BATAKAN+BARU/@-4.0243589,114.6548869,31532m/data=!3m1!1e3!4m18!1m9!3m8!1s0x2de71d9c5595170b:0x6bc953d389b8bd89!2sPantai+BATAKAN+BARU!8m2!3d-4.0842654!4d114.6287747!9m1!1b1!16s%2Fg%2F11kx67zhsr!3m7!1s0x2de71d9c5595170b:0x6bc953d389b8bd89!8m2!3d-4.0842654!4d114.6287747!9m1!1b1!16s%2Fg%2F11kx67zhsr?entry=ttu&g_ep=EgoyMDI1MDgxOS4wIKXMDSoASAFQAw%3D%3D"

try:
    driver.get(url)
    time.sleep(5)  # Tunggu halaman load
    
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

    # PERBAIKAN: Scroll otomatis di container ulasan
    print("Memuat SEMUA ulasan dengan scroll otomatis...")
    
    # Cari container ulasan yang bisa di-scroll
    scrollable_container = None
    container_selectors = [
        "div.m6QErb.DxyBCb.kA9KIf.dS8AEf",  # Container utama Google Maps
        "div[role='main']",
        "div.m6QErb",
        "div.section-scrollbox"
    ]
    
    for selector in container_selectors:
        try:
            container = driver.find_element(By.CSS_SELECTOR, selector)
            if container:
                scrollable_container = container
                print(f"Container ditemukan: {selector}")
                break
        except:
            continue
    
    if scrollable_container:
        print("Mulai scroll otomatis untuk memuat semua ulasan...")
        last_height = 0
        no_change_count = 0
        scroll_count = 0
        max_no_change = 30  # Berhenti jika 3x berturut-turut tidak ada perubahan
        
        while no_change_count < max_no_change:
            # Scroll ke bawah
            driver.execute_script(
                "arguments[0].scrollTo(0, arguments[0].scrollHeight)", 
                scrollable_container
            )
            scroll_count += 1
            print(f"Scroll #{scroll_count}...", end=" ")
            
            # Tunggu loading
            time.sleep(2)
            
            # Cek tinggi baru
            new_height = driver.execute_script(
                "return arguments[0].scrollHeight", 
                scrollable_container
            )
            
            if new_height == last_height:
                no_change_count += 1
                print(f"Tidak ada perubahan ({no_change_count}/{max_no_change})")
            else:
                no_change_count = 0
                print(f"Memuat konten baru (Height: {new_height})")
                last_height = new_height
        
        print(f"\nSelesai scroll. Total {scroll_count} kali scroll.")
        
    else:
        print("Container tidak ditemukan, menggunakan scroll halaman")
        for i in range(50):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

    # Tunggu konten final dimuat
    time.sleep(3)

    # Expand semua tombol "Lainnya"
    print("\nMengexpand ulasan panjang...")
    more_button_selectors = [
        "//button[@class='w8nwRe kyuRq' and @jsaction='pane.reviewChart.moreReviews']",
        "//button[contains(@class, 'w8nwRe')]",
        "//button[@aria-label='Lihat ulasan lengkap']",
        "//button[@aria-label='See full review']"
    ]
    
    total_expanded = 0
    for selector in more_button_selectors:
        try:
            buttons = driver.find_elements(By.XPATH, selector)
            for btn in buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", btn)
                    total_expanded += 1
                except:
                    continue
        except:
            continue
    
    print(f"Total {total_expanded} ulasan di-expand")
    time.sleep(2)

    # Scraping ulasan
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    review_containers = []
    selectors = [
        'div.jftiEf.fontBodyMedium',
        'div[data-review-id]',
        'div.jftiEf'
    ]
    
    for selector in selectors:
        containers = soup.select(selector)
        if containers:
            review_containers = containers
            print(f"\nDitemukan {len(containers)} ulasan dengan selector: {selector}")
            break

    # Extract data
    data_list = []
    seen_reviews = set()

    for review in review_containers:
        try:
            teks = ''
            text_selectors = [
                'span.wiI7pd',
                'div.MyEned span',
                'span[class*="review"]'
            ]
            
            for sel in text_selectors:
                text_elem = review.select_one(sel)
                if text_elem:
                    teks = text_elem.get_text(separator=' ', strip=True)
                    teks = re.sub(r'\s+', ' ', teks)
                    break
            
            if teks and len(teks) > 5:  # Filter ulasan minimal 5 karakter
                review_id = hash(teks)
                if review_id not in seen_reviews:
                    seen_reviews.add(review_id)
                    data_list.append([teks])

        except Exception as e:
            continue

    # Simpan ke CSV
    if data_list:
        df = pd.DataFrame(data_list, columns=['Ulasan'])
        df.to_csv('ulasan_batakan.csv', index=False, encoding='utf-8-sig')
        print(f"\n✓ Berhasil mengambil {len(df)} ulasan unik")
        print("✓ Data disimpan ke ulasan_batakan.csv")
    else:
        print("\n✗ Tidak ada data ulasan yang berhasil diambil")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
# Scraping Ulasan Google Maps (Pantai Batakan Baru)

Projek ini mengambil (men-scrape) daftar ulasan (nama, teks ulasan, rating) dari halaman Google Maps sebuah lokasi menggunakan Selenium + BeautifulSoup dan menyimpannya ke file CSV.

> Catatan Penting:
> - Gunakan hanya untuk pembelajaran.
> - Patuh pada Terms of Service Google. Jangan mengirim permintaan berlebihan.
> - Struktur HTML Google Maps sering berubah; selector perlu disesuaikan secara berkala.

## Fitur
- Membuka halaman lokasi Google Maps.
- Menavigasi ke tab Reviews/Ulasan.
- Melakukan scroll berkali‑kali untuk memuat lebih banyak ulasan.
- Mencari dan mengklik tombol “Lainnya / More” agar teks ulasan penuh muncul.
- Mengekstrak nama, teks ulasan (dibersihkan dari newline berlebih), dan rating.
- Menyimpan hasil ke `ulasan_batakan.csv` (UTF‑8).

## Kebutuhan
- Python 3.9+ (disarankan)
- Google Chrome versi terbaru
- ChromeDriver yang cocok dengan versi Chrome

## Instalasi
1. Clone / salin folder proyek.
2. (Opsional) Buat virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. Instal dependensi:
   ```bash
   pip install --upgrade pip
   pip install selenium beautifulsoup4 pandas lxml
   ```
4. Pastikan ChromeDriver tersedia:
   - Unduh manual: https://chromedriver.chromium.org/downloads (sesuaikan versi Chrome) lalu letakkan dalam PATH
   - Atau gunakan webdriver-manager (opsional):
     ```bash
     pip install webdriver-manager
     ```

## Konfigurasi (Jika Pakai webdriver-manager)
Contoh inisialisasi driver:
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
```

## Menjalankan
```bash
python screabing.py
```
Output:
- Proses akan menampilkan log (scroll, klik tombol “Lainnya”).
- Hasil disimpan di `ulasan_batakan.csv`.

## Struktur Output CSV
Kolom:
1. Nama
2. Ulasan (teks penuh yang sudah di-expand)
3. Rating (contoh: “5 bintang”)

## Penyesuaian Selector
Jika hasil kosong / sedikit:
- Perbarui daftar XPATH / CSS untuk:
  - Tab Reviews
  - Tombol “Lainnya” (class bisa berubah, contoh: `w8nwRe`)
  - Kontainer ulasan (`div[data-review-id]`, `div.jftiEf`, dll.)
- Tambah jumlah scroll atau waktu tunggu.

## Troubleshooting
| Masalah | Solusi Singkat |
|---------|----------------|
| Hanya sedikit ulasan | Tambah loop scroll, periksa selector kontainer |
| Ulasan terpotong | Pastikan loop klik tombol “Lainnya” berjalan |
| Rating “Tidak Tersedia” | Cek ulang span dengan atribut `aria-label` di DevTools |
| Error versi driver | Samakan versi Chrome & ChromeDriver / pakai webdriver-manager |
| Teks pecah baris di CSV | Gunakan pembersihan newline (`get_text(separator=' ', strip=True)`) & quoting CSV |

## Etika & Legal
- Batasi frekuensi (sleep antar aksi).
- Jangan distribusikan data tanpa izin.
- Jika tersedia API resmi, gunakan API.

## Lisensi
Hanya untuk penggunaan internal / edukasi (sesuaikan kebutuhan Anda).


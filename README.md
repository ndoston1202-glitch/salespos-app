# 🍽️ SalesPOS — Kafe/Restoran boshqaruv tizimi

Yengil POS tizimi. **Faqat Python kerak** — Node.js, npm yo'q!

## 🚀 Ishga tushirish

| Tugma | Vazifasi |
|-------|----------|
| **ISHGA_TUSHIR.bat** | Dasturni yoqadi, brauzer ochiladi |
| **YANGILASH.bat** | GitHub dan yangi versiyani oladi |
| **TOXTAT.bat** | Dasturni to'xtatadi |

### Birinchi marta
1. **Python** o'rnating: https://www.python.org/downloads/ (PATH ni belgilang)
2. **ISHGA_TUSHIR.bat** ga ikki marta bosing

### Kirish
- Manzil: `http://localhost:8000`
- Login: **admin** · Parol: **admin123**

## ✨ Imkoniyatlar
- 📊 Boshqaruv paneli (tushum, statistika)
- 🪑 Stollar — bosilganda menyu ochiladi
- 🧾 3 xil buyurtma: Stol / Olib ketish / Masofadan
- 🖨️ Har taomga printer (oshxona/salat) tayinlash
- 👨‍🍳 Oshxona paneli — taomlar printer bo'yicha
- 💰 Kassa (naqd/karta/Payme/Click)
- 🍽️ Menyu, kategoriya, tannarx va foyda

## 🛠️ Texnologiya
- **Backend:** Django (`server.py` — bitta fayl)
- **Frontend:** Vanilla JS + Tailwind CDN (build yo'q)
- **Baza:** SQLite

## 📁 Struktura
```
salespos/
├── server.py          # Butun backend
├── index.html         # Frontend (login + layout)
├── static/app.js      # Ilova logikasi
├── requirements.txt
├── ISHGA_TUSHIR.bat
├── YANGILASH.bat
└── TOXTAT.bat
```

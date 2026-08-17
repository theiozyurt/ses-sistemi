# Beyaz Gürültü Sistemi

Tkinter tabanlı beyaz gürültü oynatıcı. Süre, ses çıkış cihazı,
normal ses seviyesi ve dB tabanlı yazılım yükseltici içerir.

## Windows 8 Kullanımı

Son kullanici Windows 8 / 8.1 tarafinda sadece tek dosyayi acar:

```text
SesSistemi.exe
```

Python veya ek paket kurulumu gerekmez. `.exe` dosyasi build makinesinde
uretilir ve `dist\SesSistemi.exe` olarak cikar.

## Windows Tek Dosya EXE Uretme

Build almak icin Windows 8 / 8.1 uyumlu bir makinede Python 3.8.x 64-bit
kurulu olmalidir. Ardindan:

```bat
build_windows.bat
```

Script sanal ortam olusturur, bagimliliklari kurar ve tek dosya exe uretir:

```text
dist\SesSistemi.exe
```

## Kurulum

Windows 8 / 8.1 hedefi icin Python 3.8.x 64-bit kullanin. Daha yeni
Python ve NumPy surumleri eski Windows surumlerinde calismayabilir.

Windows:

```bat
py -3.8 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Çalıştırma

Windows:

```bat
.venv\Scripts\python main.py
```

macOS / Linux:

```bash
.venv/bin/python main.py
```

## Kalibrasyon

Uygulamadaki dB kalibrasyonu üç ölçümle çalışır:

- Hoparlör yanı: Hoparlörün hemen yanında ölçülen mevcut seviye.
- Uzak nokta: Dinlenmesi gereken noktada ölçülen mevcut seviye.
- Hedef uzak: Dinlenmesi gereken noktada hedeflenen seviye.

Örnek: hoparlör yanında 75 dB, uzak noktada 60 dB, hedef uzak seviye
80 dB ise sistem yakın hedefi 95 dB ve gereken yazılım artışını +20 dB
olarak hesaplar.

Yazılım yükseltici +24 dB ile sınırlıdır ve çıkışta soft limiter kullanır.
Bu sınır hoparlörün fiziksel kapasitesini artırmaz; hoparlör veya amfi
yetersizse daha yüksek dB için donanım gerekir.

Uygulamada dB artisi "Ses Yükseltici" alanindaki slider ile ayarlanir.
"Hesaplanan Yükseltmeyi Uygula" butonu, yukaridaki olcumlardan gereken
dB artis miktarini otomatik uygular.

## Güvenlik

Yüksek ses seviyeleri uzun kullanımda işitme riski oluşturabilir. dB
seviyesini ölçüm cihazıyla kademeli yükselterek doğrulayın.

# Beyaz Gürültü Sistemi

Tkinter tabanlı beyaz gürültü oynatıcı. Süre, ses çıkış cihazı,
normal ses seviyesi ve dB tabanlı yazılım yükseltici içerir.

## Kurulum

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Çalıştırma

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

## Güvenlik

Yüksek ses seviyeleri uzun kullanımda işitme riski oluşturabilir. dB
seviyesini ölçüm cihazıyla kademeli yükselterek doğrulayın.

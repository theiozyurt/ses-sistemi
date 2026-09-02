#!/bin/bash
# macOS icin tek dosya executable uretir (dist/SesSistemi).
#
# Var olan .venv kullanilir (numpy/sounddevice zaten kurulu olmali); yoksa
# sistem python3 ile yeni bir sanal ortam olusturulur. PyInstaller ve
# bagimliliklari internet gerektirmeden, bu depodaki
# vendor/mac_wheels/ altindaki wheel dosyalarindan kurulur.
#
# Kullanim:
#   ./build_mac.sh

set -e
cd "$(dirname "$0")"

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Mevcut .venv bulunamadi, yeni bir sanal ortam olusturuluyor..."
    python3 -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

if [ ! -d "vendor/mac_wheels" ]; then
    echo "HATA: vendor/mac_wheels dizini bulunamadi."
    echo "PyInstaller'i internetten kurmak icin: $PIP install pyinstaller"
    exit 1
fi

echo "PyInstaller, vendor/mac_wheels icindeki wheel dosyalarindan (internet gerekmeden) kuruluyor..."
"$PIP" install --no-index --find-links=vendor/mac_wheels pyinstaller

echo "numpy/sounddevice kurulu mu kontrol ediliyor..."
if ! "$PYTHON" -c "import numpy, sounddevice" 2>/dev/null; then
    echo "HATA: .venv icinde numpy/sounddevice bulunamadi."
    echo "macOS icin uygun surumleri once kurun, ornegin:"
    echo "  $PIP install numpy sounddevice cffi"
    exit 1
fi

echo "PyInstaller ile tek dosya build aliniyor..."
"$VENV_DIR/bin/pyinstaller" --clean ses-sistemi.spec

echo
echo "Build tamamlandi: dist/SesSistemi"
echo
echo "Not: Bu dosya imzasiz (unsigned) oldugu icin macOS Gatekeeper ilk"
echo "acilista uyari verebilir. Sag tik > Ac ile calistirin, ya da:"
echo "  xattr -d com.apple.quarantine dist/SesSistemi"

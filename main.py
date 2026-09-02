import math
import subprocess
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import sounddevice as sd

try:
    import ctypes
except Exception:  # pragma: no cover - ctypes is stdlib, this is a safety net
    ctypes = None


SAMPLE_RATE = 44100
CHANNELS = 2
MAX_GAIN_DB = 40.0
DEFAULT_NEAR_DB = 75.0
DEFAULT_FAR_DB = 60.0
DEFAULT_CYCLE_REPEATS = 3

# Tahmini SPL hesaplarında sıfır ses seviyesini (log10(0) tanımsız) temsil
# etmek için kullanılan alt sınır. Gerçek bir ölçüm değil, sadece
# matematiksel/görüntüsel bir taban değeridir.
SILENT_FLOOR_DB = -60.0


# ---------------------------------------------------------------------
# Çeviri (i18n) sözlüğü
#
# Uygulamadaki tüm görünür metinler burada toplanıyor. Yeni bir metin
# eklenecekse hem "tr" hem "en" altına aynı anahtarla eklenmelidir.
# ---------------------------------------------------------------------

TRANSLATIONS = {
    "tr": {
        "app_title": "Beyaz Gürültü Sistemi",
        "section_duration": "Çalışma Süresi (Aralıklı çalışmada: her çalışma aşaması)",
        "label_hours": "Saat",
        "label_minutes": "Dakika",
        "label_seconds": "Saniye",
        "section_cycle": "Aralıklı Çalışma (Çalış / Dur Döngüsü)",
        "check_cycle": "Aralıklı çalıştır",
        "cycle_desc": (
            "Etkinleştirildiğinde: yukarıdaki 'Çalışma Süresi' kadar "
            "çalışır, ardından aşağıdaki 'Durma Süresi' kadar durur."
        ),
        "cycle_off_label": "Durma Süresi ve Tekrar Sayısı",
        "label_repeat": "Tekrar Sayısı",
        "cycle_default_note": (
            "Varsayılan: 1 saat çalışır, 1 saat durur; bu döngü 3 kez "
            "tekrarlanır (toplam 6 saat). Değerleri ihtiyaca göre değiştirin."
        ),
        "section_volume": "Ses Seviyesi",
        "section_db": "dB Ayarı",
        "db_warning": (
            "Yüksek dB uzun kullanımda risklidir. "
            "Ölçüm yaparak kademeli artırın."
        ),
        "label_near_ref": "Yakın Ölçüm (dB)",
        "label_far_ref": "Uzak Ölçüm (dB)",
        "estimate_near": "Yakında tahmini",
        "estimate_far": "Uzakta tahmini",
        "calibration_invalid": "Kalibrasyon için sayısal dB girin.",
        "section_output": "Ses Çıkışı",
        "btn_refresh_devices": "Ses Çıkışlarını Yenile",
        "label_status": "Durum:",
        "label_remaining": "Kalan Süre (bu aşama):",
        "label_total_remaining": "Toplam Kalan (program):",
        "btn_start": "BAŞLAT",
        "btn_pause": "DURAKLAT",
        "btn_resume": "DEVAM ET",
        "btn_stop": "BİTİR",
        "status_ready": "HAZIR",
        "status_running": "ÇALIŞIYOR",
        "status_resting": "DURUYOR",
        "status_paused": "DURAKLATILDI",
        "status_completed": "TAMAMLANDI",
        "status_stopped": "DURDURULDU",
        "status_error": "HATA",
        "phase_work": "Çalışma",
        "phase_rest": "Bekleme",
        "err_invalid_duration_title": "Geçersiz Süre",
        "err_invalid_work_duration_msg": "Lütfen geçerli bir çalışma süresi girin.",
        "err_invalid_rest_duration_msg": "Lütfen geçerli bir durma süresi girin.",
        "err_invalid_repeat_title": "Geçersiz Tekrar Sayısı",
        "err_invalid_repeat_msg": "Lütfen 1 ile 99 arasında bir tekrar sayısı girin.",
        "err_output_title": "Ses Çıkışı",
        "err_no_output_msg": "Kullanılabilir bir ses çıkışı bulunamadı.",
        "err_select_output_msg": "Lütfen bir ses çıkışı seçin.",
        "err_audio_start_title": "Ses Başlatılamadı",
        "err_device_title": "Ses Cihazı Hatası",
        "theme_toggle_to_dark": "Koyu Mod",
        "theme_toggle_to_light": "Açık Mod",
    },
    "en": {
        "app_title": "White Noise System",
        "section_duration": "Work Duration (In interval mode: each work phase)",
        "label_hours": "Hours",
        "label_minutes": "Minutes",
        "label_seconds": "Seconds",
        "section_cycle": "Interval Mode (Work / Rest Cycle)",
        "check_cycle": "Enable interval mode",
        "cycle_desc": (
            "When enabled: runs for the 'Work Duration' above, then "
            "rests for the 'Rest Duration' below."
        ),
        "cycle_off_label": "Rest Duration and Repeat Count",
        "label_repeat": "Repeat Count",
        "cycle_default_note": (
            "Default: runs 1 hour, rests 1 hour; this cycle repeats 3 "
            "times (6 hours total). Adjust the values as needed."
        ),
        "section_volume": "Volume",
        "section_db": "dB Control",
        "db_warning": (
            "High dB levels can be risky over long use. "
            "Increase gradually and verify with a meter."
        ),
        "label_near_ref": "Nearby Measurement (dB)",
        "label_far_ref": "Distant Measurement (dB)",
        "estimate_near": "Estimated nearby",
        "estimate_far": "Estimated at distance",
        "calibration_invalid": "Enter numeric dB values for calibration.",
        "section_output": "Audio Output",
        "btn_refresh_devices": "Refresh Audio Outputs",
        "label_status": "Status:",
        "label_remaining": "Remaining (this phase):",
        "label_total_remaining": "Total Remaining (program):",
        "btn_start": "START",
        "btn_pause": "PAUSE",
        "btn_resume": "RESUME",
        "btn_stop": "STOP",
        "status_ready": "READY",
        "status_running": "RUNNING",
        "status_resting": "RESTING",
        "status_paused": "PAUSED",
        "status_completed": "COMPLETED",
        "status_stopped": "STOPPED",
        "status_error": "ERROR",
        "phase_work": "Work",
        "phase_rest": "Rest",
        "err_invalid_duration_title": "Invalid Duration",
        "err_invalid_work_duration_msg": "Please enter a valid work duration.",
        "err_invalid_rest_duration_msg": "Please enter a valid rest duration.",
        "err_invalid_repeat_title": "Invalid Repeat Count",
        "err_invalid_repeat_msg": "Please enter a repeat count between 1 and 99.",
        "err_output_title": "Audio Output",
        "err_no_output_msg": "No available audio output was found.",
        "err_select_output_msg": "Please select an audio output.",
        "err_audio_start_title": "Could Not Start Audio",
        "err_device_title": "Audio Device Error",
        "theme_toggle_to_dark": "Dark Mode",
        "theme_toggle_to_light": "Light Mode",
    },
}

# Dil seçici combobox'ında dillerin kendi adlarıyla (çevrilmeden) gösterilmesi
# standart bir kullanılabilirlik pratiğidir; bu yüzden bu eşleme dil
# bağımsızdır.
LANGUAGE_DISPLAY_NAMES = {
    "tr": "Türkçe",
    "en": "English",
}


# ---------------------------------------------------------------------
# Tema (renk token'ları)
#
# Tüm renkler burada merkezi olarak tanımlanır; widget'lar tek tek renk
# atamak yerine bu token'lara işaret eden ttk stillerini kullanır.
# ---------------------------------------------------------------------

THEMES = {
    "light": {
        "bg": "#f2f2f2",
        "fg": "#1a1a1a",
        "muted_fg": "#555555",
        "warning_fg": "#8a4b00",
        "entry_bg": "#ffffff",
        "entry_fg": "#101010",
        "select_bg": "#3a7ebf",
        "select_fg": "#ffffff",
        "button_bg": "#e3e3e3",
        "button_fg": "#1a1a1a",
        "button_active_bg": "#d0d0d0",
        "disabled_fg": "#9a9a9a",
        "trough": "#c9c9c9",
        "border": "#b5b5b5",
    },
    "dark": {
        "bg": "#202124",
        "fg": "#f1f1f1",
        "muted_fg": "#b8b8b8",
        "warning_fg": "#ffb454",
        "entry_bg": "#2d2e31",
        "entry_fg": "#f1f1f1",
        "select_bg": "#4a90d9",
        "select_fg": "#ffffff",
        "button_bg": "#3a3b3e",
        "button_fg": "#f1f1f1",
        "button_active_bg": "#4a4b4e",
        "disabled_fg": "#8a8a8a",
        "trough": "#3a3b3e",
        "border": "#4a4b4e",
    },
}


class SleepGuard:
    """
    Uygulama açık olduğu sürece işletim sisteminin otomatik uykuya
    geçmesini engeller. Kapsam, ses çalıp çalmadığından bağımsızdır:
    uygulama açıldığı andan kapanana kadar aktif kalır (aralıklı
    çalışmadaki bekleme/duraklatma süreleri dahil).

    Windows: ctypes ile WinAPI SetThreadExecutionState çağrısı (Windows
    2000'den beri var, Windows 8/8.1 dahil; ek paket gerekmez).
    macOS: sistemle birlikte gelen 'caffeinate' aracını arka planda
    çalıştırır (ek paket gerekmez).
    Diğer platformlarda (ör. Linux) kasıtlı olarak devre dışıdır.

    Herhangi bir hata durumunda sessizce (yalnızca konsola loglayarak)
    devre dışı kalır; uygulamanın geri kalanını asla etkilemez.
    """

    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001

    def __init__(self):
        self._active = False
        self._mac_process = None

    def start(self):
        if self._active:
            return

        try:
            if sys.platform.startswith("win") and ctypes is not None:
                ctypes.windll.kernel32.SetThreadExecutionState(
                    self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED
                )
                self._active = True

            elif sys.platform == "darwin":
                self._mac_process = subprocess.Popen(
                    ["caffeinate", "-i"],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                self._active = True

            # Desteklenmeyen platformlarda kasıtlı olarak hiçbir şey
            # yapılmıyor; uygulama normal şekilde çalışmaya devam eder.

        except Exception as exc:
            print("Uyku önleme başlatılamadı:", exc)
            self._active = False
            self._mac_process = None

    def stop(self):
        if not self._active:
            return

        try:
            if sys.platform.startswith("win") and ctypes is not None:
                ctypes.windll.kernel32.SetThreadExecutionState(
                    self.ES_CONTINUOUS
                )

            elif sys.platform == "darwin" and self._mac_process is not None:
                self._mac_process.terminate()

                try:
                    self._mac_process.wait(timeout=2)
                except Exception:
                    self._mac_process.kill()

        except Exception as exc:
            print("Uyku önleme kaldırılamadı:", exc)

        finally:
            self._active = False
            self._mac_process = None


class WhiteNoisePlayer:
    def __init__(self):
        self.volume = 1.0
        self.gain_db = 0.0
        self.stream = None
        self.buffer = self._create_noise_buffer()

        self.running = False
        self.paused = False
        self.device = None

        self.start_time = None
        self.pause_started = None
        self.total_paused_time = 0.0

    def set_volume(self, volume):
        try:
            value = float(volume)
        except (TypeError, ValueError):
            return

        if value != value:  # NaN kontrolü (NaN hiçbir zaman kendine eşit değildir)
            return

        self.volume = max(0.0, min(1.0, value))

    def set_gain_db(self, gain_db):
        try:
            value = float(gain_db)
        except (TypeError, ValueError):
            return

        if value != value:  # NaN kontrolü
            return

        self.gain_db = max(0.0, min(MAX_GAIN_DB, value))

    def _output_gain(self):
        return self.volume * (10 ** (self.gain_db / 20.0))

    def _create_noise_buffer(self):
        """
        Kısa bir stereo beyaz gürültü buffer'ı oluşturur.
        Daha sonra bunu gömülü WAV dosyasıyla değiştirebiliriz.
        """

        duration = 2.0
        samples = int(SAMPLE_RATE * duration)

        noise = np.random.normal(
            0.0,
            0.15,
            (samples, CHANNELS)
        ).astype(np.float32)

        # Loop noktasında (buffer sonu -> başı) sinyali kesmek yerine
        # sonu başına çapraz karıştırıyoruz (crossfade). Böylece hem klik
        # sesi engellenir hem de döngü noktasında işitilebilir bir kısılma
        # (sesin sıfıra inip tekrar yükselmesi) oluşmaz.
        crossfade_samples = int(SAMPLE_RATE * 0.02)

        fade_in = np.linspace(
            0.0,
            1.0,
            crossfade_samples
        )[:, None]

        fade_out = 1.0 - fade_in

        head = noise[:crossfade_samples].copy()
        tail = noise[-crossfade_samples:].copy()

        noise[-crossfade_samples:] = tail * fade_out + head * fade_in

        return noise

    def _callback(self, outdata, frames, time_info, status):
        if status:
            print("Audio status:", status)

        buffer_length = len(self.buffer)

        # Buffer'ın içinde nerede olduğumuzu tutmak yerine
        # callback çağrıları arasında state saklamak için attribute kullanıyoruz.
        if not hasattr(self, "_buffer_position"):
            self._buffer_position = 0

        remaining = frames
        output_position = 0

        while remaining > 0:
            available = buffer_length - self._buffer_position
            count = min(remaining, available)

            chunk = self.buffer[
                self._buffer_position:self._buffer_position + count
            ] * self._output_gain()

            # Soft limiter: yüksek gain'de sert clipping yerine sinyali
            # 1.0 sınırına yumuşak yaklaştırır. tanh() her zaman (-1, 1)
            # aralığında sonlu bir değer döndürdüğü için gain ne kadar
            # büyük olursa olsun clipping/NaN/Inf oluşmaz.
            outdata[
                output_position:output_position + count
            ] = np.tanh(chunk).astype(np.float32)

            self._buffer_position += count
            output_position += count
            remaining -= count

            if self._buffer_position >= buffer_length:
                self._buffer_position = 0

    def start(self, device=None):
        self.stop()

        self.device = device
        self._buffer_position = 0

        self.stream = sd.OutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            device=device,
            callback=self._callback,
            blocksize=1024,
        )

        self.stream.start()

        self.running = True
        self.paused = False

    def pause(self):
        if self.stream and self.running and not self.paused:
            self.stream.stop()
            self.paused = True

    def resume(self):
        if self.stream and self.running and self.paused:
            self.stream.start()
            self.paused = False

    def stop(self):
        self.running = False
        self.paused = False

        if self.stream:
            try:
                self.stream.stop()
            except Exception:
                pass

            try:
                self.stream.close()
            except Exception:
                pass

            self.stream = None

    def is_running(self):
        return self.running and not self.paused


class SoundTestApp:
    def __init__(self, root):
        self.root = root

        # ---------------------------------------------------------
        # Dil / tema durumu
        # ---------------------------------------------------------
        self.lang = "tr"
        self.theme = "light"
        self._i18n_widgets = []

        # dB tahmini için referans anlık görüntüsü: Yakın/Uzak Ölçüm
        # alanları en son ne zaman güncellendiyse, o andaki Volume/Gain
        # değerleri burada saklanır (bkz. _on_reference_measurement_changed).
        self.reference_volume = 1.0
        self.reference_gain_db = 0.0

        # Segment tabanlı olmayan (HAZIR/DURAKLATILDI/DURDURULDU/...)
        # durumları dil değişince yeniden çevirebilmek için son basit
        # durumun çeviri anahtarını saklıyoruz.
        self._last_simple_status_key = "status_ready"

        # ---------------------------------------------------------
        # Sistem uykusunu engelleme
        #
        # Uygulama açıldığı andan (burada) kapanana (_on_close) kadar
        # aktif kalır; çalma/duraklatma durumundan bağımsızdır.
        # ---------------------------------------------------------
        self.sleep_guard = SleepGuard()
        self.sleep_guard.start()

        self.root.title(self.t("app_title"))
        self.root.resizable(False, False)

        self.player = WhiteNoisePlayer()

        # ---------------------------------------------------------
        # Program / zamanlayıcı durumu
        #
        # Uygulama "aşama" (segment) listesi üzerinden çalışır. Aralıklı
        # çalışma kapalıysa liste tek bir ÇALIŞMA aşamasından oluşur (eski
        # davranışla aynı). Açıksa liste ÇALIŞMA/DURMA aşamalarının art
        # arda tekrarından oluşur (ör. 1 saat çalış / 1 saat dur x3).
        # ---------------------------------------------------------

        self.segments = []
        self.segment_index = 0
        self.segment_duration = 0
        self.segment_elapsed_before_pause = 0.0
        self.segment_started_at = None

        self.schedule_running = False
        self.schedule_paused = False
        self.selected_device_id = None

        self._timer_after_id = None

        self.status_var = tk.StringVar(value=self.t("status_ready"))
        self.remaining_var = tk.StringVar(value="00:00:00")
        self.total_remaining_var = tk.StringVar(value="00:00:00")
        self.near_estimate_var = tk.StringVar()
        self.far_estimate_var = tk.StringVar()

        self._apply_theme()

        self._build_ui()
        self._style_combobox_popdowns()
        self._load_devices()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------------------------------------------------
    # Çeviri yardımcıları
    # ---------------------------------------------------------

    def t(self, key, **kwargs):
        text = TRANSLATIONS[self.lang].get(key, key)

        if kwargs:
            return text.format(**kwargs)

        return text

    def _title_text(self):
        return self.t("app_title").upper()

    def _reg_text(self, widget, key):
        """Statik metinli bir widget'ı kaydeder ve mevcut dile göre metnini ayarlar."""
        widget.config(text=self.t(key))
        self._i18n_widgets.append((widget, key))
        return widget

    def _apply_language(self):
        self.root.title(self.t("app_title"))
        self.title_label.config(text=self._title_text())

        for widget, key in self._i18n_widgets:
            widget.config(text=self.t(key))

        self._update_theme_button_text()
        self._update_pause_button_text()
        self._refresh_status_display()
        self._update_estimates()

    def _on_language_selected(self, _event=None):
        display_name = self.lang_var.get()

        code = "tr"
        for lang_code, name in LANGUAGE_DISPLAY_NAMES.items():
            if name == display_name:
                code = lang_code
                break

        if code == self.lang:
            return

        self.lang = code
        self._apply_language()

    # ---------------------------------------------------------
    # Tema
    # ---------------------------------------------------------

    def _apply_theme(self):
        colors = THEMES[self.theme]
        style = ttk.Style(self.root)

        if "clam" in style.theme_names():
            style.theme_use("clam")

        self.root.configure(background=colors["bg"])

        style.configure("TFrame", background=colors["bg"])
        style.configure(
            "TLabelframe",
            background=colors["bg"],
            bordercolor=colors["border"],
            darkcolor=colors["bg"],
            lightcolor=colors["bg"],
        )
        style.configure(
            "TLabelframe.Label",
            background=colors["bg"],
            foreground=colors["fg"],
        )
        style.configure("TLabel", background=colors["bg"], foreground=colors["fg"])
        style.configure(
            "Muted.TLabel", background=colors["bg"], foreground=colors["muted_fg"]
        )
        style.configure(
            "Warning.TLabel", background=colors["bg"], foreground=colors["warning_fg"]
        )

        style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"])
        style.map(
            "TCheckbutton",
            background=[("active", colors["bg"])],
            foreground=[
                ("disabled", colors["disabled_fg"]),
                ("active", colors["fg"]),
            ],
        )

        style.configure(
            "TButton",
            background=colors["button_bg"],
            foreground=colors["button_fg"],
            bordercolor=colors["border"],
            focuscolor=colors["bg"],
        )
        style.map(
            "TButton",
            background=[
                ("disabled", colors["bg"]),
                ("pressed", colors["button_active_bg"]),
                ("active", colors["button_active_bg"]),
            ],
            foreground=[("disabled", colors["disabled_fg"])],
        )

        style.configure(
            "TEntry",
            fieldbackground=colors["entry_bg"],
            foreground=colors["entry_fg"],
            background=colors["bg"],
            bordercolor=colors["border"],
            insertcolor=colors["fg"],
        )
        style.map(
            "TEntry",
            fieldbackground=[
                ("readonly", colors["entry_bg"]),
                ("disabled", colors["bg"]),
            ],
            foreground=[("disabled", colors["disabled_fg"])],
        )

        style.configure(
            "TSpinbox",
            fieldbackground=colors["entry_bg"],
            foreground=colors["entry_fg"],
            background=colors["bg"],
            arrowcolor=colors["fg"],
            bordercolor=colors["border"],
            insertcolor=colors["fg"],
        )
        style.map(
            "TSpinbox",
            fieldbackground=[
                ("readonly", colors["entry_bg"]),
                ("disabled", colors["bg"]),
            ],
            foreground=[("disabled", colors["disabled_fg"])],
        )

        style.configure(
            "TCombobox",
            fieldbackground=colors["entry_bg"],
            foreground=colors["entry_fg"],
            background=colors["bg"],
            arrowcolor=colors["fg"],
            bordercolor=colors["border"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", colors["entry_bg"]),
                ("disabled", colors["bg"]),
            ],
            foreground=[("disabled", colors["disabled_fg"])],
            selectbackground=[("readonly", colors["entry_bg"])],
            selectforeground=[("readonly", colors["entry_fg"])],
        )

        style.configure(
            "Horizontal.TScale", background=colors["bg"], troughcolor=colors["trough"]
        )
        style.configure("TSeparator", background=colors["border"])

        # ttk.Combobox'ın açılır listesi aslında bir Tk Listbox'tır ve ttk
        # stil sistemi tarafından değil, Tk seçenek veritabanı (option
        # database) tarafından kontrol edilir. Koyu modda bu liste
        # güncellenmezse okunaksız kalır. option_add en azından ileride
        # oluşturulacak popdown'lar için bir güvenlik ağı;
        # _style_combobox_popdowns ise zaten var olan popdown'ları
        # doğrudan (ve güvenilir biçimde) renklendirir.
        self.root.option_add("*TCombobox*Listbox.background", colors["entry_bg"])
        self.root.option_add("*TCombobox*Listbox.foreground", colors["entry_fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", colors["select_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", colors["select_fg"])

        self._style_combobox_popdowns()

    def _style_combobox_popdowns(self):
        """
        ttk.Combobox'ın açılır listesi (popdown), Tk seçenek veritabanı
        her zaman güncel widget'ları etkilemeyebildiği için, burada
        doğrudan Tcl seviyesinde bulunup renklendiriliyor. Bu, farklı
        Tk sürümleri/platformları arasında `option_add` glob deseninden
        daha güvenilir çalışıyor. Widget'lar henüz oluşturulmadıysa
        (ör. __init__ sırasındaki ilk tema uygulaması) veya Tcl
        çağrısı bu platformda desteklenmiyorsa sessizce atlanır —
        sadece görsel bir iyileştirme olduğu için hata uygulamayı
        etkilememeli.
        """

        colors = THEMES[self.theme]

        for combo_name in ("lang_combo", "device_combo"):
            combo = getattr(self, combo_name, None)

            if combo is None:
                continue

            try:
                popdown = combo.tk.call("ttk::combobox::PopdownWindow", str(combo))
                listbox_path = f"{popdown}.f.l"
                combo.tk.call(
                    listbox_path,
                    "configure",
                    "-background", colors["entry_bg"],
                    "-foreground", colors["entry_fg"],
                    "-selectbackground", colors["select_bg"],
                    "-selectforeground", colors["select_fg"],
                )
            except tk.TclError as exc:
                print("Combobox popdown teması uygulanamadı:", exc)

    def _toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()
        self._update_theme_button_text()

    def _update_theme_button_text(self):
        key = "theme_toggle_to_light" if self.theme == "dark" else "theme_toggle_to_dark"
        self.theme_button.config(text=self.t(key))

    def _update_pause_button_text(self):
        key = "btn_resume" if self.schedule_paused else "btn_pause"
        self.pause_button.config(text=self.t(key))

    def _volume_changed(self, value):
        volume = float(value)

        self.volume_label.config(
            text=f"{int(volume)}%"
        )

        self.player.set_volume(
            volume / 100.0
        )

        self._update_estimates()

    def _gain_changed(self, value):
        gain_db = float(value)

        self.gain_label.config(
            text=f"+{gain_db:.1f} dB"
        )

        self.player.set_gain_db(gain_db)
        self._update_estimates()

    # ---------------------------------------------------------
    # dB tahmini (yakın / uzak)
    #
    # Mevcut kalibrasyon fikri korunuyor: kullanıcı hoparlör yanında ve
    # dinleme noktasında ÖLÇTÜĞÜ mevcut seviyeleri giriyor. Bu ölçümler
    # hangi Ses Seviyesi (%) ve dB Ayarı değerinde alındıysa o an
    # "referans" olarak saklanıyor (bkz. _on_reference_measurement_changed).
    #
    # Kullanıcı daha sonra Ses Seviyesi veya dB Ayarı'nı değiştirdiğinde,
    # çıkışın referans ana göre kaç dB değiştiği hesaplanıp (relatif fark)
    # ölçülen değerlere eklenir. Böylece:
    #   - Ses Seviyesi (%) de hesaba katılıyor (eski koddaki eksik nokta),
    #   - "Hedef dB" gibi fiziksel olarak kesin bir değer iddia edilmiyor,
    #   - Gösterilen değerler açıkça "tahmini" olarak sunuluyor.
    # ---------------------------------------------------------

    def _volume_to_db(self, volume):
        """0..1 aralığındaki lineer bir çarpanı dB'ye çevirir (taban sınırlı)."""

        if volume <= 0.0001:
            return SILENT_FLOOR_DB

        return max(SILENT_FLOOR_DB, 20.0 * math.log10(volume))

    def _current_output_db(self):
        return self._volume_to_db(self.player.volume) + self.player.gain_db

    def _reference_output_db(self):
        return self._volume_to_db(self.reference_volume) + self.reference_gain_db

    def _snapshot_reference_point(self):
        """Yakın/Uzak Ölçüm alanları güncellendiğinde o anki ses ayarlarını kaydeder."""

        self.reference_volume = self.player.volume
        self.reference_gain_db = self.player.gain_db

    def _on_reference_measurement_changed(self, *_args):
        self._snapshot_reference_point()
        self._update_estimates()

    def _update_estimates(self):
        try:
            near_ref = float(self.near_db_var.get())
            far_ref = float(self.far_db_var.get())
        except ValueError:
            message = self.t("calibration_invalid")
            self.near_estimate_var.set(message)
            self.far_estimate_var.set("")
            return

        delta_db = self._current_output_db() - self._reference_output_db()

        estimated_near = near_ref + delta_db
        estimated_far = far_ref + delta_db

        self.near_estimate_var.set(
            f"{self.t('estimate_near')}: ~{estimated_near:.0f} dB"
        )
        self.far_estimate_var.set(
            f"{self.t('estimate_far')}: ~{estimated_far:.0f} dB"
        )

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build_ui(self):
        # Sabit dikey (uzun boylu) pencere yerine, iki sütunlu yatay bir
        # yerleşim kullanıyoruz; hem daha kısa hem de daha geniş bir
        # pencere ortaya çıkıyor. Pencere ayrıca yeniden boyutlandırılabilir
        # bırakılıyor ki içerik hesaplaması ekrana tam oturmasa bile
        # kullanıcı pencereyi taşıyıp/küçültüp BAŞLAT butonuna ulaşabilsin.
        self.root.resizable(True, True)

        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        # ÜST BAR: dil seçici + tema düğmesi (sağ üst, kompakt)
        top_bar = ttk.Frame(main)
        top_bar.pack(fill="x")

        top_controls = ttk.Frame(top_bar)
        top_controls.pack(side="right")

        self.lang_var = tk.StringVar(value=LANGUAGE_DISPLAY_NAMES[self.lang])

        self.lang_combo = ttk.Combobox(
            top_controls,
            textvariable=self.lang_var,
            state="readonly",
            width=9,
            values=list(LANGUAGE_DISPLAY_NAMES.values()),
        )
        self.lang_combo.pack(side="left", padx=(0, 6))
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_selected)

        self.theme_button = ttk.Button(
            top_controls,
            text=self.t("theme_toggle_to_dark"),
            command=self._toggle_theme,
            width=12,
        )
        self.theme_button.pack(side="left")

        # BAŞLIK
        self.title_label = ttk.Label(
            main,
            text=self._title_text(),
            font=("Arial", 17, "bold"),
        )
        self.title_label.pack(pady=(0, 10))

        # ÜST BÖLÜM: SOL / SAĞ İKİ SÜTUN
        columns = ttk.Frame(main)
        columns.pack(fill="both", expand=True)

        left_col = ttk.Frame(columns)
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 8))

        right_col = ttk.Frame(columns)
        right_col.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # ÇALIŞMA SÜRESİ (SOL SÜTUN)
        duration_frame = ttk.LabelFrame(left_col, padding=10)
        duration_frame.pack(fill="x", pady=4)
        self._reg_text(duration_frame, "section_duration")

        self.hours_var = tk.StringVar(value="01")
        self.minutes_var = tk.StringVar(value="00")
        self.seconds_var = tk.StringVar(value="00")

        duration_content = ttk.Frame(duration_frame)
        duration_content.pack()

        self._reg_text(
            ttk.Label(duration_content), "label_hours"
        ).grid(row=0, column=0, padx=18)

        self._reg_text(
            ttk.Label(duration_content), "label_minutes"
        ).grid(row=0, column=1, padx=18)

        self._reg_text(
            ttk.Label(duration_content), "label_seconds"
        ).grid(row=0, column=2, padx=18)

        self.hours_spin = ttk.Spinbox(
            duration_content,
            from_=0,
            to=99,
            width=5,
            textvariable=self.hours_var,
        )
        self.hours_spin.grid(row=1, column=0, padx=18)

        self.minutes_spin = ttk.Spinbox(
            duration_content,
            from_=0,
            to=59,
            width=5,
            textvariable=self.minutes_var,
        )
        self.minutes_spin.grid(row=1, column=1, padx=18)

        self.seconds_spin = ttk.Spinbox(
            duration_content,
            from_=0,
            to=59,
            width=5,
            textvariable=self.seconds_var,
        )
        self.seconds_spin.grid(row=1, column=2, padx=18)

        # ARALIKLI ÇALIŞMA (ÇALIŞ / DUR DÖNGÜSÜ) (SOL SÜTUN)
        cycle_frame = ttk.LabelFrame(left_col, padding=10)
        cycle_frame.pack(fill="x", pady=4)
        self._reg_text(cycle_frame, "section_cycle")

        self.cycle_var = tk.BooleanVar(value=True)

        self.cycle_check = ttk.Checkbutton(
            cycle_frame,
            variable=self.cycle_var,
            command=self._on_cycle_toggle,
        )
        self.cycle_check.pack(anchor="w", padx=5, pady=(0, 4))
        self._reg_text(self.cycle_check, "check_cycle")

        self._reg_text(
            ttk.Label(cycle_frame, wraplength=380), "cycle_desc"
        ).pack(anchor="w", fill="x", padx=5, pady=(0, 8))

        self._reg_text(
            ttk.Label(cycle_frame), "cycle_off_label"
        ).pack(anchor="w", padx=5, pady=(0, 4))

        cycle_content = ttk.Frame(cycle_frame)
        cycle_content.pack()

        self.off_hours_var = tk.StringVar(value="01")
        self.off_minutes_var = tk.StringVar(value="00")
        self.off_seconds_var = tk.StringVar(value="00")
        self.repeat_var = tk.StringVar(value=str(DEFAULT_CYCLE_REPEATS))

        self._reg_text(
            ttk.Label(cycle_content), "label_hours"
        ).grid(row=0, column=0, padx=12)

        self._reg_text(
            ttk.Label(cycle_content), "label_minutes"
        ).grid(row=0, column=1, padx=12)

        self._reg_text(
            ttk.Label(cycle_content), "label_seconds"
        ).grid(row=0, column=2, padx=12)

        self._reg_text(
            ttk.Label(cycle_content), "label_repeat"
        ).grid(row=0, column=3, padx=12)

        self.off_hours_spin = ttk.Spinbox(
            cycle_content,
            from_=0,
            to=99,
            width=5,
            textvariable=self.off_hours_var,
        )
        self.off_hours_spin.grid(row=1, column=0, padx=12)

        self.off_minutes_spin = ttk.Spinbox(
            cycle_content,
            from_=0,
            to=59,
            width=5,
            textvariable=self.off_minutes_var,
        )
        self.off_minutes_spin.grid(row=1, column=1, padx=12)

        self.off_seconds_spin = ttk.Spinbox(
            cycle_content,
            from_=0,
            to=59,
            width=5,
            textvariable=self.off_seconds_var,
        )
        self.off_seconds_spin.grid(row=1, column=2, padx=12)

        self.repeat_spin = ttk.Spinbox(
            cycle_content,
            from_=1,
            to=99,
            width=5,
            textvariable=self.repeat_var,
        )
        self.repeat_spin.grid(row=1, column=3, padx=12)

        self._reg_text(
            ttk.Label(cycle_frame, style="Muted.TLabel", wraplength=380),
            "cycle_default_note",
        ).pack(fill="x", padx=5, pady=(8, 0))

        # SES SEVİYESİ (SAĞ SÜTUN)
        volume_frame = ttk.LabelFrame(right_col, padding=10)
        volume_frame.pack(fill="x", pady=4)
        self._reg_text(volume_frame, "section_volume")

        volume_row = ttk.Frame(volume_frame)
        volume_row.pack(fill="x")

        self.volume_var = tk.DoubleVar(value=100)

        self.volume_slider = ttk.Scale(
            volume_row,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volume_var,
            command=self._volume_changed,
        )

        self.volume_slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 12),
        )

        self.volume_label = ttk.Label(
            volume_row,
            text="100%",
            width=5,
        )

        self.volume_label.pack(side="right")

        # dB AYARI (SAĞ SÜTUN) — eski "Ses Yükseltici" + "dB Kalibrasyonu"
        # bölümlerinin birleşimi. İşlevsiz "Hedef uzak" alanı ve
        # "Hesaplanan Yükseltmeyi Uygula" butonu kaldırıldı; yerine
        # slider'ın hemen altında canlı güncellenen yakın/uzak tahmini
        # eklendi (bkz. _update_estimates).
        db_frame = ttk.LabelFrame(right_col, padding=10)
        db_frame.pack(fill="x", pady=4)
        self._reg_text(db_frame, "section_db")

        gain_row = ttk.Frame(db_frame)
        gain_row.pack(fill="x")

        self.gain_var = tk.DoubleVar(value=0)

        self.gain_slider = ttk.Scale(
            gain_row,
            from_=0,
            to=MAX_GAIN_DB,
            orient="horizontal",
            variable=self.gain_var,
            command=self._gain_changed,
        )

        self.gain_slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(5, 12),
        )

        self.gain_label = ttk.Label(
            gain_row,
            text="+0.0 dB",
            width=8,
        )

        self.gain_label.pack(side="right")

        # Canlı tahmini SPL değerleri — dB Ayarı'nın hemen altında, tek
        # bakışta okunabilecek şekilde alt alta.
        ttk.Label(
            db_frame,
            textvariable=self.near_estimate_var,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", padx=5, pady=(8, 0))

        ttk.Label(
            db_frame,
            textvariable=self.far_estimate_var,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", padx=5, pady=(0, 4))

        self._reg_text(
            ttk.Label(db_frame, style="Warning.TLabel", wraplength=380),
            "db_warning",
        ).pack(fill="x", padx=5, pady=(4, 8))

        # Referans ölçüm alanları (yakın/uzak). Bu ölçümler ne zaman
        # değiştirilirse, o andaki Ses Seviyesi/dB Ayarı otomatik olarak
        # yeni referans noktası kabul edilir.
        ref_grid = ttk.Frame(db_frame)
        ref_grid.pack(fill="x")

        self.near_db_var = tk.StringVar(value=f"{DEFAULT_NEAR_DB:.0f}")
        self.far_db_var = tk.StringVar(value=f"{DEFAULT_FAR_DB:.0f}")

        self._reg_text(
            ttk.Label(ref_grid), "label_near_ref"
        ).grid(row=0, column=0, sticky="w", padx=5)

        self._reg_text(
            ttk.Label(ref_grid), "label_far_ref"
        ).grid(row=0, column=1, sticky="w", padx=5)

        near_entry = ttk.Entry(
            ref_grid,
            textvariable=self.near_db_var,
            width=10,
        )
        near_entry.grid(row=1, column=0, sticky="ew", padx=5)

        far_entry = ttk.Entry(
            ref_grid,
            textvariable=self.far_db_var,
            width=10,
        )
        far_entry.grid(row=1, column=1, sticky="ew", padx=5)

        for column in range(2):
            ref_grid.columnconfigure(column, weight=1)

        for variable in (self.near_db_var, self.far_db_var):
            variable.trace_add(
                "write",
                self._on_reference_measurement_changed,
            )

        # Başlangıç referans noktasını mevcut (varsayılan) ses ayarlarıyla
        # eşitle ve tahminleri ilk kez hesapla.
        self._snapshot_reference_point()
        self._update_estimates()

        # SES ÇIKIŞI (SAĞ SÜTUN)
        output_frame = ttk.LabelFrame(right_col, padding=10)
        output_frame.pack(fill="x", pady=4)
        self._reg_text(output_frame, "section_output")

        self.device_var = tk.StringVar()

        self.device_combo = ttk.Combobox(
            output_frame,
            textvariable=self.device_var,
            state="readonly",
        )

        self.device_combo.pack(
            fill="x",
            padx=5,
            pady=(0, 7),
        )

        self._reg_text(
            ttk.Button(output_frame, command=self._load_devices),
            "btn_refresh_devices",
        ).pack(
            fill="x",
            padx=5,
        )

        # DURUM / KALAN SÜRE / TOPLAM KALAN — tek satırda yatay bilgi çubuğu
        info_frame = ttk.Frame(main)
        info_frame.pack(fill="x", pady=(10, 8))

        status_block = ttk.Frame(info_frame)
        status_block.pack(side="left", padx=(0, 24))

        self._reg_text(
            ttk.Label(status_block, font=("Arial", 10, "bold")), "label_status"
        ).pack(side="left")

        ttk.Label(
            status_block,
            textvariable=self.status_var,
            font=("Arial", 10),
        ).pack(side="left", padx=6)

        remaining_block = ttk.Frame(info_frame)
        remaining_block.pack(side="left", padx=(0, 24))

        self._reg_text(
            ttk.Label(remaining_block, font=("Arial", 10, "bold")), "label_remaining"
        ).pack(side="left")

        ttk.Label(
            remaining_block,
            textvariable=self.remaining_var,
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=6)

        total_remaining_block = ttk.Frame(info_frame)
        total_remaining_block.pack(side="left")

        self._reg_text(
            ttk.Label(total_remaining_block, font=("Arial", 10, "bold")),
            "label_total_remaining",
        ).pack(side="left")

        ttk.Label(
            total_remaining_block,
            textvariable=self.total_remaining_var,
            font=("Arial", 10),
        ).pack(side="left", padx=6)

        # BAŞLAT
        self.start_button = ttk.Button(
            main,
            command=self.start,
        )

        self.start_button.pack(
            fill="x",
            ipady=5,
            pady=(0, 6),
        )
        self._reg_text(self.start_button, "btn_start")

        # DURAKLAT / BİTİR
        control_frame = ttk.Frame(main)
        control_frame.pack(fill="x")

        self.pause_button = ttk.Button(
            control_frame,
            command=self.pause_resume,
            state="disabled",
        )

        self.pause_button.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 4),
            ipady=4,
        )
        self._update_pause_button_text()

        self.stop_button = ttk.Button(
            control_frame,
            command=self.stop,
            state="disabled",
        )

        self.stop_button.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(4, 0),
            ipady=4,
        )
        self._reg_text(self.stop_button, "btn_stop")

        self._apply_cycle_widget_states()

        # Pencereyi içeriğin doğal boyutuna göre otomatik ayarla; pencere
        # yeniden boyutlandırılabilir bırakılıyor (yukarıda resizable(True,
        # True) yapıldı) ki hesaplanan boyut ekrana tam oturmasa bile
        # kullanıcı pencereyi küçültüp taşıyabilsin.
        self.root.update_idletasks()
        width = max(900, self.root.winfo_reqwidth())
        height = self.root.winfo_reqheight()
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(min(width, 760), min(height, 520))

    # ---------------------------------------------------------
    # Devices
    # ---------------------------------------------------------

    def _load_devices(self):
        try:
            current_device = self.device_var.get()
            self.devices = []

            devices = sd.query_devices()

            output_devices = []

            for index, device in enumerate(devices):
                if device["max_output_channels"] > 0:
                    output_devices.append(
                        (index, device["name"])
                    )

            self.devices = output_devices

            names = [
                name
                for _, name in output_devices
            ]

            self.device_combo["values"] = names

            if not names:
                self.device_var.set("")
                return

            # Önceden seçili cihaz hâlâ mevcutsa onu koru
            if current_device in names:
                self.device_var.set(current_device)
            else:
                self.device_combo.current(0)

        except Exception as exc:
            messagebox.showerror(
                self.t("err_device_title"),
                str(exc),
            )

    # ---------------------------------------------------------
    # Aralıklı çalışma alanı (checkbox) durumu
    # ---------------------------------------------------------

    def _on_cycle_toggle(self):
        self._apply_cycle_widget_states()

    def _apply_cycle_widget_states(self):
        state = "normal" if self.cycle_var.get() else "disabled"

        for widget in (
            self.off_hours_spin,
            self.off_minutes_spin,
            self.off_seconds_spin,
            self.repeat_spin,
        ):
            widget.config(state=state)

    # ---------------------------------------------------------
    # Süre / program (segment) hesaplama
    # ---------------------------------------------------------

    def _parse_duration(self, hours_var, minutes_var, seconds_var):
        hours = int(hours_var.get())
        minutes = int(minutes_var.get())
        seconds = int(seconds_var.get())

        if hours < 0:
            raise ValueError

        if not 0 <= minutes <= 59:
            raise ValueError

        if not 0 <= seconds <= 59:
            raise ValueError

        total = (
            hours * 3600
            + minutes * 60
            + seconds
        )

        if total <= 0:
            raise ValueError

        return total

    def _get_duration(self):
        try:
            return self._parse_duration(
                self.hours_var,
                self.minutes_var,
                self.seconds_var,
            )
        except ValueError:
            messagebox.showerror(
                self.t("err_invalid_duration_title"),
                self.t("err_invalid_work_duration_msg"),
            )
            return None

    def _get_off_duration(self):
        try:
            return self._parse_duration(
                self.off_hours_var,
                self.off_minutes_var,
                self.off_seconds_var,
            )
        except ValueError:
            messagebox.showerror(
                self.t("err_invalid_duration_title"),
                self.t("err_invalid_rest_duration_msg"),
            )
            return None

    def _get_repeat_count(self):
        try:
            repeats = int(self.repeat_var.get())

            if not 1 <= repeats <= 99:
                raise ValueError

            return repeats

        except ValueError:
            messagebox.showerror(
                self.t("err_invalid_repeat_title"),
                self.t("err_invalid_repeat_msg"),
            )
            return None

    def _build_segments(self):
        on_duration = self._get_duration()

        if on_duration is None:
            return None

        if not self.cycle_var.get():
            return [("ON", on_duration)]

        off_duration = self._get_off_duration()

        if off_duration is None:
            return None

        repeats = self._get_repeat_count()

        if repeats is None:
            return None

        segments = []

        for _ in range(repeats):
            segments.append(("ON", on_duration))
            segments.append(("OFF", off_duration))

        return segments

    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------

    def start(self):
        segments = self._build_segments()

        if segments is None:
            return

        if not self.devices:
            messagebox.showerror(
                self.t("err_output_title"),
                self.t("err_no_output_msg"),
            )
            return

        selected_index = self.device_combo.current()

        if selected_index < 0:
            messagebox.showerror(
                self.t("err_output_title"),
                self.t("err_select_output_msg"),
            )
            return

        self.selected_device_id = self.devices[selected_index][0]
        self.segments = segments

        self.schedule_running = True
        self.schedule_paused = False

        self.start_button.config(state="disabled")
        self._update_pause_button_text()
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        for widget in (
            self.hours_spin,
            self.minutes_spin,
            self.seconds_spin,
            self.cycle_check,
            self.off_hours_spin,
            self.off_minutes_spin,
            self.off_seconds_spin,
            self.repeat_spin,
        ):
            widget.config(state="disabled")

        self._enter_segment(0)

    # ---------------------------------------------------------
    # Program (segment) akışı
    # ---------------------------------------------------------

    def _enter_segment(self, index):
        if index >= len(self.segments):
            self._complete_schedule()
            return

        self.segment_index = index

        kind, duration = self.segments[index]

        self.segment_duration = duration
        self.segment_elapsed_before_pause = 0.0
        self.segment_started_at = time.monotonic()

        if kind == "ON":
            try:
                self.player.start(self.selected_device_id)
            except Exception as exc:
                messagebox.showerror(
                    self.t("err_audio_start_title"),
                    str(exc),
                )
                self._abort_schedule()
                return
        else:
            self.player.stop()

        self.status_var.set(self._status_text())

        self._update_timer()

    def _status_text(self):
        kind, _ = self.segments[self.segment_index]
        running_label = self.t("status_running") if kind == "ON" else self.t("status_resting")

        if not self.cycle_var.get() or len(self.segments) <= 1:
            return running_label

        cycle_number = self.segment_index // 2 + 1
        total_cycles = len(self.segments) // 2
        phase = self.t("phase_work") if kind == "ON" else self.t("phase_rest")

        return f"{running_label} ({phase} {cycle_number}/{total_cycles})"

    def _refresh_status_display(self):
        """Dil değiştiğinde o anki duruma göre status_var'ı yeniden çevirir."""

        if self.schedule_running and not self.schedule_paused and self.segments:
            self.status_var.set(self._status_text())
        else:
            self.status_var.set(self.t(self._last_simple_status_key))

    # ---------------------------------------------------------
    # Pause / Resume
    # ---------------------------------------------------------

    def pause_resume(self):
        if not self.schedule_running:
            return

        if not self.schedule_paused:
            elapsed = time.monotonic() - self.segment_started_at
            self.segment_elapsed_before_pause = elapsed

            self.schedule_paused = True
            self.player.pause()

            self._cancel_timer()

            self._last_simple_status_key = "status_paused"
            self.status_var.set(self.t("status_paused"))
            self._update_pause_button_text()

        else:
            self.player.resume()

            self.segment_started_at = (
                time.monotonic()
                - self.segment_elapsed_before_pause
            )

            self.schedule_paused = False

            self.status_var.set(self._status_text())
            self._update_pause_button_text()

            self._update_timer()

    # ---------------------------------------------------------
    # Stop / bitirme durumları
    # ---------------------------------------------------------

    def stop(self):
        self._cancel_timer()
        self.player.stop()

        self.schedule_running = False
        self.schedule_paused = False
        self.segments = []
        self.segment_index = 0
        self.segment_started_at = None

        self._reset_controls_to_idle("status_stopped")

    def _complete_schedule(self):
        self._cancel_timer()
        self.player.stop()

        self.schedule_running = False
        self.schedule_paused = False

        self._reset_controls_to_idle("status_completed")

    def _abort_schedule(self):
        self._cancel_timer()
        self.player.stop()

        self.schedule_running = False
        self.schedule_paused = False

        self._reset_controls_to_idle("status_error")

    def _reset_controls_to_idle(self, status_key):
        self.remaining_var.set("00:00:00")
        self.total_remaining_var.set("00:00:00")

        self._last_simple_status_key = status_key
        self.status_var.set(self.t(status_key))

        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self._update_pause_button_text()
        self.stop_button.config(state="disabled")

        for widget in (
            self.hours_spin,
            self.minutes_spin,
            self.seconds_spin,
            self.cycle_check,
        ):
            widget.config(state="normal")

        self._apply_cycle_widget_states()

    # ---------------------------------------------------------
    # Timer
    # ---------------------------------------------------------

    def _cancel_timer(self):
        if self._timer_after_id is not None:
            try:
                self.root.after_cancel(self._timer_after_id)
            except Exception:
                pass

            self._timer_after_id = None

    def _format_seconds(self, seconds):
        total = max(0, int(seconds))

        hours = total // 3600
        minutes = (total % 3600) // 60
        secs = total % 60

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _total_remaining(self, current_segment_elapsed):
        remaining = self.segment_duration - current_segment_elapsed

        for _, duration in self.segments[self.segment_index + 1:]:
            remaining += duration

        return remaining

    def _update_timer(self):
        if not self.schedule_running or self.schedule_paused:
            return

        elapsed = (
            time.monotonic()
            - self.segment_started_at
        )

        remaining = self.segment_duration - elapsed

        if remaining <= 0:
            self._enter_segment(self.segment_index + 1)
            return

        self.remaining_var.set(self._format_seconds(remaining))
        self.total_remaining_var.set(
            self._format_seconds(self._total_remaining(elapsed))
        )

        self._timer_after_id = self.root.after(
            250,
            self._update_timer,
        )

    # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def _on_close(self):
        self._cancel_timer()
        self.player.stop()
        self.sleep_guard.stop()
        self.root.destroy()


def main():
    root = tk.Tk()

    app = SoundTestApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()

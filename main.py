import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import sounddevice as sd


SAMPLE_RATE = 44100
CHANNELS = 2


class WhiteNoisePlayer:
    def __init__(self):
        self.volume = 1.0
        self.stream = None
        self.buffer = self._create_noise_buffer()

        self.running = False
        self.paused = False
        self.device = None

        self.start_time = None
        self.pause_started = None
        self.total_paused_time = 0.0

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, float(volume)))

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

        # Başlangıç/bitişte küçük fade,
        # loop noktasındaki klik ihtimalini azaltır.
        fade_samples = int(SAMPLE_RATE * 0.02)

        fade_in = np.linspace(
            0.0,
            1.0,
            fade_samples
        )

        fade_out = np.linspace(
            1.0,
            0.0,
            fade_samples
        )

        noise[:fade_samples] *= fade_in[:, None]
        noise[-fade_samples:] *= fade_out[:, None]

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

            outdata[
                output_position:output_position + count
            ] = (
                    self.buffer[
                        self._buffer_position:self._buffer_position + count
                    ] * self.volume
            )

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
        self.root.title("Beyaz Gürültü Sistemi")

        self.root.resizable(False, False)

        self.player = WhiteNoisePlayer()

        self.duration_seconds = 0
        self.elapsed_before_pause = 0.0
        self.started_at = None

        self.status_var = tk.StringVar(value="HAZIR")
        self.remaining_var = tk.StringVar(value="00:00:00")

        self._build_ui()
        self._load_devices()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _volume_changed(self, value):
        volume = float(value)

        self.volume_label.config(
            text=f"{int(volume)}%"
        )

        self.player.set_volume(
            volume / 100.0
        )

    # ---------------------------------------------------------
    # UI
    # ---------------------------------------------------------

    def _build_ui(self):
        self.root.geometry("500x500")
        self.root.minsize(500, 500)
        self.root.maxsize(500, 500)

        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        # BAŞLIK
        ttk.Label(
            main,
            text="BEYAZ GÜRÜLTÜ SİSTEMİ",
            font=("Arial", 17, "bold"),
        ).pack(pady=(0, 12))

        # ÇALIŞMA SÜRESİ
        duration_frame = ttk.LabelFrame(
            main,
            text="Çalışma Süresi",
            padding=10,
        )
        duration_frame.pack(fill="x", pady=4)

        self.hours_var = tk.StringVar(value="03")
        self.minutes_var = tk.StringVar(value="00")
        self.seconds_var = tk.StringVar(value="00")

        duration_content = ttk.Frame(duration_frame)
        duration_content.pack()

        ttk.Label(
            duration_content,
            text="Saat",
        ).grid(row=0, column=0, padx=18)

        ttk.Label(
            duration_content,
            text="Dakika",
        ).grid(row=0, column=1, padx=18)

        ttk.Label(
            duration_content,
            text="Saniye",
        ).grid(row=0, column=2, padx=18)

        ttk.Spinbox(
            duration_content,
            from_=0,
            to=99,
            width=5,
            textvariable=self.hours_var,
        ).grid(row=1, column=0, padx=18)

        ttk.Spinbox(
            duration_content,
            from_=0,
            to=59,
            width=5,
            textvariable=self.minutes_var,
        ).grid(row=1, column=1, padx=18)

        ttk.Spinbox(
            duration_content,
            from_=0,
            to=59,
            width=5,
            textvariable=self.seconds_var,
        ).grid(row=1, column=2, padx=18)

        # SES SEVİYESİ
        volume_frame = ttk.LabelFrame(
            main,
            text="Ses Seviyesi",
            padding=10,
        )
        volume_frame.pack(fill="x", pady=4)

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

        # SES ÇIKIŞI
        output_frame = ttk.LabelFrame(
            main,
            text="Ses Çıkışı",
            padding=10,
        )
        output_frame.pack(fill="x", pady=4)

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

        ttk.Button(
            output_frame,
            text="Ses Çıkışlarını Yenile",
            command=self._load_devices,
        ).pack(
            fill="x",
            padx=5,
        )

        # DURUM
        status_frame = ttk.Frame(main)
        status_frame.pack(
            fill="x",
            pady=(8, 2),
        )

        ttk.Label(
            status_frame,
            text="Durum:",
            font=("Arial", 10, "bold"),
        ).pack(side="left")

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 10),
        ).pack(side="left", padx=6)

        # KALAN SÜRE
        remaining_frame = ttk.Frame(main)
        remaining_frame.pack(
            fill="x",
            pady=(2, 8),
        )

        ttk.Label(
            remaining_frame,
            text="Kalan Süre:",
            font=("Arial", 10, "bold"),
        ).pack(side="left")

        ttk.Label(
            remaining_frame,
            textvariable=self.remaining_var,
            font=("Arial", 12, "bold"),
        ).pack(side="left", padx=6)

        # BAŞLAT
        self.start_button = ttk.Button(
            main,
            text="BAŞLAT",
            command=self.start,
        )

        self.start_button.pack(
            fill="x",
            ipady=5,
            pady=(0, 6),
        )

        # DURAKLAT / BİTİR
        control_frame = ttk.Frame(main)
        control_frame.pack(fill="x")

        self.pause_button = ttk.Button(
            control_frame,
            text="DURAKLAT",
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

        self.stop_button = ttk.Button(
            control_frame,
            text="BİTİR",
            command=self.stop,
            state="disabled",
        )

        self.stop_button.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(4, 0),
            ipady=4,
        )    # ---------------------------------------------------------
    # Devices
    # ---------------------------------------------------------

    def _load_devices(self):
        try:
            current_device = self.device_var.get()

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
                "Ses Cihazı Hatası",
                str(exc),
            )
    # ---------------------------------------------------------
    # Duration
    # ---------------------------------------------------------

    def _get_duration(self):
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            seconds = int(self.seconds_var.get())

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

        except ValueError:
            messagebox.showerror(
                "Geçersiz Süre",
                "Lütfen geçerli bir çalışma süresi girin.",
            )
            return None

    # ---------------------------------------------------------
    # Start
    # ---------------------------------------------------------

    def start(self):
        duration = self._get_duration()

        if duration is None:
            return

        if not self.devices:
            messagebox.showerror(
                "Ses Çıkışı",
                "Kullanılabilir bir ses çıkışı bulunamadı.",
            )
            return

        selected_index = self.device_combo.current()

        if selected_index < 0:
            messagebox.showerror(
                "Ses Çıkışı",
                "Lütfen bir ses çıkışı seçin.",
            )
            return

        device_id = self.devices[selected_index][0]

        try:
            self.player.start(device_id)

        except Exception as exc:
            messagebox.showerror(
                "Ses Başlatılamadı",
                str(exc),
            )
            return

        self.duration_seconds = duration
        self.elapsed_before_pause = 0
        self.started_at = time.monotonic()

        self.status_var.set("ÇALIŞIYOR")

        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")

        self._update_timer()

    # ---------------------------------------------------------
    # Pause / Resume
    # ---------------------------------------------------------

    def pause_resume(self):
        if not self.player.running:
            return

        if not self.player.paused:
            elapsed = time.monotonic() - self.started_at

            self.elapsed_before_pause = elapsed

            self.player.pause()

            self.status_var.set("DURAKLATILDI")
            self.pause_button.config(text="DEVAM ET")

        else:
            self.player.resume()

            self.started_at = (
                time.monotonic()
                - self.elapsed_before_pause
            )

            self.status_var.set("ÇALIŞIYOR")
            self.pause_button.config(text="DURAKLAT")

            self._update_timer()

    # ---------------------------------------------------------
    # Stop
    # ---------------------------------------------------------

    def stop(self):
        self.player.stop()

        self.duration_seconds = 0
        self.elapsed_before_pause = 0
        self.started_at = None

        self.remaining_var.set("00:00:00")
        self.status_var.set("DURDURULDU")

        self.start_button.config(
            state="normal"
        )

        self.pause_button.config(
            state="disabled",
            text="DURAKLAT"
        )

        self.stop_button.config(
            state="disabled"
        )
    # ---------------------------------------------------------
    # Timer
    # ---------------------------------------------------------

    def _update_timer(self):
        if not self.player.running:
            return

        if self.player.paused:
            return

        elapsed = (
            time.monotonic()
            - self.started_at
        )

        remaining = self.duration_seconds - elapsed

        if remaining <= 0:
            self.remaining_var.set("00:00:00")
            self.player.stop()

            self.status_var.set("TAMAMLANDI")

            self.start_button.config(state="normal")
            self.pause_button.config(
                state="disabled",
                text="DURAKLAT",
            )
            self.stop_button.config(state="disabled")

            return

        remaining_int = int(remaining)

        hours = remaining_int // 3600
        minutes = (remaining_int % 3600) // 60
        seconds = remaining_int % 60

        self.remaining_var.set(
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        )

        self.root.after(
            250,
            self._update_timer,
        )

    # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def _on_close(self):
        self.player.stop()
        self.root.destroy()


def main():
    root = tk.Tk()

    app = SoundTestApp(root)

    root.mainloop()


if __name__ == "__main__":
    main()
import json
import sounddevice as sd
import vosk
import queue
import sys
from gtts import gTTS
import os
import time
import subprocess
import webbrowser
import datetime
import random
from PIL import ImageGrab
import sympy as sp  # Matematik çözme için

# Rastgele temiz ve hocaya uygun şakalar
sakalar = [
    "Neden bilgisayar üşür? Çünkü Windows açık!",
    "Adam neden astronot oldu? Çünkü yıldızlara aşık!",
    "Domates neden şarkı söyleyemiyor? Çünkü ketçap!",
    "Matematik kitabım çok üzgün, çünkü çok fazla problemi var.",
    "Karpuz neden şarkıcı olamadı? Çünkü çekirdekleri var!",
    "Tavuk neden yolun karşısına geçti? Karşı tarafa geçmek için!",
    "Neden astronotlar boşanır? Çünkü uzayda çok mesafe var!",
    "Klavye neden üzgün? Çünkü enter tuşu basılı kaldı.",
    "Balık neden okulda başarısız? Çünkü hafızası kısa!",
    "Neden bilgisayar doktor oldu? Çünkü virüsleri iyi tanıyor!",
    "Kaktüs neden yalnız? Çünkü diken üstünde yaşıyor!",
    "Elma neden ağaçtan düştü? Çünkü Newton'un kafasına vurmak istedi!",
    "Neden matematik dersi çok zor? Çünkü x her zaman bilinmeyen!"
]

def speak(text):
    try:
        tts = gTTS(text=text, lang='tr', slow=False)
        filename = "jarvis_temp.mp3"
        tts.save(filename)
        os.system(f'start {filename}')
        time.sleep(3)  # Kısa cevaplar için 3 saniye yeterli
        os.remove(filename)
        print(f"[SES ÇIKTI] {text}")
    except Exception as e:
        print(f"Ses hatası: {e}")
        # Yedek olarak basit print
        print(f"[SES YAZDIRILDI] {text}")

# Model yolu
MODEL_PATH = "model/vosk-model-small-tr-0.3"  # Daha iyi tanıma için model/vosk-model-tr-0.22 yapabilirsin

model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def listen():
    print("Dinliyorum... (konuş!)")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    print(f"Söyledin: {text}")
                    return text.lower()
            else:
                partial = json.loads(rec.PartialResult())
                if partial.get("partial"):
                    print(f"Partial: {partial['partial']}")

def process_command(command):
    if not command:
        return False
    
    if "merhaba" in command or "selam" in command:
        speak("Merhaba efendim, emrinizdeyim!")
    elif "nasılsın" in command or "nasılsın jarvis" in command or "nasılsın efendim" in command:
        speak("İyiyim efendim, teşekkür ederim. Siz nasılsınız efendim?")
    elif "iyiyim" in command or "ben de iyiyim" in command or "güzel" in command:
        speak("Çok sevindim efendim, gününüz güzel geçsin!")
    elif "kötüyüm" in command or "kötü" in command or "üzgünüm" in command:
        speak("Üzüldüm efendim, ne oldu? Anlatmak ister misiniz?")
    elif "saat kaç" in command or "saat" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Şu an saat {now}")
    elif any(kelime in command for kelime in ["ara", "arama yap", "arama", "ara bakayım", "ara lütfen"]):
        query = command
        for kelime in ["ara", "arama yap", "arama", "ara bakayım", "ara lütfen"]:
            query = query.replace(kelime, "")
        query = query.strip()
        if query:
            speak(f"{query} için arama yapıyorum efendim.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("Ne arayayım efendim?")
    elif "şaka yap" in command or "espri yap" in command:
        saka = random.choice(sakalar)
        speak(saka)
    elif any(kelime in command for kelime in ["aç", "başlat", "açılış", "aç lütfen", "ağaç"]):
        app = command.replace("aç", "").replace("başlat", "").replace("açılış", "").replace("aç lütfen", "").replace("ağaç", "").strip()
        if app:
            speak(f"{app} açılıyor efendim.")
            open_app(app)
        else:
            speak("Hangi uygulamayı açayım efendim?")
    elif "not al" in command:
        note = command.replace("not al", "").strip()
        with open("notlar.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now()}: {note}\n")
        speak(f"Not alındı: {note}")
    elif "ekran görüntüsü" in command or "fotoğraf çek" in command:
        screenshot = ImageGrab.grab()
        filename = f"ekran_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        screenshot.save(filename)
        speak(f"Ekran görüntüsü alındı ve {filename} olarak kaydedildi.")
    elif "matematik çöz" in command or "çöz" in command or "hesapla" in command:
        equation = command.replace("matematik çöz", "").replace("çöz", "").replace("hesapla", "").strip()
        try:
            result = sp.sympify(equation)
            speak(f"Sonuç: {result}")
        except:
            speak("Denklemi anlayamadım efendim, 'çöz 2x + 5 = 13' gibi söyleyin.")
    elif "çık" in command or "kapat" in command or "görüşürüz" in command:
        speak("Görüşürüz efendim, iyi günler!")
        return True
    else:
        speak("Bu komutu henüz bilmiyorum efendim, başka ne yapayım?")
    return False

def open_app(app_name):
    app_name = app_name.lower().strip()
    apps = {
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "not defteri": "notepad.exe",
        "hesap makinesi": "calc.exe",
        "spotify": "spotify.exe",
        "discord": "C:\\Users\\user\\AppData\\Local\\Discord\\Discord.exe",
        "valorant": "C:\\Riot Games\\VALORANT\\live\\VALORANT.exe",
        "steam": "C:\\Program Files (x86)\\Steam\\steam.exe",
        "vscode": "C:\\Users\\user\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "paint": "mspaint.exe",
    }
    
    if app_name in apps:
        try:
            os.startfile(apps[app_name])
            return
        except Exception as e:
            print(f"Uygulama yolu hatası: {e}")
    
    try:
        subprocess.Popen(f'start {app_name}', shell=True)
        speak(f"{app_name} aranıyor ve açılıyor.")
    except Exception as e:
        speak(f"Üzgünüm efendim, {app_name} açılamadı.")

# Başlat
speak("Jarvis sistem aktif, emrinizi bekliyorum efendim.")
print("Jarvis başladı. 'çık' diyerek kapatabilirsin.")

while True:
    command = listen()
    if process_command(command):
        break

import os
import subprocess
import requests
import speech_recognition as sr
import time
import asyncio
from gtts import gTTS
from tapo import ApiClient

# Conectando direto no go2rtc para não estourar o limite da câmera
RTSP_URL = os.environ.get("RTSP_URL", "rtsp://go2rtc_server:8554/camera_tapo")
TAPO_IP = os.environ.get("TAPO_IP", "")
TAPO_USER = os.environ.get("TAPO_USER", "")
TAPO_PASSWORD = os.environ.get("TAPO_PASSWORD", "")
WAKE_WORD = "caixa"

recognizer = sr.Recognizer()

async def camera_reaction():
    print("🤖 Conectando na Tapo...")
    try:
        client = ApiClient(TAPO_USER, TAPO_PASSWORD)
        device = await client.generic_device(TAPO_IP) 
        
        await device.move_motor(15, 0)
        await asyncio.sleep(1)
        await device.move_motor(-15, 0)
        print("✅ Câmera se mexeu!")
    except Exception as e:
        print(f"⚠️ Erro Tapo: {e}")

def generate_and_play_response(text):
    print(f"🔊 Gerando voz: '{text}'")
    tts = gTTS(text=text, lang="pt-br")
    tts.save("falar.mp3") 
    print("✅ Áudio gerado e enviado para a JBL!")

def capture_audio(duration, filename="temp.wav"):
    if os.path.exists(filename):
        os.remove(filename)
        
    print(f"🔴 [GRAVANDO {duration}s] FALE AGORA...")
    
    command = [
        "ffmpeg", "-rtsp_transport", "tcp", "-i", RTSP_URL,
        "-t", str(duration), "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1", filename, "-y"
    ]
    # DEVNULL removido para mostrar o erro real se o FFmpeg falhar
    subprocess.run(command)

def transcribe_audio(filename="temp.wav"):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0: 
        print(f"⚠️ Erro: O arquivo {filename} vazio ou não criado.")
        return ""
        
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
        
    try:
        return recognizer.recognize_google(audio, language="pt-BR").lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"⚠️ Erro API Google: {e}")
        return ""
    except Exception as e:
        print(f"❌ Erro transcrição: {e}")
        return ""

def process_audio():
    print(f"\n🔗 Conectado no IP: {TAPO_IP}")
    
    while True:
        print(f"\n💤 Aguardando '{WAKE_WORD}'...")
        capture_audio(4, "wake_word.wav")
        texto_espera = transcribe_audio("wake_word.wav")
        
        if texto_espera:
            print(f"👂 Você disse: '{texto_espera}'")
        else:
            time.sleep(1)
            continue
        
        palavras_gatilho = [WAKE_WORD, "umbrella", "um brel", "faixa", "taxa", "baixa", "kasha"]
        
        if any(gatilho in texto_espera for gatilho in palavras_gatilho):
            print("\n🔔 Palavra-chave detectada!")
            print("🟢 Escutando comando...")
            
            capture_audio(6, "comando.wav")
            comando = transcribe_audio("comando.wav")
            
            if comando:
                print(f"📝 Comando: '{comando}'")
                generate_and_play_response(comando)
            else:
                print("🔇 Não entendi o comando.")
                
            time.sleep(1)

if __name__ == "__main__":
    time.sleep(5) 
    generate_and_play_response("Teste de áudio um dois três") 
    process_audio()
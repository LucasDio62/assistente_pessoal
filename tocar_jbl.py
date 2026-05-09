import time
import os
import pygame

# Inicializa a placa de som do seu Windows (que está ligada na JBL)
pygame.mixer.init()
print("🎧 Conectado à JBL. Aguardando o Assistente (Docker) falar...")

while True:
    # Fica vigiando se o Docker criou o arquivo "falar.mp3"
    if os.path.exists("falar.mp3"):
        try:
            print("🔊 Reproduzindo áudio na JBL...")
            pygame.mixer.music.load("falar.mp3")
            pygame.mixer.music.play()
            
            # Espera a música terminar de tocar
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
                
            # Descarrega o arquivo da memória
            pygame.mixer.music.unload() 
            
            # Apaga o arquivo para não tocar a mesma coisa de novo
            os.remove("falar.mp3") 
            print("✅ Áudio finalizado. Aguardando próximo comando...")
            
        except Exception as e:
            print(f"❌ Erro ao tocar na JBL: {e}")
            
    # Pausa de meio segundo para não fritar o processador do Windows
    time.sleep(0.5)
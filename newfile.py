import pygame
import random
from datetime import datetime

# Inicializa o mixer de áudio
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

# --- FORÇAR MODO DEITADO ---
info = pygame.display.Info()
largura, altura = (info.current_h, info.current_w) if info.current_h > info.current_w else (info.current_w, info.current_h)

tela = pygame.display.set_mode((largura, altura))
relogio = pygame.time.Clock()

def tocar_som(tipo):
    try:
        if tipo == "tiro":
            som = pygame.mixer.Sound(buffer=bytes([int(127 * (1 + (i % 50 < 25))) for i in range(500)]))
            som.set_volume(0.1); som.play()
        elif tipo == "clique":
            som = pygame.mixer.Sound(buffer=bytes([int(127 * (1 + (i % 100 < 50))) for i in range(1000)]))
            som.set_volume(0.2); som.play()
    except: pass

# --- SISTEMA DE PATENTE E HISTÓRICO ---
def obter_patente(lvl):
    if lvl < 5: return "RECRUTA"
    elif lvl < 10: return "SOLDADO"
    elif lvl < 20: return "SARGENTO"
    elif lvl < 40: return "ELITE"
    elif lvl < 70: return "MESTRE"
    else: return "LENDÁRIO"

data_inicio = datetime.now().strftime("%d/%m/%Y")
level, exp_atual, exp_para_upar = 1, 0, 10 
abates_total, honra_total = 0, 0
exibir_perfil = False 
exibir_historico = False
avatar_equipado = "padrão" 

patente_atual = obter_patente(level)
historico_patentes = [{"nome": patente_atual, "data": data_inicio}]

jogando = False 
pos_player = [150, 480]
contador_abates_para_exp = 0 

# --- NUVENS E ESTRELAS ---
nuvens = [[random.randint(0, largura), random.randint(50, 150), random.uniform(0.5, 2)] for _ in range(5)]
estrelas = [[random.randint(0, largura), random.randint(0, 300)] for _ in range(50)]

fonte_ui = pygame.font.SysFont("Arial", 30, True)
fonte_mapa = pygame.font.SysFont("Arial", 50, True)
fonte_mini = pygame.font.SysFont("Arial", 25, True)
fonte_pequena = pygame.font.SysFont("Arial", 22, True)

pos_botao, raio_botao = (largura - 200, altura - 250), 85 

def criar_titulo_estilizado(texto, fonte, cor_texto, cor_borda):
    superficie_texto = fonte.render(texto, True, cor_texto)
    superficie_borda = fonte.render(texto, True, cor_borda)
    larg, alt = superficie_texto.get_size()
    temp_surf = pygame.Surface((larg + 4, alt + 4), pygame.SRCALPHA)
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        temp_surf.blit(superficie_borda, (2 + dx, dy + 2))
    temp_surf.blit(superficie_texto, (2, 2))
    return temp_surf

titulo_cache = criar_titulo_estilizado("PYDROID ISTREYC ROYALE", fonte_mapa, (255, 255, 255), (0, 0, 0))
legenda_mini = criar_titulo_estilizado("MINI MAPA", fonte_mini, (255, 255, 255), (0, 0, 0))
btn_iniciar = criar_titulo_estilizado("INICIAR JOGO", fonte_mapa, (255, 255, 255), (0, 0, 0))

bots = [[random.randint(600, 2500), random.randint(420, 560), random.randint(0,1), 100] for _ in range(8)]
balas, medalhas = [], [[random.randint(800, 4000), random.randint(420, 560)] for _ in range(25)] 

while True:
    relogio.tick(60) 
    
    # --- CENÁRIO (NÃO MEXER) ---
    for y in range(400):
        r = max(40, min(120, 40 + y // 5))
        g = max(20, min(40, 20 + y // 15))
        b = max(80, min(180, 180 - y // 3))
        pygame.draw.line(tela, (r, g, b), (0, y), (largura, y))
    
    for est in estrelas:
        pygame.draw.circle(tela, (255, 255, 255), est, 1)

    for n in nuvens:
        n[0] -= n[2]
        if n[0] < -150: n[0] = largura + 100
        pygame.draw.circle(tela, (200, 200, 220), (int(n[0]), n[1]), 30)
        pygame.draw.circle(tela, (200, 200, 220), (int(n[0])+25, n[1]+10), 25)
        pygame.draw.circle(tela, (200, 200, 220), (int(n[0])-25, n[1]+10), 25)

    pygame.draw.rect(tela, (34, 139, 34), (0, 400, largura, altura)) 

    clicando_tiro = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if not jogando:
                if largura//2 - 160 < mx < largura//2 + 160 and altura//2 - 40 < my < altura//2 + 40:
                    jogando = True; tocar_som("clique")
            else:
                if exibir_historico:
                    exibir_historico = False; tocar_som("clique"); continue
                
                # Clique no Perfil (Ajustado para não travar)
                if mx < 160 and my > altura - 80:
                    exibir_perfil = not exibir_perfil; tocar_som("clique")
                    continue
                
                if exibir_perfil:
                    # CLIQUE NO BOTÃO VER PATENTE (DENTRO DO PERFIL)
                    if 30 < mx < 230 and altura - 150 < my < altura - 110:
                        exibir_historico = True; tocar_som("clique")
                    # Clique nos Avatares (Lado direito)
                    if 380 < mx < 460 and altura - 450 < my < altura - 370:
                        avatar_equipado = "dourado"; tocar_som("clique")
                    if 475 < mx < 555 and altura - 450 < my < altura - 370:
                        avatar_equipado = "padrão"; tocar_som("clique")

                # Botão de Tiro
                dist_click = ((mx-pos_botao[0])**2 + (my-pos_botao[1])**2)**0.5
                if dist_click < raio_botao:
                    clicando_tiro = True
                    balas.append([pos_player[0]+50, pos_player[1]+20, 22, (255,255,255), True, -1])
                    tocar_som("tiro") 

        if jogando and not exibir_historico and event.type == pygame.MOUSEMOTION and event.buttons[0]:
            if not exibir_perfil: pos_player[1] = event.pos[1] - 25

    if not jogando:
        tela.blit(titulo_cache, (largura//2 - titulo_cache.get_width()//2, altura//3))
        pygame.draw.rect(tela, (50, 50, 50), (largura//2 - 160, altura//2 - 40, 320, 80), border_radius=15)
        tela.blit(btn_iniciar, (largura//2 - btn_iniciar.get_width()//2, altura//2 - 25))
    else:
        # --- MINI MAPA FUNCIONAL ---
        mx_m, my_m = largura - 150, 110
        pygame.draw.circle(tela, (255, 255, 255), (mx_m, my_m), 73, 2)
        pygame.draw.circle(tela, (0, 0, 0), (mx_m, my_m), 70)
        tela.blit(legenda_mini, (mx_m - 50, my_m - 100))
        # Ponto do Player no Mini Mapa
        pygame.draw.circle(tela, (0, 0, 255), (mx_m - 30, my_m + (pos_player[1]-480)//10), 4)

        for bot in bots:
            bot[0] -= 7
            if bot[0] < -200: bot[0] = largura + random.randint(200, 1500)
            cor = (255, 0, 0) if bot[2] == 0 else (255, 140, 0)
            
            # Ponto do Bot no Mini Mapa
            if 0 < bot[0] < largura:
                bx = mx_m - 70 + (bot[0] * 140 // largura)
                by = my_m - 70 + (bot[1] * 140 // altura)
                pygame.draw.circle(tela, (255, 0, 0), (int(bx), int(by)), 3)

            if random.random() < 0.03: 
                balas.append([bot[0], bot[1]+22, -15, (255, 255, 0), False, bot[2]])
                tocar_som("tiro")

            pygame.draw.rect(tela, (0, 0, 0), (bot[0]-15, bot[1]+20, 20, 8)) 
            pygame.draw.circle(tela, cor, (bot[0]+17, bot[1]+22), 22)
            pygame.draw.rect(tela, (255, 0, 0), (bot[0], bot[1]-12, 35, 5))
            pygame.draw.rect(tela, (0, 255, 0), (bot[0], bot[1]-12, 35 * (bot[3]/100), 5))
            
            if bot[3] <= 0: 
                abates_total += 1; contador_abates_para_exp += 1
                if contador_abates_para_exp >= 2:
                    exp_atual += 3; contador_abates_para_exp = 0
                    if exp_atual >= exp_para_upar: 
                        level += 1; exp_atual = 0; exp_para_upar += 5
                        patente_atual = obter_patente(level)
                        historico_patentes.append({"nome": patente_atual, "data": datetime.now().strftime("%d/%m/%Y")})
                bot[0] = largura + random.randint(500, 1500); bot[3] = 100

        for m in medalhas:
            m[0] -= 7
            pygame.draw.circle(tela, (255, 215, 0), (m[0], m[1]), 12)
            if (abs(pos_player[0] - m[0]) < 50 and abs(pos_player[1] - m[1]) < 50) or m[0] < -50:
                if m[0] > 0: honra_total += 1 
                m[0] = largura + random.randint(200, 2000); m[1] = random.randint(420, 560)

        for b in balas[:]:
            b[0] += b[2]
            if b[0] < -50 or b[0] > largura + 50: balas.remove(b); continue
            pygame.draw.line(tela, b[3], (b[0], b[1]), (b[0]+15, b[1]), 4)
            for t in bots:
                if b[4] and abs(b[0]-(t[0]+17)) < 30 and abs(b[1]-(t[1]+22)) < 30:
                    t[3] -= 34; balas.remove(b); break

        # --- UI PERFIL ---
        pygame.draw.rect(tela, (60, 60, 60), (10, altura - 70, 150, 50), border_radius=10)
        tela.blit(fonte_ui.render("PERFIL", True, (255, 255, 255)), (25, altura - 60))
        
        if exibir_perfil:
            # Painel do Perfil
            pygame.draw.rect(tela, (20, 20, 20), (10, altura - 520, 340, 440), border_radius=15)
            pygame.draw.rect(tela, (255, 255, 255), (10, altura - 520, 340, 440), 2, border_radius=15)
            
            # Avatar e Stats
            pygame.draw.rect(tela, (255, 255, 255), (30, altura - 505, 80, 80), 2, border_radius=10)
            if avatar_equipado == "dourado":
                pygame.draw.circle(tela, (255, 215, 0), (70, altura - 465), 30)
            else:
                tela.blit(fonte_ui.render("?", True, (100, 100, 100)), (60, altura - 485))

            tela.blit(fonte_ui.render(f"LVL: {level}", True, (255, 215, 0)), (130, altura - 500))
            tela.blit(fonte_pequena.render(f"PATENTE: {patente_atual}", True, (200, 200, 200)), (130, altura - 460))
            tela.blit(fonte_pequena.render(f"DESDE: {data_inicio}", True, (255, 255, 255)), (30, altura - 410))
            
            # Barra XP e Infos
            pygame.draw.rect(tela, (100, 100, 100), (30, altura - 370, 280, 12))
            pygame.draw.rect(tela, (255, 215, 0), (30, altura - 370, 280 * (exp_atual/exp_para_upar), 12))
            tela.blit(fonte_pequena.render(f"ABATES: {abates_total}", True, (0, 255, 0)), (30, altura - 340))
            tela.blit(fonte_pequena.render(f"HONRA: {honra_total}", True, (0, 191, 255)), (30, altura - 300))
            
            # BOTÃO VER PATENTE (DENTRO DO PERFIL)
            pygame.draw.rect(tela, (50, 50, 50), (30, altura - 150, 200, 40), border_radius=10)
            pygame.draw.rect(tela, (255, 255, 255), (30, altura - 150, 200, 40), 1, border_radius=10)
            tela.blit(fonte_pequena.render("VER PATENTE", True, (255, 255, 255)), (65, altura - 140))

            # Seção Avatares (Lado)
            pygame.draw.rect(tela, (30, 30, 30), (360, altura - 520, 216, 196), border_radius=15)
            pygame.draw.rect(tela, (255, 255, 255), (360, altura - 520, 216, 196), 2, border_radius=15)
            tela.blit(fonte_pequena.render("AVATARES", True, (200, 200, 200)), (420, altura - 510))
            pygame.draw.rect(tela, (255, 255, 255), (380, altura - 450, 80, 80), 2, border_radius=10)
            pygame.draw.circle(tela, (255, 215, 0), (420, altura - 410), 25)
            pygame.draw.rect(tela, (100, 100, 100), (475, altura - 450, 80, 80), 2, border_radius=10)
            tela.blit(fonte_mini.render("OFF", True, (100, 100, 100)), (495, altura - 425))

        if exibir_historico:
            pygame.draw.rect(tela, (10, 10, 10), (largura//2 - 300, 50, 600, altura - 100), border_radius=20)
            pygame.draw.rect(tela, (255, 255, 255), (largura//2 - 300, 50, 600, altura - 100), 3, border_radius=20)
            y_o = 130
            for item in historico_patentes:
                tela.blit(fonte_pequena.render(f"- {item['nome']} | {item['data']}", True, (255, 255, 255)), (largura//2 - 270, y_o))
                y_o += 40

        # Botão Tiro e Player
        pygame.draw.circle(tela, (255, 255, 255), pos_botao, raio_botao + 3) 
        pygame.draw.circle(tela, (100, 100, 100), pos_botao, raio_botao)
        pygame.draw.circle(tela, (200, 200, 200), pos_botao, 40 if not clicando_tiro else 25)
        
        pygame.draw.rect(tela, (0, 0, 0), (pos_player[0]+30, pos_player[1]+20, 25, 8)) 
        pygame.draw.circle(tela, (0, 0, 255), (pos_player[0]+22, pos_player[1]+25), 25)
        if avatar_equipado == "dourado":
             pygame.draw.circle(tela, (255, 215, 0), (pos_player[0]+22, pos_player[1]+25), 10)

    pygame.display.update()

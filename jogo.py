from PPlay.window import Window
from PPlay.gameimage import GameImage
from PPlay.sprite import Sprite
from PPlay.mouse import Mouse
from PPlay.keyboard import Keyboard
from PPlay.collision import Collision
from PPlay.sound import *
import random
import datetime

import datetime

RANKING_FILE = "ranking.txt"

def salvar_ranking(nome, tempo_jogo_segundos):
    """Salva o nome, a pontuação e o tempo de jogo no arquivo de ranking."""
    data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(RANKING_FILE, "a") as arquivo:
        arquivo.write(f"{nome},{tempo_jogo_segundos},{data_atual}\n")
        
def exibir_ranking(janela):
    """Exibe os 5 melhores jogadores salvos no arquivo de ranking, ordenados pelo menor tempo jogado."""
    janela = Window(840, 620)
    janela.set_title("Ranking")
    fundo = Sprite("fundos/fundoranking.jpg")
    try:
        with open(RANKING_FILE, "r") as arquivo:
            linhas = arquivo.readlines()
    except FileNotFoundError:
        linhas = []

    ranking = []
    for linha in linhas:
        dados = linha.strip().split(",")
        if len(dados) == 3:
            nome, tempo_jogo_segundos, data = dados
            try:
                tempo_jogo_segundos = tempo_jogo_segundos.strip().replace(']', '').replace('[', '')
                tempo_jogo_segundos = float(tempo_jogo_segundos)
                ranking.append([nome, tempo_jogo_segundos, data])
            except ValueError:
                print(f"Erro ao converter o tempo de jogo para float: {tempo_jogo_segundos}")
        else:
            print(f"Dados inválidos: {linha}")

    ranking = sorted(ranking, key=lambda x: x[1])[:5]
    fundo.draw()
    janela.update()
    janela.draw_text("Ranking - Top 5", janela.width // 2 - 100, 50, size=30, color=(47,79,79), font_name= "Rockwell", bold=False,)
    y_pos = 100
    for i, (nome, tempo_jogo_segundos, data) in enumerate(ranking, start=1):
        minutos = int(tempo_jogo_segundos // 60)
        segundos = int(tempo_jogo_segundos % 60)
        texto = f"{i}. {nome} - venceu em {minutos:02d} min. e {segundos:02d} segundos - {data}"
        janela.draw_text(texto, 50, y_pos, size=20, color=(47,79,79), font_name="Rockwell")
        y_pos += 40

    janela.draw_text("Pressione ESC para voltar", 50, y_pos + 40, size=20, color=(47,79,79), font_name="Rockwell")
    while True:
        janela.update()
        if janela.get_keyboard().key_pressed("ESC"):
            mostrar_menu()

def jogar_jogo():    
    janela = Window(600, 360)
    janela.set_title("Zombie Attack")
    
    fim1 = GameImage("fundos/fimtiros.jpg")
    fim2 = GameImage("fundos/fimvidas.jpg")
    fim3 = GameImage("fundos/fimmonstros.jpg")
    background = GameImage("fundos/back.jpg")
    gamewon = GameImage("fundos/gamewon.jpg")
    fase2 = GameImage("fundos/fase2.jpg")
    obstaculo = GameImage("icons/caixa_obstaculo2.png")

    obstaculo_x = random.choice([100,200,300,400])
    obstaculo_y = (janela.height / 2.2) + obstaculo.height + 4.5

    obstaculo.set_position(obstaculo_x,  obstaculo_y)

    somtiro = Sound("sounds/tiro.ogg")
    somdead = Sound("sounds/dead.ogg")
    somdano = Sound("sounds/dano.ogg")
    somfase = Sound("sounds/nextlevel.ogg")
    somdeath = Sound("sounds/death.ogg")

    player_right = Sprite("icons/player_redimensionado.png")
    player_left = Sprite("icons/cpleft.png")
    player = player_right
    player_left.set_position((janela.width) / 4, ((janela.height) / 2.2) + player.height - 5)
    player_right.set_position((janela.width) / 4, ((janela.height) / 2.2) + player.height - 5)
    player_initial_y = player.y

    tot_inimigos = 0

    enemy_image = "icons/enemyweak.png"

    teclado = Keyboard()

    scoreboard = [0, 0]
    quant_vidas = 4 
    quant_tiros = 15
    bullets = []
    tempo_recarga_bala = 0.5
    ultimo_tiro = 0 
    fase = 1
    direcao = 0
    is_jumping = False
    jump_speed = -250 
    gravity = 500 
    vertical_speed = 0 

    enemy_spawn_time = 2.5
    last_enemy_spawn_time = 0
    enemies = []

    def draw_life():
        janela.draw_text(f"Vidas: {quant_vidas}", janela.width - 90, 10, size=20, color=(210,105,30), font_name="Arial", bold=True)

    def draw_phase():
        janela.draw_text(f"fase: {fase}", janela.width // 8 - 60, 10, size=20, color=(0,0,205), font_name="Arial", bold=True)

    def inverter_sentido(enemy, sentido):
        enemy.x -= sentido
        return sentido

    def verificar_colisao_inimigo(enemy, dt):

        sentido = 100 * dt * enemy.direction 

        if Collision.collided(enemy, obstaculo):
            enemy.direction = -enemy.direction
            if enemy.direction == 1:
                enemy.x = obstaculo.x + obstaculo.width + 1
            elif enemy.direction == -1:
                enemy.x = obstaculo.x - enemy.width - 1

        enemy.x += sentido

        if enemy.x <= 0 or enemy.x + enemy.width >= janela.width:
            enemy.direction = -enemy.direction
            if enemy.x <= 0:
                enemy.x = 0
            elif enemy.x + enemy.width >= janela.width:
                enemy.x = janela.width - enemy.width

    while True:
        janela.update()
        dt = janela.delta_time()

        background.draw()
        draw_phase()
        draw_life()

        tempo_jogo_ms = janela.time_elapsed()
        tempo_jogo_segundos = tempo_jogo_ms / 1000

        minutos = int(tempo_jogo_segundos // 60)
        segundos = int(tempo_jogo_segundos % 60)

        janela.draw_text(f'{minutos:02d}:{segundos:02d}', janela.width // 8 - 60, 30, size=20, color=(75,0,130), font_name="Arial", bold=True)

        if teclado.key_pressed("LEFT"):
            direcao = 1
            current_x = player.x
            current_y = player.y  
            player = player_left  
            player.x = current_x  
            player.y = current_y
            player.x -= 200 * dt
            if Collision.collided(player, obstaculo):
                player.x = obstaculo.x + obstaculo.width
        elif teclado.key_pressed("RIGHT"):
            direcao = 2
            current_x = player.x  
            current_y = player.y  
            player = player_right  
            player.x = current_x
            player.y = current_y
            player.x += 200 * dt 
            if Collision.collided(player, obstaculo):
                player.x = obstaculo.x - player.width

        if teclado.key_pressed("SPACE") and not is_jumping:
            is_jumping = True
            vertical_speed = jump_speed

        if is_jumping:
            player.y += vertical_speed * dt
            vertical_speed += gravity * dt 
            if Collision.collided(player, obstaculo):
                if vertical_speed < 0:
                    player.y = obstaculo.y + obstaculo.height
                    vertical_speed = 0
                elif vertical_speed > 0:
                    player.y = obstaculo.y - player.height
                    vertical_speed = 0
            if player.y >= player_initial_y:
                player.y = player_initial_y
                is_jumping = False

        if len(enemies) < 8 and janela.time_elapsed() - last_enemy_spawn_time >= enemy_spawn_time * 1000:
            new_enemy = Sprite(enemy_image)
            random_height = random.randint(120,200)
            new_enemy.set_position(janela.width, random_height)
            new_enemy.direction = -1 
            enemies.append(new_enemy)
            last_enemy_spawn_time = janela.time_elapsed()

        enemies_to_remove = []

        for enemy in enemies:
            verificar_colisao_inimigo(enemy, dt)
            enemy.draw()
            if enemy.x + enemy.width < 0:
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            enemies.remove(enemy)

        for enemy in enemies:
            if Collision.collided(player, enemy):
                somdano.play()
                tot_inimigos += 1
                quant_vidas -= 1
                enemy.set_position(-100, -100)

        bullet = Sprite("icons/bullet.png")
        bullet.speed = 300
        bullet.set_position(player.x + player.width, player.y + (player.height / 2) - (bullet.height / 2))

        if teclado.key_pressed("F") and janela.time_elapsed() - ultimo_tiro >= tempo_recarga_bala * 1000:
            somtiro.play()
            quant_tiros -= 1
            if direcao == 2:
                bullet.set_position(player.x + player.width, player.y + (player.height / 2) - (bullet.height / 2))
                bullet.speed = 300  
            elif direcao == 1:  
                bullet.set_position(player.x - bullet.width, player.y + (player.height / 2) - (bullet.height / 2))
                bullet.speed = -300  
            bullets.append(bullet)
            ultimo_tiro = janela.time_elapsed()  

        bullets_to_remove = []

        for bullet in bullets:
            bullet.x += bullet.speed * dt  
            bullet.draw()
            if bullet.x > janela.width:
                bullets_to_remove.append(bullet)
            if Collision.collided(bullet, obstaculo):
                bullets_to_remove.append(bullet)
                bullet.set_position(-100,-100)

        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        for bullet in bullets:
            for enemy in enemies:
                if Collision.collided(bullet, enemy):
                    somdead.play()
                    tot_inimigos += 1
                    scoreboard[0] += 1
                    bullets_to_remove.append(bullet)  
                    enemy.set_position(-100, -100) 

        for bullet in bullets_to_remove:
            if bullet in bullets:
                bullets.remove(bullet)

        if quant_tiros <= 0:
            somdeath.play()
            fim1.draw()           
            janela.update()
            while True:
                janela.update()
                if janela.get_keyboard().key_pressed("ENTER"):
                    mostrar_menu()
                elif janela.get_keyboard().key_pressed("ESC"):
                    janela.close()
        elif quant_vidas <= 0:
            somdeath.play()
            fim2.draw()           
            janela.update()
            while True:
                janela.update()
                if janela.get_keyboard().key_pressed("ENTER"):
                    mostrar_menu()
                elif janela.get_keyboard().key_pressed("ESC"):
                    janela.close()
        elif tot_inimigos==8 and scoreboard[0] != 6:
            somdeath.play()
            fim3.draw()   
            janela.draw_text(f'{tot_inimigos} surgiram, você matou apenas {scoreboard[0]} :(', 180, 320, size=20, color=(0,0,0), font_name="Arial", bold=True)           
            janela.update()
            while True:
                janela.update()
                if janela.get_keyboard().key_pressed("ENTER"):
                    mostrar_menu()
                elif janela.get_keyboard().key_pressed("ESC"):
                    janela.close()
    
        player.draw()
        obstaculo.draw()

        janela.draw_text(f'kills: {scoreboard[0]}', 280, 20, size=20, color=(128,0,0), font_name="Rockwell", bold=True)
        janela.draw_text(f'Tiros: {quant_tiros}', janela.width - 90, 30, size=20, color=(139,69,19), font_name="Arial", bold=True)
        janela.draw_text(f'Elimine 6 monstros', 240, 0, size=20, color=(128,0,0), font_name="Arial", bold=True)
        
        if scoreboard[0] == 6:
            fase2.draw()
            somfase.play()           
            janela.draw_text(f'FASE 2', janela.width / 2.70, janela.height / 2.5 , size=50, color=(0, 0, 0), font_name="Rockwell", bold=True, italic=True)
            janela.update()
            janela.delay(4000)
            jogar_fase2()

def jogar_fase2(fase=2, quant_inimigos = 10, enemy_spawn_time = 2.5, deaths = 6 ):
    janela = Window(600, 360)
    janela.set_title("Zombie Attack")
    
    fim1 = GameImage("fundos/fimtiros.jpg")
    fim2 = GameImage("fundos/fimvidas.jpg")
    fim3 = GameImage("fundos/fimmonstros.jpg")
    background = GameImage("fundos/back.jpg")
    gamewon = GameImage("fundos/gamewon.jpg")
    fase2 = GameImage("fundos/fase2.jpg")
    obstaculo = GameImage("icons/caixa_obstaculo2.png")

    obstaculo_x = random.choice([100,200,300,400])
    obstaculo_y = (janela.height / 2.2) + obstaculo.height + 4.5
    obstaculo.set_position(obstaculo_x,  obstaculo_y)
   
    somtiro = Sound("sounds/tiro.ogg")
    somdead = Sound("sounds/dead.ogg")
    somdano = Sound("sounds/dano.ogg")
    somfase = Sound("sounds/nextlevel.ogg")
    somdeath = Sound("sounds/death.ogg")
    won = Sound("sounds/victory.ogg")

    player_right = Sprite("icons/player_redimensionado.png")
    player_left = Sprite("icons/cpleft.png")
    player = player_right
    player_left.set_position((janela.width) / 4, ((janela.height) / 2.2) + player.height - 5)
    player_right.set_position((janela.width) / 4, ((janela.height) / 2.2) + player.height - 5)
    player_initial_y = player.y

    tot_inimigos = 0

    enemy_image = "icons/enemyweak.png"

    teclado = Keyboard()

    scoreboard = [0, 0]
    quant_vidas = 4
    quant_tiros = 15
    bullets = []
    tempo_recarga_bala = 0.5
    ultimo_tiro = 0
    direcao = 0
    is_jumping = False
    jump_speed = -250  
    gravity = 500  
    vertical_speed = 0
    last_enemy_spawn_time = 0  
    enemies = []

    def draw_life():
        janela.draw_text(f"Vidas: {quant_vidas}", janela.width - 90, 10, size=20, color=(210,105,30), font_name="Arial", bold=True)

    def draw_phase():
        janela.draw_text(f"fase: {fase}", janela.width // 8 - 60, 10, size=20, color=(0,0,205), font_name="Arial", bold=True)

    def inverter_sentido(enemy, sentido):
        enemy.x -= sentido
        return sentido

    def verificar_colisao_inimigo(enemy, dt):

        sentido = 100 * dt * enemy.direction 
        if Collision.collided(enemy, obstaculo):
            enemy.direction = -enemy.direction
            if enemy.direction == 1:
                enemy.x = obstaculo.x + obstaculo.width + 1
            elif enemy.direction == -1:
                enemy.x = obstaculo.x - enemy.width - 1

        enemy.x += sentido

        if enemy.x <= 0:
            enemy.x = janela.width - enemy.width 
        elif enemy.x + enemy.width >= janela.width:
            enemy.x = 0 

        enemy.x += sentido

        if enemy.x <= 0 or enemy.x + enemy.width >= janela.width:
            enemy.direction = -enemy.direction
            
            if enemy.x <= 0:
                enemy.x = 0  
            elif enemy.x + enemy.width >= janela.width:
                enemy.x = janela.width - enemy.width  
            
    while True:
        janela.update()
        dt = janela.delta_time()

        background.draw()
        draw_phase()
        draw_life()

        tempo_jogo_ms = janela.time_elapsed()
        tempo_jogo_segundos = tempo_jogo_ms / 1000

        minutos = int(tempo_jogo_segundos // 60)
        segundos = int(tempo_jogo_segundos % 60)

        janela.draw_text(f'{minutos:02d}:{segundos:02d}', janela.width // 8 - 60, 30, size=20, color=(75,0,130), font_name="Arial", bold=True)

        if teclado.key_pressed("LEFT"):
            direcao = 1
            current_x = player.x  
            current_y = player.y  
            player = player_left  
            player.x = current_x
            player.y = current_y
            player.x -= 200 * dt
            if Collision.collided(player, obstaculo):
                player.x = obstaculo.x + obstaculo.width
        elif teclado.key_pressed("RIGHT"):
            direcao = 2
            current_x = player.x  
            current_y = player.y 
            player = player_right 
            player.x = current_x 
            player.y = current_y
            player.x += 200 * dt  
            if Collision.collided(player, obstaculo):
                player.x = obstaculo.x - player.width  

        if teclado.key_pressed("SPACE") and not is_jumping:
            is_jumping = True
            vertical_speed = jump_speed

        if is_jumping:
            player.y += vertical_speed * dt
            vertical_speed += gravity * dt
            if Collision.collided(player, obstaculo):
                if vertical_speed < 0:
                    player.y = obstaculo.y + obstaculo.height
                    vertical_speed = 0
                elif vertical_speed > 0:
                    player.y = obstaculo.y - player.height 
                    vertical_speed = 0  
            if player.y >= player_initial_y:
                player.y = player_initial_y
                is_jumping = False

        if len(enemies) < quant_inimigos and janela.time_elapsed() - last_enemy_spawn_time >= enemy_spawn_time * 1000:
            new_enemy = Sprite(enemy_image)
            random_height = random.randint(120,200)
            new_enemy.set_position(janela.width, random_height)
            new_enemy.direction = -1 
            enemies.append(new_enemy) 
            last_enemy_spawn_time = janela.time_elapsed()

        enemies_to_remove = [] 

        for enemy in enemies:
            verificar_colisao_inimigo(enemy, dt) 
            enemy.draw()
            if enemy.x + enemy.width < 0:
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            tot_inimigos += 1
            enemies.remove(enemy)

        for enemy in enemies:
            if Collision.collided(player, enemy):
                if player.y + player.height <= obstaculo.y and player.x + player.width > obstaculo.x and player.x < obstaculo.x + obstaculo.width:
                    tot_inimigos += 1
                    enemy.set_position(-100,-100)
                else:
                    somdano.play()
                    tot_inimigos += 1
                    quant_vidas -= 1
                    enemy.set_position(-100, -100)

        bullet = Sprite("icons/bullet.png")
        bullet.speed = 300
        bullet.set_position(player.x + player.width, player.y + (player.height / 2) - (bullet.height / 2))

        if teclado.key_pressed("F") and janela.time_elapsed() - ultimo_tiro >= tempo_recarga_bala * 1000:
            somtiro.play()
            quant_tiros -= 1
            if direcao == 2: 
                bullet.set_position(player.x + player.width, player.y + (player.height / 2) - (bullet.height / 2))
                bullet.speed = 300 
            elif direcao == 1:
                bullet.set_position(player.x - bullet.width, player.y + (player.height / 2) - (bullet.height / 2))
                bullet.speed = -300 
            bullets.append(bullet)
            ultimo_tiro = janela.time_elapsed()

        bullets_to_remove = []

        for bullet in bullets:
            bullet.x += bullet.speed * dt 
            bullet.draw()
            if bullet.x > janela.width:
                bullets_to_remove.append(bullet)
            if Collision.collided(bullet, obstaculo):
                bullets_to_remove.append(bullet)
                bullet.set_position(-100,-100)

        for bullet in bullets_to_remove:
            bullets.remove(bullet)

        for bullet in bullets:
            for enemy in enemies:
                if Collision.collided(bullet, enemy):
                    somdead.play()
                    tot_inimigos += 1
                    scoreboard[0] += 1
                    bullets_to_remove.append(bullet)
                    enemy.set_position(-100, -100)

        for bullet in bullets_to_remove:
            if bullet in bullets:
                bullets.remove(bullet)

        if quant_tiros <= 0:
            somdeath.play()
            fim1.draw()           
            janela.update()
            while True:
                janela.update()
                if janela.get_keyboard().key_pressed("ENTER"):
                    mostrar_menu()
                elif janela.get_keyboard().key_pressed("ESC"):
                    janela.close()
        elif quant_vidas <= 0:
            somdeath.play()
            fim2.draw()           
            janela.update()
            while True:
                janela.update()
                if janela.get_keyboard().key_pressed("ENTER"):
                    mostrar_menu()
                elif janela.get_keyboard().key_pressed("ESC"):
                    janela.close()
        elif tot_inimigos==(quant_inimigos) and scoreboard[0] != deaths:
            somdeath.play()
            fim3.draw()
            janela.draw_text(f'{tot_inimigos} surgiram, você matou apenas {scoreboard[0]} :(', 180, 320, size=20, color=(0,0,0), font_name="Arial", bold=True)           
            janela.update()
            while True:
                janela.update()
                if janela.get_keyboard().key_pressed("ENTER"):
                    mostrar_menu()
                elif janela.get_keyboard().key_pressed("ESC"):
                    janela.close()

        player.draw()
        obstaculo.draw()

        if scoreboard[0] == deaths:
            fase += 1
            quant_inimigos += 2
            enemy_spawn_time -= 0.6
            deaths = 6
            if fase > 5:
                won.play()
                gamewon.draw()
                janela.update()
                janela.delay(2000)
                print("Fim de jogo!")
                nome = input("Digite seu nome: ")
                salvar_ranking(nome, tempo_jogo_segundos)
                janela.close()
            fase2.draw()
            somfase.play()
            janela.draw_text(f'FASE {fase}', janela.width / 2.70, janela.height / 2.5 , size=50, color=(0, 0, 0), font_name="Rockwell", bold=True, italic=True)
            janela.update()
            janela.delay(5000)
            jogar_fase2(fase,quant_inimigos,enemy_spawn_time, deaths)

        janela.draw_text(f'kills: {scoreboard[0]}', 280, 20, size=20, color=(128,0,0), font_name="Rockwell", bold=True)        
        janela.draw_text(f'Tiros: {quant_tiros}', janela.width - 90, 30, size=20, color=(139,69,19), font_name="Arial", bold=True)
        janela.draw_text('Elimine 6 monstros', 240, 0, size=20, color=(128,0,0), font_name="Arial", bold=True)
        
def mostrar_menu():
    janela = Window(840, 620)
    janela.set_title("Menu Principal")

    menus = Sound("sounds/loop.ogg")
    menus.loop = True
    menus.play()

    instrucoes = GameImage("fundos/fundoinstrucoes.jpg")

    fundo_menu = Sprite("fundos/fundomenu.jpg")
    logo = Sprite("icons/logo.png")
    logo.x = 280
    logo.y = 100

    jogar = Sprite("icons/jogar.png")
    jogar.x = 100
    jogar.y = 300

    ranking = Sprite("icons/ranking.png")
    ranking.x = 500
    ranking.y = 300

    sair = Sprite("icons/sair.png")
    sair.x = 300
    sair.y = 400

    mouse = Mouse()
    teclado = Keyboard()

    while True:
        fundo_menu.draw() 

        jogar.draw()
        ranking.draw()
        logo.draw()
        sair.draw()

        mouse_x, mouse_y = mouse.get_position()

        if mouse.is_button_pressed(1): 
            if dentro_do_botao(jogar, mouse_x, mouse_y):
                instrucoes.draw()
                janela.update()
                while True:
                    janela.update()
                    if janela.get_keyboard().key_pressed("ENTER"):
                        menus.stop()
                        jogar_jogo() 
            elif dentro_do_botao(ranking, mouse_x, mouse_y):
                menus.stop()
                exibir_ranking(janela)
            elif dentro_do_botao(sair, mouse_x, mouse_y):
                janela.close()

        janela.update()

def dentro_do_botao(botao, mouse_x, mouse_y):
    if botao.x <= mouse_x <= botao.x + botao.width and botao.y <= mouse_y <= botao.y + botao.height:
        return True
    return False

def main():
    mostrar_menu()

main()
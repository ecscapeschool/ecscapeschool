import pygame
import sys
import time
import os
import random
import math

# --- INITIALIZATION ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape School: Final Mission")
clock = pygame.time.Clock()

# Ensure the script looks for images in its own directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# --- COLORS ---
WHITE, BLACK, BLUE, YELLOW, RED, GREEN, ORANGE, GRAY, BROWN = (255, 255, 255), (0, 0, 0), (0, 0, 150), (255, 255, 0), (200, 0, 0), (0, 150, 0), (255, 140, 0), (150, 150, 150), (100, 50, 20)
font = pygame.font.SysFont("Arial", 22, bold=True)
title_font = pygame.font.SysFont("Arial", 32, bold=True)

# --- LANGUAGE SYSTEM ---
lang_idx = 0 
langs = ["EN", "SK"]
texts = {
    "EN": {"start": "START", "settings": "SETTINGS", "back": "BACK", "loc": "Room", "books": "Books", "keys": "Keys", "win": "YOU WIN!", "go": "GAME OVER (R to Restart)", "lang": "Lang", "rooms": ["Classroom", "Hall", "Back Hall", "Dining Room", "Field", "1st Floor", "Garden"]},
    "SK": {"start": "ŠTART", "settings": "NASTAVENIA", "back": "SPÄŤ", "loc": "Miestnosť", "books": "Zošity", "keys": "Kľúče", "win": "VÝHRA!", "go": "KONIEC HRY (R pre Restart)", "lang": "Jazyk", "rooms": ["Trieda", "Chodba", "Zadná chodba", "Jedáleň", "Dvor", "1. Poschodie", "Záhrada"]}
}

# --- IMAGE LOADING FUNCTION ---
def load_img(name, size, fallback_col=RED):
    if os.path.exists(name):
        try:
            # .convert_alpha() is essential for PNG transparency
            img = pygame.image.load(name).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception as e:
            print(f"Error loading {name}: {e}")
    
    # Fallback if image is missing
    s = pygame.Surface(size)
    s.fill(fallback_col)
    pygame.draw.rect(s, BLACK, (0, 0, size[0], size[1]), 2)
    return s

def loading_screen():
    assets_def = [
        ("player.png", (50, 70), BLUE), ("book.png", (30, 30), YELLOW), ("table.png", (100, 60), BROWN),
        ("chair.png", (45, 45), GRAY), ("locker.png", (55, 90), GRAY), ("desk.png", (100, 60), BROWN),
        ("door.png", (60, 90), BROWN), ("house.png", (200, 200), GREEN), ("fence.png", (200, 80), BLACK),
        ("exit.png", (60, 60), GREEN), ("kuchyna.png", (150, 100), GRAY), ("teacher.png", (60, 90), RED),
        ("ruler.png", (40, 10), YELLOW), ("keys.png", (35, 35), YELLOW)
    ]
    loaded = []
    for i, (name, size, col) in enumerate(assets_def):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        screen.fill(BLUE)
        progress = int(((i + 1) / len(assets_def)) * 100)
        screen.blit(title_font.render(f"LOADING: {progress}%", True, BLACK), (WIDTH//2-100, HEIGHT//2-50))
        pygame.draw.rect(screen, BLACK, (200, HEIGHT//2+20, 400, 30), 2)
        pygame.draw.rect(screen, GREEN, (202, HEIGHT//2+22, int(396 * (progress/100)), 26))
        pygame.display.flip()
        time.sleep(0.05)
        loaded.append(load_img(name, size, col))
    return loaded

# Load all assets
p_img, b_img, table_img, c_img, l_img, d_img, door_img, house_img, fence_img, exit_img, kitchen_img, t_img, ruler_img, keys_img = loading_screen()

# --- VARIABLES ---
keys_map = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "jump": pygame.K_SPACE}
setting_target = None
game_state = "MENU"
room_id = 1
player_rect = p_img.get_rect(center=(400, 500))
player_speed = 6
notebook_count, keys_found = 0, 0
is_jumping, jump_count, p_offset = False, 10, 0
timer_started, start_ticks, time_limit = False, 0, 60
is_hidden = False
player_hp = 3
max_hp = 3
invincible_until = 0 

# Basketball
basketball_score = 0
hoop_rect = pygame.Rect(350, 180, 100, 10)
balls = [{"rect": pygame.Rect(200 + i*300, 500, 24, 24), "vel_y": 0, "carried": False, "scored": False} for i in range(2)]
teacher_rect = t_img.get_rect(topleft=(-200, -200))
teacher_speed = 1.6
teacher_room = 0 

# Objects
stairs_rect = pygame.Rect(340, 530, 120, 70)
door_rect = door_img.get_rect(topleft=(100, 100))
house_rect = house_img.get_rect(center=(600, 150))
fence_barrier = pygame.Rect(0, 380, 800, 20)
desks = [pygame.Rect(100+s*250, 250+r*150, 100, 60) for r in range(2) for s in range(3)]
hall_lockers = [pygame.Rect(50+i*150, 50, 55, 90) for i in range(5)]
notebooks = [{"rect": pygame.Rect(random.randint(100,700), random.randint(100,500), 30, 30), "room": random.randint(1,4)} for _ in range(7)]
keys_list = [{"rect": pygame.Rect(random.randint(50,700), random.randint(50,450), 35, 35), "room": random.randint(1,4)} for _ in range(3)]

# --- MAIN LOOP ---
running = True
while running:
    mx, my = pygame.mouse.get_pos()
    cur = texts[langs[lang_idx]]
    current_time = pygame.time.get_ticks()

    if game_state == "PLAY":
        if room_id == 1: screen.fill((139, 69, 19))
        elif room_id == 2: screen.fill((100, 100, 100))
        elif room_id == 4: screen.fill((160, 80, 40))
        elif room_id == 5: screen.fill((20, 100, 20))
        elif room_id == 6: screen.fill((50, 50, 120))
        elif room_id == 7: screen.fill((30, 120, 30))
        else: screen.fill(GRAY)
    else: screen.fill(BLUE)

    if game_state == "MENU":
        instr = ["W,A,S,D: Move", "Space: Jump", "E: Interact / Hide", "3 Hits = Game Over", "Get 7 Books -> 3 Keys -> Floor 1 Exit"]
        for i, line in enumerate(instr): screen.blit(font.render(line, True, WHITE), (50, 50+i*30))
        pygame.draw.rect(screen, GREEN, (300, 300, 200, 50))
        pygame.draw.rect(screen, GRAY, (300, 370, 200, 50))
        screen.blit(font.render(cur["start"], True, BLACK), (350, 312))
        screen.blit(font.render(cur["settings"], True, BLACK), (340, 382))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and 300<mx<500:
                if 300<my<350: game_state = "PLAY"
                if 370<my<420: game_state = "SETTINGS"

    elif game_state == "SETTINGS":
        y_s = 100
        for action, key in keys_map.items():
            c = YELLOW if setting_target == action else WHITE
            pygame.draw.rect(screen, GRAY, (280, y_s, 240, 35))
            screen.blit(font.render(f"{action.upper()}: {pygame.key.name(key)}", True, c), (300, y_s+5))
            y_s += 45
        pygame.draw.rect(screen, ORANGE, (280, 400, 240, 45))
        screen.blit(font.render(f"{cur['lang']}: {langs[lang_idx]}", True, BLACK), (340, 412))
        pygame.draw.rect(screen, RED, (280, 470, 240, 45))
        screen.blit(font.render(cur["back"], True, WHITE), (360, 482))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if 280<mx<520:
                    y2 = 100
                    for action in keys_map:
                        if y2<my<y2+35: setting_target = action
                        y2 += 45
                    if 400<my<445: lang_idx = (lang_idx + 1) % 2
                    if 470<my<515: game_state = "MENU"
            if event.type == pygame.KEYDOWN and setting_target:
                keys_map[setting_target] = event.key; setting_target = None

    elif game_state == "PLAY":
        if room_id == 1:
            for d in desks: screen.blit(c_img, (d.x+25, d.y-45)); screen.blit(d_img, d)
        elif room_id == 2:
            for l in hall_lockers: screen.blit(l_img, l)
            pygame.draw.rect(screen, (50, 50, 50), stairs_rect)
        elif room_id == 4:
            screen.blit(kitchen_img, (325, 50))
            for d in desks: screen.blit(table_img, d)
        elif room_id == 5:
            pygame.draw.rect(screen, WHITE, (340, 100, 120, 90)); pygame.draw.rect(screen, RED, hoop_rect)
            pygame.draw.line(screen, BLACK, (400, 190), (400, 600), 8)
            for b in balls:
                if b["carried"]: b["rect"].center = (player_rect.centerx, player_rect.top)
                else:
                    b["vel_y"] += 0.7; b["rect"].y += b["vel_y"]
                    if b["rect"].bottom > 580: b["rect"].bottom = 580; b["vel_y"] *= -0.6
                    if b["rect"].colliderect(hoop_rect) and b["vel_y"] > 0 and not b["scored"]:
                        basketball_score += 1; b["scored"] = True
                pygame.draw.circle(screen, ORANGE, b["rect"].center, 12)
        elif room_id == 6:
            pygame.draw.rect(screen, (50, 50, 50), stairs_rect); screen.blit(door_img, door_rect)
        elif room_id == 7:
            screen.blit(house_img, house_rect)
            for x in range(0, 800, 200): screen.blit(fence_img, (x, 380))

        if notebook_count >= 5:
            if teacher_room != room_id:
                teacher_room = room_id
                side = random.randint(0, 3)
                if side == 0: teacher_rect.topleft = (-50, random.randint(0, HEIGHT))
                elif side == 1: teacher_rect.topleft = (WIDTH + 50, random.randint(0, HEIGHT))
                elif side == 2: teacher_rect.topleft = (random.randint(0, WIDTH), -50)
                else: teacher_rect.topleft = (random.randint(0, WIDTH), HEIGHT + 50)

            if not is_hidden:
                if teacher_rect.x < player_rect.x: teacher_rect.x += teacher_speed
                elif teacher_rect.x > player_rect.x: teacher_rect.x -= teacher_speed
                if teacher_rect.y < player_rect.y: teacher_rect.y += teacher_speed
                elif teacher_rect.y > player_rect.y: teacher_rect.y -= teacher_speed
            
            screen.blit(t_img, teacher_rect)
            swing_angle = math.sin(current_time * 0.015) * 60
            rotated_ruler = pygame.transform.rotate(ruler_img, swing_angle)
            screen.blit(rotated_ruler, (teacher_rect.centerx, teacher_rect.centery))

            if teacher_rect.colliderect(player_rect) and not is_hidden:
                if current_time > invincible_until:
                    player_hp -= 1
                    invincible_until = current_time + 1500 
                    if player_hp <= 0: game_state = "GAMEOVER"
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if room_id == 2:
                        for l in hall_lockers:
                            if player_rect.colliderect(l): is_hidden = not is_hidden
                    if not is_hidden:
                        if room_id == 2 and player_rect.colliderect(stairs_rect): room_id = 6; player_rect.y = 450
                        elif room_id == 6 and player_rect.colliderect(stairs_rect): room_id = 2; player_rect.y = 450
                        elif room_id == 6 and player_rect.colliderect(door_rect) and keys_found >= 3:
                            room_id = 7; player_rect.y = 500
                        for nb in notebooks[:]:
                            if player_rect.colliderect(nb["rect"]) and nb["room"] == room_id:
                                notebooks.remove(nb); notebook_count += 1
                                if notebook_count == 1: timer_started = True; start_ticks = current_time
                        if notebook_count >= 7:
                            for k in keys_list[:]:
                                if player_rect.colliderect(k["rect"]) and k["room"] == room_id:
                                    keys_list.remove(k); keys_found += 1
                if event.key == pygame.K_g and room_id == 5:
                    for b in balls:
                        if b["carried"]: b["carried"] = False; b["vel_y"] = -16; break
                        elif player_rect.colliderect(b["rect"]): b["carried"] = True; b["scored"] = False; break
                if event.key == keys_map["jump"] and not is_jumping: is_jumping = True

        if not is_hidden:
            keys = pygame.key.get_pressed()
            nx, ny = player_rect.x, player_rect.y
            if keys[keys_map["left"]]: nx -= player_speed
            if keys[keys_map["right"]]: nx += player_speed
            if keys[keys_map["up"]]: ny -= player_speed
            if keys[keys_map["down"]]: ny += player_speed
            
            tr = pygame.Rect(nx, ny, player_rect.width, player_rect.height)
            can_move = True
            if room_id == 7 and tr.colliderect(fence_barrier):
                if p_offset < 30: can_move = False
            if can_move: player_rect.x, player_rect.y = nx, ny

        if is_jumping:
            if jump_count >= -10:
                p_offset = (jump_count**2) * 0.5 * (1 if jump_count > 0 else -1)
                jump_count -= 1
            else: is_jumping = False; jump_count = 10; p_offset = 0

        if player_rect.right > WIDTH and room_id < 5: room_id += 1; player_rect.left = 10
        elif player_rect.left < 0 and room_id > 1 and room_id not in [6, 7]: room_id -= 1; player_rect.right = WIDTH - 10
        if room_id == 7 and player_rect.colliderect(house_rect): game_state = "WIN"

        for nb in notebooks:
            if nb["room"] == room_id: screen.blit(b_img, nb["rect"])
        if notebook_count >= 7:
            for k in keys_list:
                if k["room"] == room_id: screen.blit(keys_img, k["rect"])

        if not is_hidden:
            if current_time < invincible_until and (current_time // 100) % 2 == 0:
                pass
            else:
                screen.blit(p_img, (player_rect.x, player_rect.y - p_offset))
        else:
            screen.blit(font.render("HIDDEN", True, YELLOW), (player_rect.x, player_rect.y - 30))
        
        hp_pct = (player_hp / max_hp) * 100
        hp_col = GREEN if hp_pct > 60 else (ORANGE if hp_pct > 30 else RED)
        pygame.draw.rect(screen, BLACK, (WIDTH - 160, 50, 140, 20))
        pygame.draw.rect(screen, hp_col, (WIDTH - 158, 52, int(136 * (player_hp/max_hp)), 16))
        screen.blit(font.render(f"HP: {int(hp_pct)}%", True, WHITE), (WIDTH - 160, 75))
        screen.blit(font.render(f"{cur['books']}: {notebook_count}/7 | {cur['keys']}: {keys_found}/3 | {cur['loc']}: {cur['rooms'][room_id-1]}", True, WHITE), (20, 20))
        
        if timer_started:
            rem = max(0, time_limit - (current_time-start_ticks)//1000)
            screen.blit(font.render(f"TIMER: {rem}s", True, RED), (WIDTH-120, 20))
            if rem == 0: game_state = "GAMEOVER"

    elif game_state == "GAMEOVER":
        screen.fill(BLACK); screen.blit(title_font.render(cur["go"], True, RED), (WIDTH//2-180, HEIGHT//2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: 
                room_id, notebook_count, keys_found, timer_started, player_hp = 1, 0, 0, False, 3
                player_rect.center = (400, 500); game_state = "MENU"
                notebooks = [{"rect": pygame.Rect(random.randint(100,700), random.randint(100,500), 30, 30), "room": random.randint(1,4)} for _ in range(7)]
                keys_list = [{"rect": pygame.Rect(random.randint(50,700), random.randint(50,450), 35, 35), "room": random.randint(1,4)} for _ in range(3)]

    elif game_state == "WIN":
        screen.fill(GREEN); screen.blit(title_font.render(cur["win"], True, WHITE), (WIDTH//2-100, HEIGHT//2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

    pygame.display.flip(); clock.tick(60)
pygame.quit()

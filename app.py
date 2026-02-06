import pygame
import math
import sys
import random
import json
import os

# config
WIDTH, HEIGHT = 1000, 650
BG_COLOR = (25, 20, 35)
CARD_COLOR = (45, 35, 70)
ACCENT_COLOR = (255, 105, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 100)

SCREEN_START = "start"
SCREEN_LEVEL = "level"
SCREEN_MENU = "menu"
SCREEN_GAME = "game"

CHARACTERS = ["cat", "husky", "ducky", "frog", "larry", "parrot"]
LEVELS = ["A0", "A1", "A2", "B1", "B2"]

# init
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("StudyTale: English")
clock = pygame.time.Clock()


# fonts
def get_determination_font(size):
    return pygame.font.SysFont(["determination mono", "determination regular", "determination"], size)


font_logo = get_determination_font(45)
font_pixel = get_determination_font(28)
font_small_pixel = get_determination_font(19)
font_std = pygame.font.SysFont(["arialroundedmtbold", "comicansms", "arial"], 24)
font_std_big = pygame.font.SysFont(["arialroundedmtbold", "comicansms", "arial"], 34)

# assets
try:
    bg_menu = pygame.image.load("assets/bg.png").convert()
    bg_menu = pygame.transform.scale(bg_menu, (WIDTH, HEIGHT))
    logo_img = pygame.image.load("assets/logo.png").convert_alpha()
    logo_img = pygame.transform.smoothscale(logo_img, (WIDTH, HEIGHT))
    pygame.mixer.music.load("assets/music.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
except:
    bg_menu = pygame.Surface((WIDTH, HEIGHT))
    logo_img = pygame.Surface((WIDTH, HEIGHT))

bg_overlay = pygame.Surface((WIDTH, HEIGHT))
bg_overlay.fill((0, 0, 0))
bg_overlay.set_alpha(130)


def load_data(level):
    filename = f"{level}.json"
    if not os.path.exists(filename):
        sample = {"Sample Topic": [{"q": f"Level {level} start?", "opts": ["Yes", "No", "Maybe"], "ans": "Yes"}]}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample, f, ensure_ascii=False, indent=4)
        return sample
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_char_assets(name):
    def get_img(state):
        try:
            img = pygame.image.load(f"assets/{name}_{state}.png").convert()
            img.set_colorkey(BLACK)
            return img
        except:
            s = pygame.Surface((100, 100));
            s.fill((100, 100, 100))
            return s

    return {"idle": get_img("idle"), "happy": get_img("happy"), "sad": get_img("sad")}


def draw_text(text, font, color, x, y, center=False, max_width=450):
    words = text.split(' ')
    lines = []
    current_line = ""

    # move the word to next line
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        img = font.render(line.strip(), True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y + i * (font.get_linesize()))
        else:
            rect.topleft = (x, y + i * (font.get_linesize()))
        screen.blit(img, rect)



def draw_button(text, rect, is_hovered, radius=15, pixel_font=font_pixel):
    color = ACCENT_COLOR if is_hovered else CARD_COLOR
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    pygame.draw.rect(screen, WHITE, rect, width=2, border_radius=radius)
    draw_text(text, pixel_font, WHITE, rect.centerx, rect.centery, center=True)


def show_feedback(img, text, color):
    for _ in range(50):
        screen.blit(bg_menu, (0, 0))
        dark = pygame.Surface((WIDTH, HEIGHT));
        dark.fill(BLACK);
        dark.set_alpha(190);
        screen.blit(dark, (0, 0))
        scaled = pygame.transform.scale(img, (400, 400))
        screen.blit(scaled, (WIDTH // 2 - 200, HEIGHT // 2 - 230))
        draw_text(text, font_pixel, color, WIDTH // 2, HEIGHT - 110, center=True)
        pygame.display.flip()
        clock.tick(60)


# screens

def start_screen():
    screen.fill(BLACK)
    screen.blit(bg_overlay, (0, 0))
    screen.blit(logo_img, (0, 0))
    if (pygame.time.get_ticks() // 600) % 2 == 0:
        draw_text("Press any key to start", font_pixel, WHITE, WIDTH // 2, HEIGHT - 60, center=True)


def level_select_screen():
    screen.blit(bg_menu, (0, 0))
    screen.blit(bg_overlay, (0, 0))
    draw_text("SELECT LEVEL", font_logo, WHITE, WIDTH // 2, 150, center=True)
    mouse_pos = pygame.mouse.get_pos()
    level_btns = []
    for i, lvl in enumerate(LEVELS):
        rect = pygame.Rect(WIDTH // 2 - 100, 250 + i * 70, 200, 55)
        draw_button(lvl, rect, rect.collidepoint(mouse_pos))
        level_btns.append((rect, lvl))
    return level_btns


def main_menu_logic(menu_data, current_level):
    screen.blit(bg_menu, (0, 0))
    screen.blit(bg_overlay, (0, 0))
    overlay = pygame.Surface((560, 540));
    overlay.set_alpha(180);
    overlay.fill(BLACK)
    screen.blit(overlay, (WIDTH // 2 - 280, 90))

    mouse_pos = pygame.mouse.get_pos()
    draw_text(f"StudyTale: {current_level}", font_logo, WHITE, WIDTH // 2, 55, center=True)

    char_name = CHARACTERS[menu_data['char_idx']]
    draw_text(f"Friend: {char_name.upper()}", font_pixel, ACCENT_COLOR, WIDTH // 2, 135, center=True)

    btn_prev = pygame.Rect(WIDTH // 2 - 220, 120, 45, 45)
    btn_next = pygame.Rect(WIDTH // 2 + 175, 120, 45, 45)
    draw_button("<", btn_prev, btn_prev.collidepoint(mouse_pos))
    draw_button(">", btn_next, btn_next.collidepoint(mouse_pos))

    vol_rect = pygame.Rect(WIDTH - 180, 30, 120, 8)
    draw_text("Vol:", font_pixel, WHITE, WIDTH - 240, 25)
    pygame.draw.rect(screen, CARD_COLOR, vol_rect, border_radius=4)
    curr_vol = pygame.mixer.music.get_volume()
    pygame.draw.rect(screen, ACCENT_COLOR, (vol_rect.x, vol_rect.y, int(vol_rect.width * curr_vol), 8), border_radius=4)
    pygame.draw.circle(screen, WHITE, (vol_rect.x + int(vol_rect.width * curr_vol), vol_rect.centery), 8)

    search_rect = pygame.Rect(WIDTH // 2 - 200, 180, 400, 40)
    pygame.draw.rect(screen, ACCENT_COLOR if menu_data['input_active'] else CARD_COLOR, search_rect, border_radius=10)
    txt = menu_data['search_text'] if menu_data['search_text'] != "" else "Search topic..."
    draw_text(txt, font_pixel, WHITE if menu_data['search_text'] != "" else (150, 150, 150), search_rect.x + 12,
              search_rect.y + 7)

    topics_area = pygame.Rect(WIDTH // 2 - 230, 230, 460, 370)
    pygame.draw.rect(screen, (15, 15, 15), topics_area, border_radius=15)

    filtered_topics = [t for t in menu_data['data'].keys() if menu_data['search_text'].lower() in t.lower()]
    old_clip = screen.get_clip()
    screen.set_clip(topics_area)
    topic_btns = []
    for i, topic in enumerate(filtered_topics):
        rect = pygame.Rect(topics_area.x + 40, topics_area.y + 20 + i * 70 + menu_data['scroll_y'], 380, 55)
        draw_button(topic, rect, rect.collidepoint(mouse_pos) and topics_area.collidepoint(mouse_pos),
                    pixel_font=font_small_pixel)
        topic_btns.append((rect, topic))
    screen.set_clip(old_clip)

    return btn_prev, btn_next, vol_rect, search_rect, topic_btns, topics_area


def game_loop(topic, char_name, data):
    assets = load_char_assets(char_name)
    questions = list(data[topic])
    random.shuffle(questions)
    q_idx = 0
    btn_home = pygame.Rect(20, 20, 110, 45)

    while q_idx < len(questions):
        screen.blit(bg_menu, (0, 0))
        dark = pygame.Surface((WIDTH, HEIGHT));
        dark.fill(BLACK);
        dark.set_alpha(220);
        screen.blit(dark, (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        curr = questions[q_idx]

        s = math.sin(pygame.time.get_ticks() * 0.006) * 12
        img = pygame.transform.scale(assets["idle"], (350, 350 + int(s)))
        screen.blit(img, (70, HEIGHT // 2 - 175))

        draw_button("HOME", btn_home, btn_home.collidepoint(mouse_pos), radius=10)
        draw_text(f"Progress: {q_idx + 1}/{len(questions)}", font_pixel, ACCENT_COLOR, 520, 60)
        draw_text(curr["q"], font_std_big, WHITE, 520, 140)

        ans_btns = []
        for i, opt in enumerate(curr["opts"]):
            r = pygame.Rect(520, 240 + i * 85, 400, 65)
            draw_button(opt, r, r.collidepoint(mouse_pos))
            ans_btns.append((r, opt))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_home.collidepoint(event.pos): return
                for r, val in ans_btns:
                    if r.collidepoint(event.pos):
                        if val == curr["ans"]:
                            show_feedback(assets["happy"], "STAY DETERMINED!", YELLOW)
                            q_idx += 1
                        else:
                            show_feedback(assets["sad"], "DON'T GIVE UP!", (255, 60, 60))
        pygame.display.flip()
        clock.tick(60)


# run
current_screen = SCREEN_START
current_level = "A0"
m_data = {'char_idx': 0, 'scroll_y': 0, 'search_text': "", 'input_active': False, 'dragging_vol': False, 'data': {}}

while True:
    if current_screen == SCREEN_START:
        start_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]: current_screen = SCREEN_LEVEL
        pygame.display.flip()

    elif current_screen == SCREEN_LEVEL:
        lvl_btns = level_select_screen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, lvl in lvl_btns:
                    if rect.collidepoint(event.pos):
                        current_level = lvl
                        m_data['data'] = load_data(lvl)
                        current_screen = SCREEN_MENU
        pygame.display.flip()

    elif current_screen == SCREEN_MENU:
        bp, bn, vr, sr, t_btns, t_area = main_menu_logic(m_data, current_level)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_data['input_active'] = sr.collidepoint(event.pos)
                if vr.inflate(0, 20).collidepoint(event.pos): m_data['dragging_vol'] = True
                if event.button == 4: m_data['scroll_y'] = min(0, m_data['scroll_y'] + 45)
                if event.button == 5: m_data['scroll_y'] -= 45
                if bp.collidepoint(event.pos): m_data['char_idx'] = (m_data['char_idx'] - 1) % len(CHARACTERS)
                if bn.collidepoint(event.pos): m_data['char_idx'] = (m_data['char_idx'] + 1) % len(CHARACTERS)
                for r, t in t_btns:
                    if r.collidepoint(event.pos) and t_area.collidepoint(event.pos):
                        game_loop(t, CHARACTERS[m_data['char_idx']], m_data['data'])
            if event.type == pygame.MOUSEBUTTONUP: m_data['dragging_vol'] = False
            if event.type == pygame.MOUSEMOTION and m_data['dragging_vol']:
                m_vol = max(0, min((event.pos[0] - vr.x) / vr.width, 1.0))
                pygame.mixer.music.set_volume(m_vol)
            if event.type == pygame.KEYDOWN and m_data['input_active']:
                if event.key == pygame.K_BACKSPACE:
                    m_data['search_text'] = m_data['search_text'][:-1]
                else:
                    m_data['search_text'] += event.unicode
        pygame.display.flip()

    clock.tick(60)

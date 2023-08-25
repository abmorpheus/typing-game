import random, pygame, copy

pygame.init()

WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Type Racing')
surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
timer = pygame.time.Clock()
fps = 60

# Game variables
level = 1
active_string = ""
score = 0
high_score = 0
lives = 5
paused = True
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
submit = ''
word_objects = []

wordFile = open("words.txt", "r")
wordList = wordFile.read().split()
wordList = [''.join(letter for letter in word if letter.isalnum()) for word in wordList]

len_indexes = []
length = 1
new_level = True
choices = [False, True, False, False, False, False, False]
high_score = 0
with open("high_score.txt", 'r') as file:
    read = file.readlines()
    high_score = int(read[0]) if read[0].isnumeric() else 0


wordList.sort(key = len)
for i in range(len(wordList)):
    if len(wordList[i]) > length:
        length += 1
        len_indexes.append(i)
len_indexes.append(len(wordList))

# Fonts
header_font = pygame.font.Font('assets/fonts/square.ttf', 50)
pause_font = pygame.font.Font('assets/fonts/1up.ttf', 40)
banner_font = pygame.font.Font('assets/fonts/OdibeeSans-Regular.ttf', 30)
font = pygame.font.Font('assets/fonts/AldotheApache.ttf', 50)

# Sound Effects
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/music1.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

click = pygame.mixer.Sound('assets/sounds/click.mp3')
ding = pygame.mixer.Sound('assets/sounds/ding.mp3')
wrong = pygame.mixer.Sound('assets/sounds/wrong.mp3')

click.set_volume(0.2)
ding.set_volume(0.2)
wrong.set_volume(0.3)


class Word:
    def __init__(self, text, speed, xpos, ypos):
        self.text = text
        self.ypos = ypos
        self.xpos = xpos
        self.speed = speed

    def draw(self):
        color = 'black'
        screen.blit(font.render(self.text, True, color), (self.xpos, self.ypos))
        active_len = len(active_string)
        if active_string == self.text[:active_len]:
            screen.blit(font.render(active_string, True, 'green'), (self.xpos, self.ypos))

    def update(self):
        self.xpos -= self.speed

class Button:
    def __init__(self, xpos, ypos, text, clicked, surface):
        self.xpos = xpos
        self.ypos = ypos
        self.text = text
        self.clicked = clicked
        self.surface = surface
    
    def draw(self):
        circular = pygame.draw.circle(self.surface, (45, 89, 135), (self.xpos, self.ypos), 35)
        if circular.collidepoint(pygame.mouse.get_pos()):
            buttons = pygame.mouse.get_pressed()
            if buttons[0]:
                pygame.draw.circle(self.surface, (190, 35, 35), (self.xpos, self.ypos), 35)
                self.clicked = True
            else:
                pygame.draw.circle(self.surface, (190, 89, 35), (self.xpos, self.ypos), 35)

        pygame.draw.circle(self.surface, 'white', (self.xpos, self.ypos), 35, 3)
        self.surface.blit(pause_font.render(self.text, True, 'white'), (self.xpos-15, self.ypos-25))

def draw_screen():
    # outlines
    pygame.draw.rect(screen, (32, 42, 68), [0, HEIGHT - 100, WIDTH, 100])
    pygame.draw.rect(screen, 'white', [0, 0, WIDTH, HEIGHT], 5)
    pygame.draw.line(screen, 'white', (250, HEIGHT-100), (250, HEIGHT), 2)
    pygame.draw.line(screen, 'white', (700, HEIGHT-100), (700, HEIGHT), 2)
    pygame.draw.line(screen, 'white', (0, HEIGHT-100), (WIDTH, HEIGHT-100), 2)
    pygame.draw.rect(screen, 'black', [0, 0, WIDTH, HEIGHT], 2)

    # text for displaying current lvl, input, high socre etc
    screen.blit(header_font.render(f"Level: {level}", True, 'white'), (10, HEIGHT-75))
    screen.blit(header_font.render(f'"{active_string}"', True, 'white'), (270, HEIGHT-75))

    pause_button = Button(748, HEIGHT-52, 'II', False, screen)
    pause_button.draw()

    screen.blit(banner_font.render(f"Score: {score}", True, 'black'), (250, 10))
    screen.blit(banner_font.render(f"Best: {high_score}", True, 'black'), (550, 10))
    screen.blit(banner_font.render(f"Lives: {lives}", True, 'black'), (10, 10))
    return pause_button.clicked

def draw_pause():
    choice_commits = copy.deepcopy(choices)
    surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(surface, (0, 0, 0, 100), [100, 100, 600, 300], 0, 5)
    pygame.draw.rect(surface, (0, 0, 0, 100), [100, 100, 600, 300], 5, 5)
    
    resume_button = Button(160, 200, '>', False, surface)
    resume_button.draw()
    quit_button = Button(410, 200, 'X', False, surface)
    quit_button.draw()

    surface.blit(header_font.render("MENU", True, 'white'), (110, 110))
    surface.blit(header_font.render("PLAY", True, 'white'), (210, 175))
    surface.blit(header_font.render("QUIT", True, 'white'), (450, 175))
    surface.blit(header_font.render("Active Letter Lengths:", True, 'white'), (110, 250))

    for i in range(len(choices)):
        button = Button(160 + (i*80), 350, str(i+2), False, surface)
        button.draw()
        if button.clicked:
            if choice_commits[i]:
                choice_commits[i] = False
            else:
                choice_commits[i] = True
        if choices[i]:
            pygame.draw.circle(surface, 'green', (160 + (i*80), 350), 35, 5)

    screen.blit(surface, (0, 0))     
    return resume_button.clicked, choice_commits, quit_button.clicked

def check_answer(sc):
    for w in word_objects:
        if w.text == submit:
            points = w.speed * len(w.text) * 10 * (len(w.text)/4)
            sc += int(points)
            word_objects.remove(w)
            ding.play()
    return sc

def generate_level():
    word_objs = []
    include = []
    vertical_spacing = (HEIGHT-150)//level
    if True not in choices:
        choices[0] = True
    for i in range(len(choices)):
        if choices[i]:
            include.append((len_indexes[i], len_indexes[i+1]))
    for i in range(level):
        speed = random.randint(1, 3)
        ypos = random.randint(10 + (i*vertical_spacing), (i+1)*vertical_spacing)
        xpos = random.randint(WIDTH, WIDTH + 1000)
        ind_select = random.choice(include)
        index = random.randint(ind_select[0], ind_select[1])
        text = wordList[index].lower()
        new_word = Word(text, speed, xpos, ypos)
        word_objs.append(new_word)

    return word_objs

def check_highscore():
    global high_score
    if score > high_score:
        high_score = score
        f = open("high_score.txt", "w+")
        f.write(str(int(high_score)))
        f.close()


# Main program
run = True
while run:
    screen.fill((135, 206, 235))
    timer.tick(fps)
    pause_button = draw_screen()

    if paused:
        resume_btn, changes, quit_btn = draw_pause()
        if resume_btn:
            paused = False
        if quit_btn:
            run = False
            check_highscore(score)
    if new_level and not paused:
        word_objects = generate_level()
        new_level = False
    else:
        for w in word_objects:
            w.draw()
            if not paused:
                w.update()
            if w.xpos < -200:
                word_objects.remove(w)
                lives -= 1
    if len(word_objects) == 0 and not paused:
        level += 1
        new_level = True
    
    if submit != '':
        init = score
        score = check_answer(score)
        submit = ''
        if init == score:
            wrong.play()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            check_highscore()
            run = False
        
        if event.type == pygame.KEYDOWN:
            if not paused:
                if event.unicode.lower() in letters:
                    active_string += event.unicode.lower()
                    click.play()
                if event.key == pygame.K_BACKSPACE and len(active_string):
                    active_string = active_string[:-1]
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    submit = active_string
                    active_string = ""

            if event.key == pygame.K_ESCAPE:
                if paused:
                    paused = False
                else:
                    paused = True
        if event.type == pygame.MOUSEBUTTONUP and paused:
            if event.button == 1:
                choices = changes

    if pause_button:
        paused = True

    if lives <= 0:
        paused = True
        level = 1
        lives = 5
        word_objects = []
        new_level = True
        check_highscore()
        score = 0
    pygame.display.flip()

pygame.quit()
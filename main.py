import pygame as pg
import json
import random

# Инициализация pg
pg.init()

FPS = 60
# Размеры окна
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 550

BUTTON_WIDTH = 200
BUTTON_HEIGHT = 60

MENU_NAV_XPAD = 90
MENU_NAV_YPAD = 130

ICON_SIZE = 80
PADDING = 10

DOG_WIDTH = 310
DOG_HEIGHT = 500
DOG_Y = 150

font = pg.font.Font(None, 40)
font_mini = pg.font.Font(None, 15)


def load_image(file, width, height):
    image = pg.image.load(file)
    image = pg.transform.scale(image, (width, height))
    return image


def text_render(text, render_font=font):
    return render_font.render(str(text), True, 'black')


class Button:
    def __init__(self, x, y, text, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, text_font=font, func=None):
        self.idle_image = load_image('images/button.png', width, height)
        self.pressed_image = load_image('images/button_clicked.png', width, height)
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y

        self.is_pressed = True

        self.func = func

        self.font = text_font
        self.text = text_render(text, text_font)
        self.text_render = self.text.get_rect()
        self.text_render.center = self.rect.center

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_render)

    def update(self):
        mouse_pos = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if self.is_pressed:
                self.image = self.pressed_image
            else:
                self.image = self.idle_image

    def is_clicked(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                self.func()
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False


class Item:
    def __init__(self, name='', price=0, image='images/items/blue t-shirt.png', is_bought=False, is_using=False, satiety=0):
        self.name = name
        self.price = price
        self.file = image
        self.is_bought = is_bought
        self.is_put_on = is_using
        self.satiety = satiety

        if satiety == 0:
            self.image = load_image(image, DOG_WIDTH // 1.7, DOG_HEIGHT // 1.7)
            self.full_image = load_image(image, DOG_WIDTH, DOG_HEIGHT)
        else:
            self.image = load_image(image, 150, 150)


class Dog:
    def __init__(self):
        self.image = load_image('images/dog.png', DOG_WIDTH // 2, DOG_HEIGHT // 2)
        self.rect = self.image.get_rect()
        self.rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 135

    def update(self):
        keypressed = pg.key.get_pressed()
        if keypressed[pg.K_a]:
            self.rect.x -= 7
        if keypressed[pg.K_d]:
            self.rect.x += 7


class Toy(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        ri = random.randint(0, 2)
        if ri == 0:
            ri = 'images/toys/ball.png'
        elif ri == 1:
            ri = 'images/toys/blue bone.png'
        elif ri == 2:
            ri = 'images/toys/red bone.png'

        self.image = load_image(ri, 100, 100)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100, 700), 0)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > 700:
            self.kill()


class MiniGame:
    def __init__(self, game):
        self.game = game
        self.bg = load_image('images/game_background.png', SCREEN_WIDTH, SCREEN_HEIGHT)

        self.dog = Dog()
        self.toys = pg.sprite.Group()
        self.score = 0
        self.start_time = pg.time.get_ticks()
        self.interval = 10000

    def new_game(self):
        self.dog = Dog()
        self.toys = pg.sprite.Group()
        self.score = 0
        self.start_time = pg.time.get_ticks()
        self.interval = 10000

    def update(self):
        if self.game.mode == 'mini game':
            self.dog.update()
            self.toys.update()
            if random.randint(0, 50) == 1:
                self.toys.add(Toy())
            hits = pg.sprite.spritecollide(self.dog, self.toys, True, pg.sprite.collide_circle_ratio(0.6))
            self.score += len(hits)
            if self.start_time + self.interval <= pg.time.get_ticks():
                self.game.happiness += self.score * 3
                if self.game.happiness > 100:
                    self.game.happiness = 100
                self.new_game()
                self.game.mode = 'main'

    def draw(self):
        self.game.screen.blit(self.bg, (0, 0))

        self.game.screen.blit(self.dog.image, self.dog.rect)

        self.toys.draw(self.game.screen)

        self.game.screen.blit(text_render(self.score), (MENU_NAV_XPAD + 20, 80))


class ClothesMenu:
    def __init__(self, game, data):
        self.game = game
        self.menu_page = load_image('images/menu/menu_page.png', SCREEN_WIDTH, SCREEN_HEIGHT)

        self.button_label_off = load_image('images/menu/bottom_label_off.png', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.button_label_on = load_image('images/menu/bottom_label_on.png', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_off = load_image('images/menu/top_label_off.png', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_on = load_image('images/menu/top_label_on.png', SCREEN_WIDTH, SCREEN_HEIGHT)

        self.items = []

        for item in data['clothes']:
            self.items.append(Item(*item.values()))

        self.current_item = 0

        self.item_rect = self.items[0].image.get_rect()
        self.item_rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        self.next_button = Button(SCREEN_WIDTH - MENU_NAV_XPAD - BUTTON_WIDTH, SCREEN_HEIGHT - MENU_NAV_YPAD, 'Вперед',  height=int(BUTTON_HEIGHT//1.2), width=int(BUTTON_WIDTH//1.2), func=self.to_next)
        self.back_button = Button(MENU_NAV_XPAD + 30, SCREEN_HEIGHT - MENU_NAV_YPAD, 'Назад',  height=int(BUTTON_HEIGHT//1.2), width=int(BUTTON_WIDTH//1.2), func=self.to_back)
        self.use_button = Button(MENU_NAV_XPAD + 30, SCREEN_HEIGHT - MENU_NAV_YPAD - 50, 'Надеть',  height=int(BUTTON_HEIGHT//1.2), width=int(BUTTON_WIDTH//1.2), func=self.use_item)
        self.buy_button = Button(SCREEN_WIDTH // 2 - int(BUTTON_WIDTH // 1.5) // 2, SCREEN_HEIGHT // 2 + 95, 'Купить',  height=int(BUTTON_HEIGHT//1.5), width=int(BUTTON_WIDTH//1.5), func=self.buy)

        self.buttons = [self.next_button, self.back_button, self.use_button, self.buy_button]

    def to_next(self):
        if not self.current_item >= len(self.items) - 1:
            self.current_item += 1
        else:
            self.current_item = 0

    def to_back(self):
        if self.current_item > 0:
            self.current_item -= 1
        else:
            self.current_item = len(self.items) - 1

    def use_item(self):
        if self.items[self.current_item].is_bought:
            self.items[self.current_item].is_put_on = not self.items[self.current_item].is_put_on

    def buy(self):
        if self.game.money >= self.items[self.current_item].price:
            self.game.money -= self.items[self.current_item].price
            self.items[self.current_item].is_bought = True

    def update(self):
        for button in self.buttons:
            button.update()

    def is_clicked(self, event):
        for button in self.buttons:
            button.is_clicked(event)

    def draw(self, screen):
        self.text = text_render(self.items[self.current_item].price, font)
        self.text_render = self.text.get_rect()
        self.text_render.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 95)


        screen.blit(self.menu_page, (0, 0))
        screen.blit(self.items[self.current_item].image, self.item_rect)
        screen.blit(self.text, self.text_render)

        if self.items[self.current_item].is_bought:
            screen.blit(self.button_label_on, (0, 0))
            self.text = text_render('Куплено', font)
        else:
            screen.blit(self.button_label_off, (0, 0))
            self.text = text_render('Не куплено', font)

        self.text_render = self.text.get_rect()
        self.text_render.center = (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT // 2 - 80)
        screen.blit(self.text, self.text_render)

        if self.items[self.current_item].is_put_on:
            screen.blit(self.top_label_on, (0, 0))
            self.text = text_render('Надето', font)
        else:
            screen.blit(self.top_label_off, (0, 0))
            self.text = text_render('Не надето', font)

        self.text_render = self.text.get_rect()
        self.text_render.center = (SCREEN_WIDTH // 2 + 250, SCREEN_HEIGHT // 2 - 150)
        screen.blit(self.text, self.text_render)

        for button in self.buttons:
            button.draw(screen)


class FoodMenu:
    def __init__(self, game):
        self.game = game
        self.menu_page = load_image('images/menu/menu_page.png', SCREEN_WIDTH, SCREEN_HEIGHT)

        self.button_label_off = load_image('images/menu/bottom_label_off.png', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.button_label_on = load_image('images/menu/bottom_label_on.png', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_off = load_image('images/menu/top_label_off.png', SCREEN_WIDTH, SCREEN_HEIGHT)
        self.top_label_on = load_image('images/menu/top_label_on.png', SCREEN_WIDTH, SCREEN_HEIGHT)

        self.items = [Item('Яблоко', 25, 'images/food/apple.png', satiety=15), Item('Кость', 15, 'images/food/bone.png', satiety=8), Item('Корм', 35, 'images/food/dog food.png', satiety=20), Item('Элитный корм', 85, 'images/food/dog food elite.png', satiety=50), Item('Мясо', 150, 'images/food/meat.png', satiety=100)]

        self.current_item = 0

        self.item_rect = self.items[0].image.get_rect()
        self.item_rect.center = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10

        self.next_button = Button(SCREEN_WIDTH - MENU_NAV_XPAD - BUTTON_WIDTH, SCREEN_HEIGHT - MENU_NAV_YPAD, 'Вперед',  height=int(BUTTON_HEIGHT//1.2), width=int(BUTTON_WIDTH//1.2), func=self.to_next)
        self.back_button = Button(MENU_NAV_XPAD + 30, SCREEN_HEIGHT - MENU_NAV_YPAD, 'Назад',  height=int(BUTTON_HEIGHT//1.2), width=int(BUTTON_WIDTH//1.2), func=self.to_back)
        self.buy_button = Button(SCREEN_WIDTH // 2 - int(BUTTON_WIDTH // 1.5) // 2, SCREEN_HEIGHT // 2 + 95, 'Купить',  height=int(BUTTON_HEIGHT//1.5), width=int(BUTTON_WIDTH//1.5), func=self.buy)

        self.buttons = [self.next_button, self.back_button, self.buy_button]

    def to_next(self):
        if not self.current_item >= len(self.items) - 1:
            self.current_item += 1
        else:
            self.current_item = 0

    def to_back(self):
        if self.current_item > 0:
            self.current_item -= 1
        else:
            self.current_item = len(self.items) - 1

    def buy(self):
        if self.game.money >= self.items[self.current_item].price:
            self.game.money -= self.items[self.current_item].price
            self.game.satiety += self.items[self.current_item].satiety
            if self.game.satiety > 100:
                self.game.satiety = 100

    def update(self):
        for button in self.buttons:
            button.update()

    def is_clicked(self, event):
        for button in self.buttons:
            button.is_clicked(event)

    def draw(self, screen):
        self.text = text_render(self.items[self.current_item].price, font)
        self.text_render = self.text.get_rect()
        self.text_render.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 95)

        screen.blit(self.menu_page, (0, 0))
        screen.blit(self.items[self.current_item].image, self.item_rect)
        screen.blit(self.text, self.text_render)

        for button in self.buttons:
            button.draw(screen)


class Game:
    def __init__(self):

        # Создание окна
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Виртуальный питомец")

        self.clock = pg.time.Clock()

        with open('save.json', encoding='utf-8') as f:
            data = json.load(f)
            self.data = data

        self.happiness = data['happiness']
        self.satiety = data['satiety']
        self.health = data['health']

        self.money = data['money']
        self.coins_per_second = data['coins_per_second']
        self.costs_of_upgrade = {}

        for key, value in data['costs_of_upgrade'].items():
            self.costs_of_upgrade[int(key)] = value

        self.background = load_image('images/background.png', SCREEN_WIDTH, SCREEN_HEIGHT)

        self.happiness_image = load_image('images/happiness.png', ICON_SIZE, ICON_SIZE)
        self.satiety_image = load_image('images/satiety.png', ICON_SIZE, ICON_SIZE)
        self.health_image = load_image('images/health.png', ICON_SIZE, ICON_SIZE)
        self.money_image = load_image('images/money.png', ICON_SIZE, ICON_SIZE)
        self.body_image = load_image('images/dog.png', DOG_WIDTH, DOG_HEIGHT)

        button_x = SCREEN_WIDTH - BUTTON_WIDTH - PADDING

        self.buttons = [Button(button_x, PADDING + ICON_SIZE, 'ЕДА', func=self.food_menu_on), Button(button_x, PADDING * 2 + ICON_SIZE + BUTTON_HEIGHT, 'ОДЕЖДА', func=self.clothes_menu_on), Button(button_x, PADDING * 3 + ICON_SIZE + BUTTON_HEIGHT * 2, 'ИГРЫ', func=self.mini_game_on), Button(SCREEN_WIDTH - ICON_SIZE - PADDING // 2, 5, 'Улучшить', BUTTON_WIDTH // 3, BUTTON_HEIGHT // 3, font_mini, func=self.increase_money)]

        self.clothes_menu = ClothesMenu(self, self.data)
        self.food_menu = FoodMenu(self)
        self.mini_game = MiniGame(self)

        self.mode = 'main'

        self.INCREASE_COINS = pg.USEREVENT + 1
        pg.time.set_timer(self.INCREASE_COINS, 1000)
        self.DECREASE_SATIETY = pg.USEREVENT + 2
        pg.time.set_timer(self.DECREASE_SATIETY, 1500)
        self.DECREASE_HEALTH = pg.USEREVENT + 3
        pg.time.set_timer(self.DECREASE_HEALTH, 500)
        self.INCREASE_HEALTH = pg.USEREVENT + 4
        pg.time.set_timer(self.INCREASE_HEALTH, 2000)
        self.DECREASE_HAPPINESS = pg.USEREVENT + 5
        pg.time.set_timer(self.DECREASE_HAPPINESS, 1500)

        self.run()

    def increase_money(self):
        for cost in self.costs_of_upgrade:
            if not self.costs_of_upgrade[cost] and self.money >= cost:
                self.costs_of_upgrade[cost] = True
                self.money -= cost
                self.coins_per_second *= 2
                break

    def clothes_menu_on(self):
        self.mode = 'clothes menu'

    def food_menu_on(self):
        self.mode = 'food menu'

    def mini_game_on(self):
        self.mode = 'mini game'

    def save(self):
        self.data['happiness'] = self.happiness
        self.data['satiety'] = self.satiety
        self.data['health'] = self.health
        self.data['money'] = self.money
        self.data['coins_per_second'] = self.coins_per_second
        self.data['costs_of_upgrade'] = self.costs_of_upgrade
        self.data['clothes'] = []
        for item in self.clothes_menu.items:
            self.data['clothes'].append({'name': item.name, 'price': item.price, 'file': item.file, 'is_bought': item.is_bought, 'is_using': item.is_put_on})
        with open('save.json', 'w', encoding='utf-8') as outdata:
            json.dump(self.data, outdata, ensure_ascii=False)

    def run(self):
        while True:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.save()
                exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.mode = 'main'
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.money += 1
            if event.type == self.INCREASE_COINS:
                self.money += self.coins_per_second
            if event.type == self.DECREASE_SATIETY:
                if self.satiety > 0:
                    self.satiety -= 1
            if event.type == self.DECREASE_HEALTH:
                if self.satiety <= 0 and self.health > 0:
                    self.health -= 1
                if self.happiness <= 0 and self.health > 0:
                    self.health -= 1
                if self.health <= 0:
                    self.happiness = 100
                    self.satiety = 100
                    self.health = 100
                    self.money = 10
                    self.coins_per_second = 1
                    for key in self.costs_of_upgrade.keys():
                        self.costs_of_upgrade[key] = False
                    self.save()
                    pg.quit()
                    exit()
            if event.type == self.INCREASE_HEALTH:
                if self.satiety > 50 and self.health < 100:
                    self.health += 1
            if event.type == self.DECREASE_HAPPINESS:
                if self.happiness > 0:
                    self.happiness -= 1
            if self.mode == 'main':
                for button in self.buttons:
                    button.is_clicked(event)
            elif self.mode == 'clothes menu':
                self.clothes_menu.is_clicked(event)
            elif self.mode == 'food menu':
                self.food_menu.is_clicked(event)

    def update(self):
        if self.mode == 'main':
            for button in self.buttons:
                button.update()
        elif self.mode == 'mini game':
            self.mini_game.update()
        elif self.mode == 'clothes menu':
            self.clothes_menu.update()
        elif self.mode == 'food menu':
            self.food_menu.update()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.happiness_image, (PADDING, PADDING))
        self.screen.blit(self.satiety_image, (PADDING, PADDING + ICON_SIZE // 1.5))
        self.screen.blit(self.health_image, (PADDING, PADDING + (ICON_SIZE // 1.5) * 2))
        self.screen.blit(self.money_image, (SCREEN_WIDTH - PADDING - ICON_SIZE, PADDING))
        self.screen.blit(text_render(self.happiness), (ICON_SIZE + PADDING, PADDING * 4))
        self.screen.blit(text_render(self.satiety), (ICON_SIZE + PADDING, PADDING * 4 + ICON_SIZE // 1.5))
        self.screen.blit(text_render(self.health), (ICON_SIZE + PADDING, PADDING * 4 + (ICON_SIZE // 1.5) * 2))
        self.screen.blit(text_render(self.money), (SCREEN_WIDTH - ICON_SIZE * 2 - PADDING, PADDING * 4))

        for button in self.buttons:
            button.draw(self.screen)

        if self.mode == 'main':
            self.screen.blit(self.body_image, (SCREEN_WIDTH // 2 - DOG_WIDTH // 2, DOG_Y))

            for item in self.clothes_menu.items:
                if item.is_put_on:
                    self.screen.blit(item.full_image, (SCREEN_WIDTH // 2 - DOG_WIDTH // 2, DOG_Y))

        if self.mode == 'clothes menu':
            self.clothes_menu.draw(self.screen)
        elif self.mode == 'food menu':
            self.food_menu.draw(self.screen)
        elif self.mode == 'mini game':
            self.mini_game.draw()

        pg.display.flip()


if __name__ == "__main__":
    Game()

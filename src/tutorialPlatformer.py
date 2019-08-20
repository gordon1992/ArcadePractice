from datetime import datetime

import arcade

# Constants
RESOURCES_ROOT = "../resources/"
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1
TILE_SCALING = 0.5
COIN_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 8
GRAVITY = 5
PLAYER_JUMP_SPEED = 80

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 150
RIGHT_VIEWPORT_MARGIN = 150
BOTTOM_VIEWPORT_MARGIN = 50
TOP_VIEWPORT_MARGIN = 100

GAME_START_X = 0
GAME_END_X = 1250


class Coin(arcade.Sprite):
    def __init__(self, image, scale, value):
        super().__init__(image, scale)
        self.value = value

    def remove_from_sprite_lists(self):
        super().remove_from_sprite_lists()


class Player(arcade.Sprite):
    TEXTURE_LEFT = 0
    TEXTURE_RIGHT = 1

    def __init__(self):
        super().__init__()

        # Load a left facing texture and a right facing texture.
        # mirrored=True will mirror the image we load.
        left_texture = arcade.load_texture(f"{RESOURCES_ROOT}/images/player_1/player_stand.png", mirrored=True,
                                           scale=CHARACTER_SCALING)
        self.textures.append(left_texture)
        right_texture = arcade.load_texture(f"{RESOURCES_ROOT}/images/player_1/player_stand.png",
                                            scale=CHARACTER_SCALING)
        self.textures.append(right_texture)

        # By default, face right.
        self.set_texture(self.TEXTURE_RIGHT)

    def update(self):
        # Figure out if we should face left or right
        if self.change_x < 0:
            self.set_texture(self.TEXTURE_LEFT)
        if self.change_x > 0:
            self.set_texture(self.TEXTURE_RIGHT)


class MyGame(arcade.Window):

    def __init__(self):
        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.player_sprite = None

        self.physics_engine = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.collect_coin_sound = arcade.load_sound(f"{RESOURCES_ROOT}/sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(f"{RESOURCES_ROOT}/sounds/jump1.wav")

        self.message_shown = 0
        self.messages = ["message one", "here is message two", "oh hey, it's message three"]
        self.last_rotation = datetime.timestamp(datetime.now())

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList[Coin]()

        self.setup_player()
        self.setup_wall()
        self.setup_ground()
        self.setup_crates()
        self.setup_coins()

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

    def setup_player(self):
        self.player_sprite = Player()
        self.player_sprite.center_x = LEFT_VIEWPORT_MARGIN
        self.player_sprite.center_y = 107
        self.player_list.append(self.player_sprite)
        self.score = 0

    def setup_wall(self):
        for y in range(32, 2000, 64):
            wall = arcade.Sprite(f"{RESOURCES_ROOT}/images/tiles/stone.png", TILE_SCALING)
            wall.center_x = GAME_START_X - 64
            wall.center_y = y
            self.wall_list.append(wall)

        for y in range(32, 2000, 64):
            wall = arcade.Sprite(f"{RESOURCES_ROOT}/images/tiles/stone.png", TILE_SCALING)
            wall.center_x = GAME_END_X + 32
            wall.center_y = y
            self.wall_list.append(wall)

    def setup_ground(self):
        for x in range(GAME_START_X, GAME_END_X, 64):
            wall = arcade.Sprite(f"{RESOURCES_ROOT}/images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

    def setup_crates(self):
        for x in range(256, GAME_END_X, 256):
            wall = arcade.Sprite(f"{RESOURCES_ROOT}/images/tiles/boxCrate_double.png", TILE_SCALING)
            wall.position = [x, 96]
            self.wall_list.append(wall)

    def setup_coins(self):
        self.setup_bronze_coins()
        self.setup_silver_coins()
        self.setup_gold_coins()

    def setup_bronze_coins(self):
        # Use a loop to place some coins for our character to pick up
        for x in range(448, GAME_END_X, 256):
            coin = Coin(f"{RESOURCES_ROOT}/images/items/coinBronze.png", COIN_SCALING, 1)
            coin.center_x = x
            coin.center_y = 96
            coin.value = 1
            self.coin_list.append(coin)

    def setup_silver_coins(self):
        # Use a loop to place some coins for our character to pick up
        for x in range(384, GAME_END_X, 256):
            coin = Coin(f"{RESOURCES_ROOT}/images/items/coinSilver.png", COIN_SCALING, 2)
            coin.center_x = x
            coin.center_y = 96
            coin.value = 2
            self.coin_list.append(coin)

    def setup_gold_coins(self):
        # Use a loop to place some coins for our character to pick up
        for x in range(320, GAME_END_X, 256):
            coin = Coin(f"{RESOURCES_ROOT}/images/items/coinGold.png", COIN_SCALING, 5)
            coin.center_x = x
            coin.center_y = 96
            coin.value = 5
            self.coin_list.append(coin)

    def on_draw(self):
        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        # Draw our score on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        now = datetime.timestamp(datetime.now())
        time_since_last_rotation = now - self.last_rotation
        if time_since_last_rotation > 3:
            self.last_rotation = now
            self.message_shown = (self.message_shown + 1) % len(self.messages)
        arcade.draw_text(self.messages[self.message_shown], 10 + self.view_left, 300 + self.view_bottom,
                         arcade.csscolor.WHITE, 64)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

    def update(self, delta_time):
        self.update_player_movement()
        self.physics_engine.update()
        self.update_coin_collision()
        self.update_scrolling()

    def update_player_movement(self):
        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        if self.up_pressed and self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
            self.up_pressed = False
            arcade.play_sound(self.jump_sound)
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
            self.player_sprite.update()
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
            self.player_sprite.update()

    def update_coin_collision(self):
        # See if we hit any coins
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)
        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += coin.value

    def update_scrolling(self):
        # Track if we need to change the viewport
        changed = False
        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True
        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True
        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True
        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True
        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

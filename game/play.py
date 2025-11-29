import arcade, arcade.gui, json, time, os

from utils.constants import FOLLOW_DECAY_CONST, GRAVITY, PLAYER_MOVEMENT_SPEED, PLAYER_JUMP_SPEED, GRID_PIXEL_SIZE, PLAYER_JUMP_COOLDOWN, LEFT_RIGHT_DIAGONAL_ID, RIGHT_LEFT_DIAGONAL_ID
from utils.preload import tilemaps, player_still_animation, player_jump_animation, player_walk_animation, freeze_sound, background_sound

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client, level_num):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Keeping the warmth")

        self.camera_sprites = arcade.Camera2D()
        self.camera_bounds = self.window.rect
        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.level_num = level_num

        self.scene = self.create_scene()

        self.right_left_diagonal_sprites = [
            sprite for sprite in self.scene["ice"]
            if hasattr(sprite, 'properties') and 
            sprite.properties.get('tile_id') == RIGHT_LEFT_DIAGONAL_ID
        ]

        self.left_right_diagonal_sprites = [
            sprite for sprite in self.scene["ice"] 
            if hasattr(sprite, 'properties') and 
            sprite.properties.get('tile_id') == LEFT_RIGHT_DIAGONAL_ID
        ]

        self.spawn_position = tilemaps[self.level_num].object_lists["spawn"][0].shape
        player_x, player_y = self.spawn_position

        self.player = arcade.TextureAnimationSprite(animation=player_still_animation, center_x=player_x, center_y=player_y)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=GRAVITY,
            walls=[self.scene["walls"], self.scene["ice"]]
        )

        self.warmth = 100
        self.direction = "right"
        self.last_jump = time.perf_counter()
        self.start = time.perf_counter()
        self.trees = 0
        self.collected_trees = []

        self.level_texts = []

        for tile in tilemaps[self.level_num].object_lists["text"]:
            self.level_texts.append(arcade.Text(tile.name, tile.shape[0], tile.shape[1], font_size=14))
            self.level_texts[-1].original_text = tile.name
            self.level_texts[-1].change_to_when_hit = tile.properties.get("change_to_when_hit")

        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.data = json.load(file)
        else:
            self.data = {}

        self.high_score = self.data.get("high_score", 9999)
        self.tries = self.data.get("tries", 1)
        if self.high_score == 9999:
            self.no_highscore = True
            self.high_score = 0
        else:
            self.no_highscore = False

        self.scene.add_sprite("Player", self.player)

        if self.settings.get("sfx", True):        
            self.freeze_player = freeze_sound.play(loop=True, volume=self.settings.get("sfx_volume", 100) / 100)
            self.freeze_player.pause()

            self.background_player = background_sound.play(loop=True, volume=self.settings.get("sfx_volume", 100) / 100)

    def on_show_view(self):
        super().on_show_view()

        self.info_label = self.anchor.add(arcade.gui.UILabel(text=f"Time took: 0s High Score: {self.high_score}s Trees: 0 Tries: {self.tries}", font_size=20), anchor_x="center", anchor_y="top")

    def reset(self, reached_end=False):
        self.warmth = 100
        self.trees = 0
        self.player.change_x, self.player.change_y = 0, 0
        self.player.position = self.spawn_position
        self.start = time.perf_counter()
        self.tries += 1

        for collected_tree in self.collected_trees:
            self.scene["trees"].append(collected_tree)

        for level_text in self.level_texts:
            level_text.text = level_text.original_text

        self.collected_trees = []

        if not reached_end and self.no_highscore:
            self.high_score = 9999
        elif reached_end and self.no_highscore:
            self.no_highscore = False

        self.update_data_file()

    def create_scene(self) -> arcade.Scene:
        self.camera_bounds = arcade.LRBT(
            self.window.width/2.0,
            tilemaps[self.level_num].width * GRID_PIXEL_SIZE - self.window.width/2.0,
            self.window.height/2.0,
            tilemaps[self.level_num].height * GRID_PIXEL_SIZE
        )

        return arcade.Scene.from_tilemap(tilemaps[self.level_num])

    def on_draw(self):
        self.clear()

        with self.camera_sprites.activate():
            self.scene.draw()

            for level_text in self.level_texts:
                level_text.draw()

        self.ui.draw()
        arcade.draw_lbwh_rectangle_filled(self.window.width / 4, 0, (self.window.width / 2), self.window.height / 20, arcade.color.SKY_BLUE)
        arcade.draw_lbwh_rectangle_filled(self.window.width / 4, 0, (self.window.width / 2) * (self.warmth / 100), self.window.height / 20, arcade.color.RED)

    def center_camera_to_player(self):
        self.camera_sprites.position = arcade.math.smerp_2d(
            self.camera_sprites.position,
            self.player.position,
            self.window.delta_time,
            FOLLOW_DECAY_CONST,
        )

        self.camera_sprites.view_data.position = arcade.camera.grips.constrain_xy(
            self.camera_sprites.view_data, self.camera_bounds
        )

    def clamp(self, value, min_value, max_value):
        return max(min_value, min(value, max_value))
    
    def change_player_animation(self, animation):
        if self.player.animation != animation:
            self.player.animation = animation

    def on_update(self, delta_time: float):
        hit_list = self.physics_engine.update()
        self.center_camera_to_player()

        if self.player.collides_with_list(self.scene["end"]):
            end_time = round(time.perf_counter() - self.start, 2)
            
            if self.no_highscore or end_time < self.high_score:
                self.high_score = end_time
            
            self.reset(True)
            return

        if self.no_highscore:
            self.high_score = round(time.perf_counter() - self.start, 2)

        self.info_label.text = f"Time took: {round(time.perf_counter() - self.start, 2)}s High Score: {self.high_score}s Trees: {self.trees} Tries: {self.tries}"

        if self.warmth <= 0 or self.player.collides_with_list(self.scene["spikes"]) or self.player.center_x < 0 or self.player.center_x > tilemaps[self.level_num].width * GRID_PIXEL_SIZE or self.player.center_y < 0:
            self.reset()

        tree_collisions = self.player.collides_with_list(self.scene["trees"])

        if tree_collisions:
            for tree in tree_collisions:
                self.trees += 1
                self.collected_trees.append(tree)
                self.scene["trees"].remove(tree)

                self.warmth = self.clamp(self.warmth + 35, 0, 100)

        moved = False
        ice_touch = any([ice_sprite in hit_list for ice_sprite in self.scene["ice"]]) and self.physics_engine.can_jump()

        if self.window.keyboard[arcade.key.UP] or self.window.keyboard[arcade.key.SPACE]:
            if time.perf_counter() - self.last_jump >= PLAYER_JUMP_COOLDOWN and self.physics_engine.can_jump():
                self.last_jump = time.perf_counter()
                self.player.change_y = PLAYER_JUMP_SPEED

        if self.window.keyboard[arcade.key.LEFT] or self.window.keyboard[arcade.key.A]:
            moved = True
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
            self.direction = "left"

        elif self.window.keyboard[arcade.key.RIGHT] or self.window.keyboard[arcade.key.D]:
            moved = True
            self.player.change_x = PLAYER_MOVEMENT_SPEED
            self.direction = "right"
        
        else:
            if ice_touch:
                on_left_right_diagonal = any([True for hit in hit_list if hit in self.left_right_diagonal_sprites])
                on_right_left_diagonal = any([True for hit in hit_list if hit in self.right_left_diagonal_sprites])

                if on_left_right_diagonal or (self.direction == "right" and not on_right_left_diagonal):
                    self.player.change_x = self.clamp(self.player.change_x * 0.75, PLAYER_MOVEMENT_SPEED * 0.4, PLAYER_MOVEMENT_SPEED)
                else:
                    self.player.change_x = self.clamp(self.player.change_x * 0.75, -PLAYER_MOVEMENT_SPEED, -PLAYER_MOVEMENT_SPEED * 0.4)
            else:
                self.player.change_x = 0
            
        if moved and ice_touch:
            self.player.change_x *= 1.5

        self.warmth = self.clamp(self.warmth - 0.15, 0, 100)

        if self.warmth < 40:
            if self.settings.get("sfx", True) and not self.freeze_player.playing:
                self.freeze_player.play()
        else:
            if self.settings.get("sfx", True):
                self.freeze_player.pause()

        if self.player.change_y > 0:
            self.change_player_animation(player_jump_animation)
        elif abs(self.player.change_x) > PLAYER_MOVEMENT_SPEED * 0.4:
            self.change_player_animation(player_walk_animation)
        else:
            self.change_player_animation(player_still_animation)

        for level_text in self.level_texts:
            if level_text.change_to_when_hit and self.player.rect.intersection(level_text.rect):
                level_text.text = level_text.change_to_when_hit

        self.player.update_animation()

    def update_data_file(self):
        with open("data.json", "w") as file:
            file.write(json.dumps({
                "high_score": self.high_score,
                "tries": self.tries
            }, indent=4))

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
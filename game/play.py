import arcade, arcade.gui, json

from utils.constants import FOLLOW_DECAY_CONST, GRAVITY, PLAYER_MOVEMENT_SPEED, PLAYER_JUMP_SPEED, GRID_PIXEL_SIZE
from utils.preload import tile_map, player_still_animation, player_jump_animation, player_walk_animation, freeze_sound, background_sound

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Keeping the warmth")

        self.camera_sprites = arcade.Camera2D()
        self.camera_bounds = self.window.rect
        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.scene = self.create_scene()
        self.spawn_position = tile_map.object_lists["spawn"][0].shape

        player_x, player_y = self.spawn_position

        self.player = arcade.TextureAnimationSprite(animation=player_still_animation, center_x=player_x, center_y=player_y)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player, gravity_constant=GRAVITY,
            walls=[self.scene["walls"], self.scene["ice"]]
        )

        self.warmth = 100

        self.direction = "right"

        self.scene.add_sprite("Player", self.player)

        with open("settings.json", "r") as file:
            self.settings = json.load(file)

        if self.settings.get("sfx", True):        
            self.freeze_player = freeze_sound.play(loop=True, volume=self.settings.get("sfx_volume", 100) / 100)
            self.freeze_player.pause()

            self.background_player = background_sound.play(loop=True, volume=self.settings.get("sfx_volume", 100) / 100)

    def on_show_view(self):
        super().on_show_view()

    def reset(self):
        self.warmth = 100
        self.player.change_x, self.player.change_y = 0, 0
        self.player.position = self.spawn_position

    def create_scene(self) -> arcade.Scene:
        self.camera_bounds = arcade.LRBT(
            self.window.width/2.0,
            tile_map.width * GRID_PIXEL_SIZE - self.window.width/2.0,
            self.window.height/2.0,
            tile_map.height * GRID_PIXEL_SIZE
        )

        return arcade.Scene.from_tilemap(tile_map)

    def on_draw(self):
        self.clear()

        with self.camera_sprites.activate():
            self.scene.draw()

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

        if self.warmth <= 0:
            self.reset()

        if self.player.collides_with_list(self.scene["spikes"]):
            self.reset()

        if self.player.center_x < 0 or self.player.center_x > tile_map.width * GRID_PIXEL_SIZE:
            self.reset()
        elif self.player.center_y < 0:
            self.reset()

        ice_touch = any([ice_sprite in hit_list for ice_sprite in self.scene["ice"]]) and self.physics_engine.can_jump()

        if self.window.keyboard[arcade.key.UP] or self.window.keyboard[arcade.key.SPACE]:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED

        if self.window.keyboard[arcade.key.LEFT] or self.window.keyboard[arcade.key.A]:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
            self.direction = "left"

        elif self.window.keyboard[arcade.key.RIGHT] or self.window.keyboard[arcade.key.D]:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
            self.direction = "right"
        
        else:
            if ice_touch:
                if self.direction == "right":
                    self.player.change_x = self.clamp(self.player.change_x * 0.7, PLAYER_MOVEMENT_SPEED * 0.05, PLAYER_MOVEMENT_SPEED)
                else:
                    self.player.change_x = self.clamp(self.player.change_x * 0.7, -PLAYER_MOVEMENT_SPEED, -PLAYER_MOVEMENT_SPEED * 0.05)
            else:
                self.player.change_x = 0
            
        if ice_touch:
            self.player.change_x *= 1.3

        if abs(self.player.rect.distance_from_bounds(self.spawn_position)) > GRID_PIXEL_SIZE * 5:
            if self.settings.get("sfx", True) and not self.freeze_player.playing:
                self.freeze_player.play()
            self.warmth = self.clamp(self.warmth - 0.1, 0, 100)
        else:
            if self.settings.get("sfx", True):
                self.freeze_player.pause()
            self.warmth = self.clamp(self.warmth + 0.05, 0, 100)

        if self.player.change_y > 0:
            self.change_player_animation(player_jump_animation)
        elif abs(self.player.change_x) > 0:
            self.change_player_animation(player_walk_animation)
        else:
            self.change_player_animation(player_still_animation)

        self.player.update_animation()
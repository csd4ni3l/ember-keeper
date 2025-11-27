import arcade, arcade.gui

from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Keeping the warmth")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.warmth = 100

        self.camera = arcade.Camera2D()
        self.spritelist = arcade.SpriteList()

    def on_show_view(self):
        super().on_show_view()
        self.warmth_meter = self.anchor.add(arcade.gui.UISlider(value=100, max_value=100, min_value=0), anchor_x="center", anchor_y="bottom")

    def on_update(self, delta_time):
        self.warmth_meter.value = self.warmth

    def on_draw(self):
        super().on_draw()

        with self.camera.activate():
            self.spritelist.draw()
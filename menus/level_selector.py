import arcade, arcade.gui

from utils.constants import AVAILABLE_LEVELS, button_style
from utils.preload import button_texture, button_hovered_texture

class LevelSelector(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Selecting Level...")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=5), anchor_x="center", anchor_y="center")

    def on_show_view(self):
        super().on_show_view()
        
        self.box.add(arcade.gui.UILabel(text="Level Selector", font_size=28))

        for n in range(AVAILABLE_LEVELS):
            button = self.box.add(arcade.gui.UITextureButton(text=f"Level {n + 1}", width=self.window.width / 2, height=self.window.height / 10, texture=button_texture, texture_hovered=button_hovered_texture, style=button_style))
            button.on_click = lambda event, n=n: self.play_level(n)

    def play_level(self, n):
        from game.play import Game
        self.window.show_view(Game(self.pypresence_client, n))

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))
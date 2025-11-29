import arcade, arcade.gui, json, os

from utils.constants import AVAILABLE_LEVELS, button_style
from utils.preload import button_texture, button_hovered_texture

class Statistics(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()
        
        self.pypresence_client = pypresence_client

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.box = self.anchor.add(arcade.gui.UIBoxLayout(align="left"), anchor_x="center", anchor_y="top")

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.data = json.load(file)
        else:
            self.data = {
                f"{level_num}_best_time": 9999
                for level_num in range(AVAILABLE_LEVELS)
            }
            self.data.update({
                f"{level_num}_tries": 0
                for level_num in range(AVAILABLE_LEVELS)
            })

        self.total_tries = sum([self.data[f"{level_num}_tries"] for level_num in range(AVAILABLE_LEVELS)])

    def on_show_view(self):
        super().on_show_view()

        self.back_button = arcade.gui.UITextureButton(texture=button_texture, texture_hovered=button_hovered_texture, text='<--', style=button_style, width=100, height=50)
        self.back_button.on_click = lambda event: self.main_exit()
        self.anchor.add(self.back_button, anchor_x="left", anchor_y="top", align_x=10, align_y=-10)

        self.box.add(arcade.gui.UILabel("Statistics", font_size=40))

        self.box.add(arcade.gui.UISpace(height=self.window.height / 15))

        for level_num in range(AVAILABLE_LEVELS):
            self.box.add(arcade.gui.UILabel(f"Level {level_num + 1}", font_size=32))
            self.box.add(arcade.gui.UILabel(f"High Score: {self.data[f'{level_num}_best_time']}", font_size=24))
            self.box.add(arcade.gui.UILabel(f"Tries: {self.data[f'{level_num}_tries']}", font_size=24))
            self.box.add(arcade.gui.UISpace(height=self.window.height / 15))

        self.box.add(arcade.gui.UILabel(f"Total", font_size=32))
        self.box.add(arcade.gui.UILabel(f"Total Tries: {self.total_tries}", font_size=24))

    def main_exit(self):
        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))
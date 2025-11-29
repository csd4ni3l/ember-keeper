import arcade.gui, arcade, os

# Get the directory where this module is located
_module_dir = os.path.dirname(os.path.abspath(__file__))
_assets_dir = os.path.join(os.path.dirname(_module_dir), 'assets')

button_texture = arcade.gui.NinePatchTexture(64 // 4, 64 // 4, 64 // 4, 64 // 4, arcade.load_texture(os.path.join(_assets_dir, 'graphics', 'button.png')))
button_hovered_texture = arcade.gui.NinePatchTexture(64 // 4, 64 // 4, 64 // 4, 64 // 4, arcade.load_texture(os.path.join(_assets_dir, 'graphics', 'button_hovered.png')))

def animation_from(path_list):
    return arcade.TextureAnimation([
        arcade.TextureKeyframe(arcade.load_texture(path))
        for path in path_list
    ])

player_walk_animation = animation_from([os.path.join(_assets_dir, 'graphics', 'KenneyNewPlatformerPack', 'character', 'character_green_walk_a.png'), os.path.join(_assets_dir, 'graphics', 'KenneyNewPlatformerPack', 'character', 'character_green_walk_b.png')])
player_still_animation = animation_from([os.path.join(_assets_dir, 'graphics', 'KenneyNewPlatformerPack', 'character', 'character_green_idle.png')])
player_jump_animation = animation_from([os.path.join(_assets_dir, 'graphics', 'KenneyNewPlatformerPack', 'character', 'character_green_jump.png')])
player_duck_animation = animation_from([os.path.join(_assets_dir, 'graphics', 'KenneyNewPlatformerPack', 'character', 'character_green_duck.png')])

background_sound = arcade.Sound(os.path.join(_assets_dir, "sound", "background.mp3"))
freeze_sound = arcade.Sound(os.path.join(_assets_dir, "sound", "freeze.wav"))

tilemaps = [arcade.load_tilemap(os.path.join(_assets_dir, "levels", tilemap)) for tilemap in os.listdir(os.path.join(_assets_dir, "levels"))]
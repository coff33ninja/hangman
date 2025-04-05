import os
import shutil
from asset_manager import AssetManager

class ThemeManager:
    def __init__(self, theme_folder="assets/themes", default_theme="default"):
        self.theme_folder = theme_folder
        self.current_theme = default_theme
        self.assets = {}
        self.asset_manager = AssetManager()

    def validate_theme(self, theme_name):
        """
        Validate if a theme has all required assets.
        """
        theme_path = os.path.join(self.theme_folder, theme_name)
        required_files = ["background.png", "font.ttf", "sounds", "hangman_images"]
        for file in required_files:
            if not os.path.exists(os.path.join(theme_path, file)):
                raise FileNotFoundError(f"Missing '{file}' in theme '{theme_name}'.")

    def load_theme(self, theme_name):
        theme_path = os.path.join(self.theme_folder, theme_name)
        if not os.path.exists(theme_path):
            raise FileNotFoundError(f"Theme '{theme_name}' not found.")
        self.validate_theme(theme_name)
        self.current_theme = theme_name
        self.assets = {
            "background": os.path.join(theme_path, "background.png"),
            "font": os.path.join(theme_path, "font.ttf"),
            "sounds": os.path.join(theme_path, "sounds"),
            "hangman_images": os.path.join(theme_path, "hangman_images"),
        }

    def get_asset(self, asset_type):
        return self.assets.get(asset_type, None)

    def get_available_themes(self):
        """
        Return a list of available themes.
        """
        return [d for d in os.listdir(self.theme_folder) if os.path.isdir(os.path.join(self.theme_folder, d))]

    def generate_themes(self):
        """
        Generate default themes if they do not exist.
        """
        default_themes = {
            "default": {
                "background": "assets/default_background.png",
                "font": "assets/default_font.ttf",
                "sounds": "assets/default_sounds",
                "hangman_images": "assets/default_hangman_images",
            },
            "spooky": {
                "background": "assets/spooky_background.png",
                "font": "assets/spooky_font.ttf",
                "sounds": "assets/spooky_sounds",
                "hangman_images": "assets/spooky_hangman_images",
            },
        }

        for theme_name, assets in default_themes.items():
            theme_path = os.path.join(self.theme_folder, theme_name)
            if not os.path.exists(theme_path):
                os.makedirs(theme_path)
                tasks = []
                for asset_type, asset_path in assets.items():
                    if asset_type == "background" and not os.path.exists(asset_path):
                        tasks.append((self.asset_manager.generate_placeholder_image, (asset_path, (800, 600), (200, 200, 200), f"{theme_name} Background")))
                    elif asset_type == "hangman_images" and not os.path.exists(asset_path):
                        tasks.append((self.asset_manager.generate_hangman_images, (asset_path, 10)))  # 10 stages
                    elif asset_type == "sounds" and not os.path.exists(asset_path):
                        os.makedirs(asset_path)
                        print(f"Generated placeholder sounds folder for theme '{theme_name}'.")
                    elif os.path.exists(asset_path):
                        self.copy_default_assets(asset_path, theme_path)
                    else:
                        print(f"Missing asset: {asset_path}. Placeholder not generated for this type.")
                self.asset_manager.generate_assets(tasks)

    def copy_default_assets(self, src_folder, dest_folder):
        """
        Copy default assets from the source folder to the destination folder.
        """
        if os.path.exists(src_folder):
            for item in os.listdir(src_folder):
                src_path = os.path.join(src_folder, item)
                dest_path = os.path.join(dest_folder, item)
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy(src_path, dest_path)

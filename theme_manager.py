import os

class ThemeManager:
    def __init__(self, theme_folder="assets/themes", default_theme="default"):
        self.theme_folder = theme_folder
        self.current_theme = default_theme
        self.assets = {}

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

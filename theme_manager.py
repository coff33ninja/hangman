import os

class ThemeManager:
    def __init__(self, theme_dir="assets/themes"):
        self.theme_dir = theme_dir
        self.current_theme = "default"

    def load_theme(self, theme_name):
        """
        Load a theme by name.
        """
        theme_path = os.path.join(self.theme_dir, theme_name)
        if os.path.exists(theme_path):
            self.current_theme = theme_name
            return True
        return False

    def get_available_themes(self):
        """
        Return a list of available themes.
        """
        return [d for d in os.listdir(self.theme_dir) if os.path.isdir(os.path.join(self.theme_dir, d))]

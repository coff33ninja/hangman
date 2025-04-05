import os
from PIL import Image, ImageDraw
from threading import Thread

class AssetManager:
    def __init__(self, asset_folder="assets"):
        self.asset_folder = asset_folder

    def generate_placeholder_image(self, filepath, size=(800, 600), color=(200, 200, 200), text="Placeholder"):
        """
        Generate a placeholder image with the specified size and color.
        """
        img = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(img)
        text_bbox = draw.textbbox((0, 0), text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text(
            ((size[0] - text_width) // 2, (size[1] - text_height) // 2),
            text,
            fill=(0, 0, 0),
        )
        img.save(filepath)

    def draw_hangman_stage(self, draw, stage, width, height):
        """
        Draw the Hangman body parts for a specific stage.
        :param draw: The ImageDraw object.
        :param stage: The current stage of the Hangman.
        :param width: The width of the image.
        :param height: The height of the image.
        """
        base_x, base_y = width // 2, int(height * 0.8)
        pole_height = int(height * 0.6)
        head_radius = int(width * 0.1)

        # Draw the gallows
        if stage >= 1:
            draw.line((base_x - 50, base_y, base_x + 50, base_y), fill="black", width=5)  # Base
        if stage >= 2:
            draw.line((base_x, base_y, base_x, base_y - pole_height), fill="black", width=5)  # Vertical pole
        if stage >= 3:
            draw.line((base_x, base_y - pole_height, base_x + 100, base_y - pole_height), fill="black", width=5)  # Top beam
        if stage >= 4:
            draw.line((base_x + 100, base_y - pole_height, base_x + 100, base_y - pole_height + 50), fill="black", width=5)  # Rope

        # Draw the Hangman body parts
        if stage >= 5:
            draw.ellipse((base_x + 75, base_y - pole_height + 50, base_x + 125, base_y - pole_height + 100), outline="black", width=5)  # Head
        if stage >= 6:
            draw.line((base_x + 100, base_y - pole_height + 100, base_x + 100, base_y - pole_height + 200), fill="black", width=5)  # Torso
        if stage >= 7:
            draw.line((base_x + 100, base_y - pole_height + 125, base_x + 75, base_y - pole_height + 175), fill="black", width=5)  # Left arm
        if stage >= 8:
            draw.line((base_x + 100, base_y - pole_height + 125, base_x + 125, base_y - pole_height + 175), fill="black", width=5)  # Right arm
        if stage >= 9:
            draw.line((base_x + 100, base_y - pole_height + 200, base_x + 75, base_y - pole_height + 275), fill="black", width=5)  # Left leg
        if stage >= 10:
            draw.line((base_x + 100, base_y - pole_height + 200, base_x + 125, base_y - pole_height + 275), fill="black", width=5)  # Right leg

    def generate_hangman_images(self, folder, stages=10):
        """
        Generate placeholder Hangman images for the specified number of stages.
        """
        os.makedirs(folder, exist_ok=True)
        for i in range(1, stages + 1):
            filepath = os.path.join(folder, f"stage_{i}.png")
            img = Image.new("RGB", (200, 400), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            self.draw_hangman_stage(draw, i, 200, 400)
            img.save(filepath)

    def generate_hangman_assets(self, base_folder, difficulties):
        """
        Generate Hangman assets for different difficulty levels.
        :param base_folder: The base folder where Hangman assets will be stored.
        :param difficulties: A dictionary where keys are difficulty levels and values are the number of stages.
        """
        for difficulty, stages in difficulties.items():
            folder = os.path.join(base_folder, f"level{difficulty}")
            self.generate_hangman_images(folder, stages=stages)

    def generate_assets(self, tasks):
        """
        Generate assets using threading for efficiency.
        :param tasks: A list of tasks, where each task is a tuple (function, args).
        """
        threads = []
        for func, args in tasks:
            thread = Thread(target=func, args=args)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

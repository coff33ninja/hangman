from PIL import Image, ImageDraw, ImageFont
import os

def create_hangman_images(
    output_dir="assets/images", levels=3, stages_per_level=[7, 10, 14]
):
    """
    Generate placeholder Hangman images for each difficulty level and stage.
    """
    os.makedirs(output_dir, exist_ok=True)

    width, height = 400, 400  # Image dimensions

    # Load a custom font
    font_path = "custom_font.ttf"  # Path to your custom font file
    font_size = 20  # Set the desired font size
    font = ImageFont.truetype(font_path, font_size)

    for level in range(1, levels + 1):
        for stage in range(stages_per_level[level - 1]):
            # Create a blank white image
            img = Image.new("RGB", (width, height), "white")
            draw = ImageDraw.Draw(img)

            # Draw placeholder Hangman figure based on the stage
            draw_hangman(draw, stage, width, height)

            # Add text to indicate level and stage
            text = f"Level {level} - Stage {stage}"
            text_bbox = draw.textbbox((0, 0), text, font=font)

            text_width, text_height = (
                text_bbox[2] - text_bbox[0],
                text_bbox[3] - text_bbox[1],
            )

            draw.text(
                ((width - text_width) // 2, height - text_height - 10),
                text,
                fill="black",
                font=font,
            )

            # Save the image
            img.save(os.path.join(output_dir, f"level{level}_stage{stage}.png"))

def draw_hangman(draw, stage, width, height):
    """
    Draw a simple Hangman figure based on the stage.
    """
    # Draw the gallows
    draw.line([(50, 350), (350, 350)], fill="black", width=3)  # Base
    draw.line([(100, 350), (100, 50)], fill="black", width=3)  # Pole
    draw.line([(100, 50), (250, 50)], fill="black", width=3)  # Top beam
    draw.line([(250, 50), (250, 100)], fill="black", width=3)  # Rope

    # Draw the Hangman figure progressively
    if stage >= 1:  # Head
        draw.ellipse([(230, 100), (270, 140)], outline="black", width=3)
    if stage >= 2:  # Body
        draw.line([(250, 140), (250, 220)], fill="black", width=3)
    if stage >= 3:  # Left arm
        draw.line([(250, 160), (220, 190)], fill="black", width=3)
    if stage >= 4:  # Right arm
        draw.line([(250, 160), (280, 190)], fill="black", width=3)
    if stage >= 5:  # Left leg
        draw.line([(250, 220), (220, 270)], fill="black", width=3)
    if stage >= 6:  # Right leg
        draw.line([(250, 220), (280, 270)], fill="black", width=3)
    if stage >= 7:  # Left eye
        draw.line([(240, 110), (245, 115)], fill="black", width=2)
        draw.line([(245, 110), (240, 115)], fill="black", width=2)
    if stage >= 8:  # Right eye
        draw.line([(255, 110), (260, 115)], fill="black", width=2)
        draw.line([(260, 110), (255, 115)], fill="black", width=2)
    if stage >= 9:  # Mouth
        draw.arc([(240, 120), (260, 130)], start=0, end=180, fill="black", width=2)
    if stage >= 10:  # Nose
        draw.line([(250, 115), (250, 120)], fill="black", width=2)
    if stage >= 11:  # Left hand
        draw.ellipse([(215, 185), (225, 195)], outline="black", width=2)
    if stage >= 12:  # Right hand
        draw.ellipse([(275, 185), (285, 195)], outline="black", width=2)
    if stage >= 13:  # Left foot
        draw.ellipse([(215, 265), (225, 275)], outline="black", width=2)
    if stage >= 14:  # Right foot
        draw.ellipse([(275, 265), (285, 275)], outline="black", width=2)

if __name__ == "__main__":
    create_hangman_images()

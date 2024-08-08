from PIL import Image, ImageDraw, ImageFont
import io

def generate_avatar(username):
    # Configuration
    size = (150, 150)
    bg_color = (100, 100, 100)
    text_color = (255, 255, 255)
    
    # Création de l'image
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Charger une police de caractères avec une taille de 100 pixels
    font = ImageFont.truetype("arial.ttf", 125)
    
    # Calculer la position du texte pour le centrer
    text = username[0].upper()
    
    # Utiliser textbbox au lieu de textsize
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # Calculer les coordonnées du centre de l'image
    center_x = size[0] / 2
    center_y = size[1] / 2
    
    # Calculer la position du texte pour centrer le milieu de la lettre
    text_x = center_x - text_width / 2
    text_y = center_y - text_height / 2
    
    # Dessiner le texte sur l'image
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Sauvegarder l'image dans un buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer
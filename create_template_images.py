import os
from PIL import Image

# Create template preview images for the customize page
def create_template_previews():
    images_dir = '/home/ubuntu/interactive_lesson_app/src/static/images'
    
    # Default template preview
    default_img = Image.new('RGB', (300, 200), (106, 17, 203))
    default_img.save(os.path.join(images_dir, 'template_default.jpg'))
    
    # Colorful template preview
    colorful_img = Image.new('RGB', (300, 200), (255, 8, 68))
    colorful_img.save(os.path.join(images_dir, 'template_colorful.jpg'))
    
    # Minimal template preview
    minimal_img = Image.new('RGB', (300, 200), (67, 67, 67))
    minimal_img.save(os.path.join(images_dir, 'template_minimal.jpg'))

if __name__ == "__main__":
    create_template_previews()
    print("Template preview images created successfully!")

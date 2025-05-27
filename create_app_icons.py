from PIL import Image, ImageDraw

# Create app icons for PWA
def create_app_icons():
    # Create 192x192 icon
    icon_small = Image.new('RGB', (192, 192), (106, 17, 203))
    draw = ImageDraw.Draw(icon_small)
    # Add a simple design
    draw.rectangle([(40, 40), (152, 152)], fill=(255, 255, 255))
    draw.rectangle([(60, 60), (132, 132)], fill=(106, 17, 203))
    # Save the icon
    icon_small.save('/home/ubuntu/interactive_lesson_app/src/static/images/icon-192x192.png')
    
    # Create 512x512 icon
    icon_large = Image.new('RGB', (512, 512), (106, 17, 203))
    draw = ImageDraw.Draw(icon_large)
    # Add a simple design
    draw.rectangle([(106, 106), (406, 406)], fill=(255, 255, 255))
    draw.rectangle([(160, 160), (352, 352)], fill=(106, 17, 203))
    # Save the icon
    icon_large.save('/home/ubuntu/interactive_lesson_app/src/static/images/icon-512x512.png')
    
    print("App icons created successfully!")

if __name__ == "__main__":
    create_app_icons()

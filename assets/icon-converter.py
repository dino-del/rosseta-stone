from PIL import Image

img = Image.open("assets/icon.png")
img.save("assets/icon.ico", format="ICO", sizes=[(64, 64)])

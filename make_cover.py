"""Builds the Workshop cover of Coalition Demands (768x768, in the style of the Quartermaster, Child Education and
Export Bans covers): the rider of cover_full.png at the top, the title in the game's Cormorant Garamond and the main
features below. Writes cover.png, the square preview; cover_full.png goes to the page's gallery as it is.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = "E:/SteamLibrary/steamapps/common/Europa Universalis V/game/"
FONTS = GAME + "loading_screen/fonts/CormorantGaramond/"
SIZE = 768
ART_H = 540
GOLD = (232, 196, 120)
TEXT = (226, 222, 210)
FEATURES = "Return Conquests  ·  Revive Countries  ·  Ease Antagonism"


def gradient(top, bottom):
    im = Image.new("RGB", (SIZE, SIZE))
    d = ImageDraw.Draw(im)
    for y in range(SIZE):
        t = y / (SIZE - 1)
        d.line([(0, y), (SIZE, y)], fill=tuple(round(a + (b - a) * t) for a, b in zip(top, bottom)))
    return im


def main():
    cover = gradient((40, 30, 24), (20, 15, 12))

    # the rider, from the pointing hand to the horse's nose, faded into the background at its bottom
    full = Image.open(os.path.join(HERE, "cover_full.png")).convert("RGB")
    scale = SIZE / 545
    art = full.crop((200, 0, 745, 540)).resize((SIZE, round(540 * scale)), Image.LANCZOS)
    art = art.crop((0, 0, SIZE, ART_H))
    fade = Image.new("L", art.size, 255)
    d = ImageDraw.Draw(fade)
    for y in range(ART_H - 190, ART_H):
        d.line([(0, y), (SIZE, y)], fill=round(255 * (ART_H - y) / 190))
    cover.paste(art, (0, 0), fade)

    d = ImageDraw.Draw(cover)
    title = ImageFont.truetype(FONTS + "CormorantGaramond-SemiBold.ttf", 96)
    sub = ImageFont.truetype(FONTS + "CormorantGaramond-Medium.ttf", 30)
    t = "Coalition Demands"
    w = d.textlength(t, font=title)
    d.text(((SIZE - w) / 2 + 3, 540 + 3), t, font=title, fill=(10, 8, 6))
    d.text(((SIZE - w) / 2, 540), t, font=title, fill=GOLD)
    d.line([(150, 666), (SIZE - 150, 666)], fill=GOLD, width=2)
    w = d.textlength(FEATURES, font=sub)
    assert w < SIZE - 40, w
    d.text(((SIZE - w) / 2, 682), FEATURES, font=sub, fill=TEXT)

    cover.save(os.path.join(HERE, "cover.png"))
    print("cover.png", cover.size)


if __name__ == "__main__":
    main()

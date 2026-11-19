#!/usr/bin/env python3
"""Compose the 19 November 2026 world-news front page (1024x1024).

Build-time tool (Pillow is available on this machine). The entry itself is
the composed JPEG; main.py only copies it into /output at grade time, which
is the pattern the kit's starter uses and the rules allow.

Layout (1024x1024):
  masthead  0..118    date + kicker
  hero      118..446  Gulf: US strikes an IRGC site, Iran fires back
  band      446..668  Shenzhen: Trump, Xi and Putin meet (full width)
  row 3     668..946  Venezuela / US Senate / DR Congo Ebola
  ticker    946..1024 also-today strip (facts from the same five stories)
All text is drawn with PIL (crisp vector type) over dark scrims, so nothing
is garbled the way AI-generated text would be. No randomness anywhere:
same inputs give the same bytes every run.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
ASSETS = "assets"
OUT = "entry.png"

SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (11, 22, 34)
AMBER = (255, 179, 0)
WHITE = (255, 255, 255)
SOFT = (226, 232, 238)


def font(path, size):
    return ImageFont.truetype(path, size)


def cover_crop(im, tw, th, focus_y=0.5):
    """Resize + crop so the image exactly fills tw x th.

    focus_y (0..1) places the crop window vertically: 0.5 = centred.
    """
    sw, sh = im.size
    scale = max(tw / sw, th / sh)
    im = im.resize((round(sw * scale), round(sh * scale)), Image.LANCZOS)
    x = (im.width - tw) // 2
    slack = im.height - th
    y = round(slack * focus_y) if slack > 0 else 0
    return im.crop((x, y, x + tw, y + th))


def scrim(draw_img, box, max_alpha=205):
    """Bottom-up black gradient scrim inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box
    height = y1 - y0
    overlay = Image.new("RGBA", (x1 - x0, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(height):
        a = int(max_alpha * (i / height) ** 1.6)
        od.line([(0, i), (x1 - x0, i)], fill=(0, 0, 0, a))
    draw_img.paste(overlay, (x0, y0), overlay)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap to a pixel width."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def panel(base, img_path, box, tag, headline, sub, head_size=27, focus_y=0.5):
    x0, y0, x1, y1 = box
    tw, th = x1 - x0, y1 - y0
    im = Image.open(img_path).convert("RGB")
    base.paste(cover_crop(im, tw, th, focus_y), (x0, y0))
    scrim(base, (x0, y0 + th // 3, x1, y1))
    d = ImageDraw.Draw(base)
    pad = 16
    tx = x0 + pad
    # sub-line at the very bottom
    sub_f = font(SANS, 19)
    sub_lines = wrap(d, sub, sub_f, tw - 2 * pad)
    sub_h = len(sub_lines) * 24
    # headline above the sub-line (up to 2 lines)
    head_f = font(SANS_BOLD, head_size)
    head_lines = wrap(d, headline, head_f, tw - 2 * pad)[:2]
    head_h = len(head_lines) * (head_size + 4)
    # tag above the headline, on a dark chip so it reads on any photo
    tag_f = font(SANS_BOLD, 17)
    ty = y1 - pad - sub_h - head_h - 26
    tag_w = d.textlength(tag, font=tag_f)
    chip = Image.new("RGBA", (int(tag_w) + 16, 26), (7, 16, 26, 200))
    base.paste(chip, (tx - 8, ty - 3), chip)
    d = ImageDraw.Draw(base)
    d.text((tx, ty), tag, font=tag_f, fill=AMBER)
    hy = ty + 26
    for ln in head_lines:
        d.text((tx, hy), ln, font=head_f, fill=WHITE,
               stroke_width=1, stroke_fill=(0, 0, 0))
        hy += head_size + 4
    sy = hy + 2
    for ln in sub_lines:
        d.text((tx, sy), ln, font=sub_f, fill=SOFT,
               stroke_width=1, stroke_fill=(0, 0, 0))
        sy += 24


def main():
    base = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(base)

    # ---- masthead ------------------------------------------------------
    d.text((W // 2, 30), "THE WORLD IN ONE DAY",
           font=font(SANS_BOLD, 21), fill=AMBER, anchor="ma")
    d.text((W // 2, 56), "THURSDAY 19 NOVEMBER 2026",
           font=font(SERIF_BOLD, 52), fill=WHITE, anchor="ma")
    d.line([(24, 116), (W - 24, 116)], fill=AMBER, width=3)

    # ---- hero: the Gulf -----------------------------------------------
    panel(base,
          f"{ASSETS}/media-generation-hero-gulf-0-62e28cde-d9e5-4a9b-846f-8644c1480ee8.webp",
          (0, 118, W, 446),
          "THE GULF",
          "US STRIKES IRGC SITE ON QESHM ISLAND",
          "Iran fires on a US air base in Kuwait and targets in Bahrain; "
          "Kuwait's defences intercept drones and no American personnel "
          "were wounded, US Central Command says.",
          head_size=36, focus_y=0.45)

    # ---- band: Shenzhen -----------------------------------------------
    panel(base,
          f"{ASSETS}/media-generation-panel-shenzhen-faces-0-73fd507e-8b6c-4107-a797-ff98d6d267ec.webp",
          (0, 446, W, 668),
          "SHENZHEN  •  APEC",
          "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
          "First meeting of the three leaders, at the APEC summit.",
          head_size=34, focus_y=0.1)

    # ---- bottom row: Venezuela / Senate / Ebola -----------------------
    gx, gy = 10, 668
    cw, ch, gut = 328, 278, 10
    panel(base,
          f"{ASSETS}/media-generation-panel-caracas-0-76e1da07-9b80-4b9a-9937-584e003afc08.webp",
          (gx, gy, gx + cw, gy + ch),
          "CARACAS",
          "TIES RESTORED AFTER 21 YEARS",
          "US Defence Secretary Hegseth visits Caracas; the deal covers "
          "training and intelligence sharing.",
          head_size=23)
    panel(base,
          f"{ASSETS}/media-generation-panel-senate-0-20e5f680-9974-4430-a605-3288a028dea0.webp",
          (gx + cw + gut, gy, gx + 2 * cw + gut, gy + ch),
          "WASHINGTON",
          "DEMOCRATS TAKE THE SENATE",
          "Mary Peltola beats Dan Sullivan in Alaska; Democrats hold "
          "56 seats, 9 flipped.",
          head_size=23)
    panel(base,
          f"{ASSETS}/media-generation-panel-ebola-0-4534cf3e-4a88-41aa-8933-8adba9742bf1.webp",
          (gx + 2 * cw + 2 * gut, gy, gx + 3 * cw + 2 * gut, gy + ch),
          "DR CONGO",
          "EBOLA OUT OF CONTROL",
          "WHO: the outbreak is uncontrolled after six months; 11,000 "
          "infected, 5,400 dead.",
          head_size=23)

    # ---- ticker --------------------------------------------------------
    d.rectangle([(0, 956), (W, H)], fill=(7, 16, 26))
    d.line([(0, 956), (W, 956)], fill=AMBER, width=2)
    d.text((24, 964),
           "ALSO TODAY:   Ships on fire in the Strait of Hormuz  •  Saudi-led coalition strikes Yemen",
           font=font(SANS_BOLD, 18), fill=AMBER)
    d.text((24, 989),
           "Kuwait's air defences intercepted drones  •  Trump holds separate talks with Putin",
           font=font(SANS, 18), fill=SOFT)

    # JPEG bytes in entry.png: the gate reads the format from the magic
    # bytes, and the name stays entry.png either way. JPEG keeps the
    # photographic front page well under the 1 MiB cap; PNG was 1.17 MB
    # for yesterday's page.
    base.save(OUT, format="JPEG", quality=88, optimize=True)
    print(f"wrote {OUT} {base.size}")


if __name__ == "__main__":
    main()

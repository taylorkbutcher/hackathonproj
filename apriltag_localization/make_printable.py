"""Make exact-size printable PDF for 100mm tag36h11 tags."""
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from PIL import Image
import os

TAG_IDS = [0, 1, 2]
TAG_SIZE_MM = 100
SRC_DIR = os.path.join(os.path.dirname(__file__), "tags")
OUT = os.path.join(os.path.dirname(__file__), "tags_100mm.pdf")

# Upscale tiny 10x10 PNGs with NEAREST for crisp print
for tid in TAG_IDS:
    src = os.path.join(SRC_DIR, f"tag36h11_{tid}.png")
    img = Image.open(src).convert("RGB")
    big = img.resize((1000, 1000), Image.NEAREST)
    big.save(os.path.join(SRC_DIR, f"tag36h11_{tid}_big.png"))

c = canvas.Canvas(OUT, pagesize=(210*mm, 297*mm))  # A4
for tid in TAG_IDS:
    big_path = os.path.join(SRC_DIR, f"tag36h11_{tid}_big.png")
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, 270*mm, f"tag36h11 id {tid} - outer black = 100mm")
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, 262*mm, "Print at 100% / Actual size / No scaling. Measure black square.")
    # center 100mm tag
    x = (210 - TAG_SIZE_MM) / 2 * mm
    y = 120*mm
    c.drawImage(big_path, x, y, width=TAG_SIZE_MM*mm, height=TAG_SIZE_MM*mm)
    # 100mm reference ruler
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, 100*mm, "Reference (should measure 100mm):")
    c.line(20*mm, 95*mm, (20+100)*mm, 95*mm)
    for i in range(0, 101, 10):
        c.line((20+i)*mm, 95*mm, (20+i)*mm, 92*mm)
        c.drawString((19+i)*mm, 88*mm, str(i))
    c.showPage()
c.save()
print(f"Wrote {OUT}")

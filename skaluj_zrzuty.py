from PIL import Image
import glob, os

SRC = "/mnt/d/projekty/pdf_sign_remover/zrzuty_store"
OUT = os.path.join(SRC, "store_1366x768")
os.makedirs(OUT, exist_ok=True)

CANVAS = (1366, 768)
BG = (243, 243, 243)  # jasnoszare tlo Windows 11

for f in sorted(glob.glob(os.path.join(SRC, "*.png"))):
    im = Image.open(f).convert("RGB")
    w, h = im.size
    # skala tak, by okno zajmowalo max ~78% wysokosci canvas, zachowujac ostrosc (bez powiekszania ponad 1.6x)
    scale = min((CANVAS[1]*0.82)/h, (CANVAS[0]*0.85)/w, 1.6)
    nw, nh = int(w*scale), int(h*scale)
    im2 = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", CANVAS, BG)
    x = (CANVAS[0]-nw)//2
    y = (CANVAS[1]-nh)//2
    canvas.paste(im2, (x, y))
    name = os.path.basename(f)
    outp = os.path.join(OUT, name)
    canvas.save(outp, "PNG")
    print(f"{name}: {w}x{h} -> canvas {CANVAS[0]}x{CANVAS[1]} (okno {nw}x{nh}, skala {scale:.2f})")

print("Gotowe. Zrzuty do Store:", OUT)

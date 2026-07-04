"""Generator ladnej ikony dla PDF Signature Remover.
Koncepcja: biala kartka dokumentu z etykieta PDF + okragla pieczec/podpis,
ktora jest USUWANA (czerwony ukosnik przekreslajacy pieczec).
Renderowane w duzej skali (supersampling) i skalowane do rozmiarow Store.
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = "/mnt/d/projekty/pdf_sign_remover/msix_pkg/Assets"
os.makedirs(OUT, exist_ok=True)

# Kolory
GRANAT_1 = (26, 45, 90)      # gorny gradient tla
GRANAT_2 = (14, 26, 56)      # dolny gradient tla
KARTKA = (248, 249, 251)
KARTKA_CIEN = (205, 212, 224)
ROG = (222, 228, 238)        # zawiniety rog
PDF_CZERW = (208, 48, 45)
LINIA_TEKST = (170, 180, 198)
PIECZEC = (40, 120, 190)     # niebieska pieczec podpisu
PIECZEC_JASNA = (90, 160, 220)
USUN_CZERW = (228, 62, 55)   # ukosnik "usun"
BIALY = (255, 255, 255)

def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size-1, size-1], radius=radius, fill=255)
    return m

def gradient_bg(size, c1, c2):
    bg = Image.new("RGB", (size, size), c1)
    top = Image.new("RGB", (size, size), c2)
    mask = Image.new("L", (size, size))
    md = mask.load()
    for y in range(size):
        v = int(255 * y / size)
        for x in range(size):
            md[x, y] = v
    bg.paste(top, (0, 0), mask)
    return bg

def render(size):
    SS = 4  # supersampling
    S = size * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # tlo z gradientem + zaokraglone rogi
    bg = gradient_bg(S, GRANAT_1, GRANAT_2).convert("RGBA")
    radius = int(S * 0.18)
    mask = rounded_mask(S, radius)
    img.paste(bg, (0, 0), mask)

    d = ImageDraw.Draw(img)

    # --- Kartka dokumentu (biala, z lekkim cieniem) ---
    kw = int(S * 0.42)   # szerokosc kartki
    kh = int(S * 0.52)   # wysokosc
    kx = int(S * 0.17)
    ky = int(S * 0.16)
    r = int(S * 0.03)
    fold = int(S * 0.12)  # rozmiar zawinietego rogu

    # cien kartki
    cien = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cien)
    off = int(S*0.012)
    dc.rounded_rectangle([kx+off, ky+off, kx+kw+off, ky+kh+off], radius=r, fill=(0,0,0,70))
    cien = cien.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(S*0.012))
    img.alpha_composite(cien)

    # korpus kartki - ksztalt z zawinietym gornym-prawym rogiem
    body = [
        (kx, ky+r),
        (kx, ky+kh-r),
    ]
    # uzyjemy prostokata zaokraglonego + wytniemy rog recznie: prosciej rysujemy polygon
    d.rounded_rectangle([kx, ky, kx+kw, ky+kh], radius=r, fill=KARTKA)
    # zawiniety rog (gorny prawy): trojkat w kolorze tla + zakladka
    d.polygon([(kx+kw-fold, ky), (kx+kw, ky+fold), (kx+kw-fold, ky+fold)], fill=ROG)
    d.line([(kx+kw-fold, ky), (kx+kw-fold, ky+fold), (kx+kw, ky+fold)], fill=KARTKA_CIEN, width=max(2,SS))

    # --- linie tekstu na dokumencie (mniej i grubsze dla malych ikon) ---
    lx = kx + int(kw*0.14)
    lw = int(kw*0.72)
    ly = ky + int(kh*0.28)
    n_linii = 4 if size >= 100 else 2
    gap = int(kh*0.13)
    grub_linii = int(S*0.012) if size >= 100 else int(S*0.020)
    for i in range(n_linii):
        w = lw if i < n_linii-1 else int(lw*0.55)
        d.rounded_rectangle([lx, ly+i*gap, lx+w, ly+i*gap+grub_linii],
                            radius=int(S*0.006), fill=LINIA_TEKST)

    # --- etykieta PDF (czerwony prostokat u dolu kartki) ---
    ew = int(kw*0.52); eh = int(kh*0.17)
    ex = kx + int(kw*0.14); ey = ky + kh - eh - int(kh*0.12)
    d.rounded_rectangle([ex, ey, ex+ew, ey+eh], radius=int(S*0.02), fill=PDF_CZERW)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(eh*0.62))
    except Exception:
        f = ImageFont.load_default()
    txt = "PDF"
    tb = d.textbbox((0,0), txt, font=f)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    d.text((ex+(ew-tw)/2 - tb[0], ey+(eh-th)/2 - tb[1]), txt, font=f, fill=BIALY)

    # --- Pieczec / podpis (okragla, prawy dolny rog, nachodzi na kartke) ---
    pr = int(S*0.175)   # promien
    # umiesc srodek tak, by caly okrag + przekreslenie mial margines od krawedzi
    margines = int(S*0.11)
    pcx = S - margines - pr
    pcy = S - margines - pr
    # obwodka pieczeci (dwa okregi)
    d.ellipse([pcx-pr, pcy-pr, pcx+pr, pcy+pr], fill=(255,255,255,235))
    d.ellipse([pcx-pr, pcy-pr, pcx+pr, pcy+pr], outline=PIECZEC, width=max(3,int(S*0.012)))
    ir = int(pr*0.72)
    d.ellipse([pcx-ir, pcy-ir, pcx+ir, pcy+ir], outline=PIECZEC_JASNA, width=max(2,int(S*0.006)))
    PODPIS_KOLOR = (20, 60, 110)   # ciemny granat - mocny kontrast na bialym kole
    # "podpis" - wyrazny, plynny, ukosny zawijas (imitacja odrecznego podpisu)
    pts = []
    n = 90
    for i in range(n+1):
        t = i/n
        x = pcx - ir*0.74 + t*(ir*1.48)
        y = (pcy + math.sin(t*math.pi*1.6)*ir*0.34
             - t*ir*0.24
             + math.sin(t*math.pi*3.2)*ir*0.07)
        pts.append((x, y))
    grubosc_podpis = max(3, int(S*0.017))
    d.line(pts, fill=PODPIS_KOLOR, width=grubosc_podpis, joint="curve")

    # --- Znak USUWANIA: czerwone kolo z ukosnikiem nachodzace na pieczec ---
    # (symbol "zakaz/usun" - jednoznacznie: podpis jest usuwany)
    d.line([(pcx-pr*0.78, pcy+pr*0.78), (pcx+pr*0.78, pcy-pr*0.78)],
           fill=USUN_CZERW, width=max(5,int(S*0.030)))

    # zredukuj (antyalias)
    img = img.resize((size, size), Image.LANCZOS)
    return img

# Rozmiary Store/MSIX
zadania = {
    "Square44x44Logo.png": 44,
    "Square71x71Logo.png": 71,
    "Square150x150Logo.png": 150,
    "Square310x310Logo.png": 310,
    "StoreLogo.png": 50,
}
for nazwa, s in zadania.items():
    render(s).save(os.path.join(OUT, nazwa))
    print(f"{nazwa}: {s}x{s}")

# Wide310x150 - ikona wysrodkowana na granatowym tle + nazwa
def wide():
    W, H = 310, 150
    SS = 4
    img = gradient_bg(H*SS, GRANAT_1, GRANAT_2).convert("RGBA").resize((W*SS,H*SS))
    # ikona po lewej
    ic = render(H).resize((int(H*0.8), int(H*0.8)), Image.LANCZOS)
    base = Image.new("RGBA", (W*SS, H*SS), (0,0,0,0))
    bg = gradient_bg(max(W,H)*SS, GRANAT_1, GRANAT_2).convert("RGBA").resize((W*SS,H*SS))
    base.alpha_composite(bg)
    icb = ic.resize((int(H*0.8*SS), int(H*0.8*SS)), Image.LANCZOS)
    base.alpha_composite(icb, (int(H*0.1*SS), int(H*0.1*SS)))
    d = ImageDraw.Draw(base)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(20*SS))
        f2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(13*SS))
    except Exception:
        f = f2 = ImageFont.load_default()
    tx = int(H*0.95*SS)
    d.text((tx, int(52*SS)), "PDF Signature", font=f, fill=BIALY)
    d.text((tx, int(78*SS)), "Remover", font=f, fill=BIALY)
    base = base.resize((W,H), Image.LANCZOS)
    base.convert("RGB").save(os.path.join(OUT, "Wide310x150Logo.png"))
    print("Wide310x150Logo.png: 310x150")
wide()

# SplashScreen 620x300 - ikona + nazwa na srodku
def splash():
    W, H = 620, 300
    SS = 2
    base = gradient_bg(max(W,H)*SS, GRANAT_1, GRANAT_2).convert("RGBA").resize((W*SS,H*SS))
    ic = render(150).resize((int(140*SS), int(140*SS)), Image.LANCZOS)
    base.alpha_composite(ic, (int((W/2-70)*SS), int(40*SS)))
    d = ImageDraw.Draw(base)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(30*SS))
    except Exception:
        f = ImageFont.load_default()
    txt = "PDF Signature Remover"
    tb = d.textbbox((0,0), txt, font=f)
    tw = tb[2]-tb[0]
    d.text(((W*SS-tw)/2 - tb[0], int(210*SS)), txt, font=f, fill=BIALY)
    base = base.resize((W,H), Image.LANCZOS)
    base.convert("RGB").save(os.path.join(OUT, "SplashScreen.png"))
    print("SplashScreen.png: 620x300")
splash()

print("GOTOWE - wszystkie assety zregenerowane")

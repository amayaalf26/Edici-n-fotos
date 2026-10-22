"""Uso: python editar.py [foto.jpg ...]   (sin argumentos procesa todo lo de estilo.json)
Lee originales/ y estilo.json, exporta a salida/<nombre>_historia.jpg (1080x1920)."""
import json, sys
from pathlib import Path
import cv2, numpy as np

def papel(img):
    # quita sombras/degradado de luz dividiendo por el fondo estimado, luego da contraste
    g = img.astype(np.float32)
    bg = cv2.medianBlur(cv2.resize(img, None, fx=.25, fy=.25), 31)
    bg = cv2.GaussianBlur(cv2.resize(bg, img.shape[1::-1]), (0, 0), 25).astype(np.float32)
    out = np.clip(g / (bg + 1) * 235, 0, 255)
    out = np.clip((out - 40) * 1.25, 0, 255)          # negros mas profundos
    out = out * np.array([0.96, 0.985, 1.0])          # calidez suave (BGR)
    return out.astype(np.uint8)

def pantalla(img):
    # solo sube un poco la luz de las sombras y el contraste; sin realce local (evita halos)
    g = (img / 255.0) ** 0.85
    return np.clip((g - 0.04) * 1.12 * 255, 0, 255).astype(np.uint8)

def sharpen(img):
    return cv2.addWeighted(img, 1.4, cv2.GaussianBlur(img, (0, 0), 2), -0.4, 0)

def historia(img, W, H, m):
    h, w = img.shape[:2]
    # fondo: la misma foto difuminada, rellena todo el formato 9:16
    s = max(W / w, H / h)
    bg = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    y0, x0 = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
    bg = cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 45)
    bg = (bg * 0.55).astype(np.uint8)
    # foto nitida centrada dentro de los margenes
    s = min((W - 2 * m) / w, (H - 2 * m) / h)
    fg = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_LANCZOS4)
    fh, fw = fg.shape[:2]
    y, x = (H - fh) // 2, (W - fw) // 2
    bg[y:y + fh, x:x + fw] = fg
    return bg

def main():
    cfg = json.load(open("estilo.json"))
    W, H = cfg["tamano"]
    Path("salida").mkdir(exist_ok=True)
    nombres = sys.argv[1:] or list(cfg["fotos"])
    for n in nombres:
        n = Path(n).name
        c = cfg["fotos"][n]
        img = cv2.imread(f"originales/{n}")
        h, w = img.shape[:2]
        x1, y1, x2, y2 = c["recorte"]
        img = img[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]
        img = papel(img) if c["modo"] == "papel" else pantalla(img)
        out = historia(sharpen(img) if c["modo"] == "papel" else img, W, H, cfg["margen"])
        dest = f"salida/{Path(n).stem}_historia.jpg"
        cv2.imwrite(dest, out, [cv2.IMWRITE_JPEG_QUALITY, cfg["calidad"]])
        print("OK", dest, out.shape[1], "x", out.shape[0])

main()

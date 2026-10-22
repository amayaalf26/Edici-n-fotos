"""Une el versículo (pantalla) y la reflexión (libro) en UNA sola historia 1080x1920.
Uso: python componer.py   ->  salida/historia_gratitud_pablo.jpg"""
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from editar import papel, pantalla, sharpen

W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf"
FUENTE = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONDO_ARRIBA, FONDO_ABAJO = (28, 38, 56), (16, 22, 34)
DORADO = (212, 175, 110)
BLANCO = (245, 243, 238)

def recorte(nombre, caja, modo):
    img = cv2.imread(f"originales/{nombre}")
    h, w = img.shape[:2]
    x1, y1, x2, y2 = caja
    img = img[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]
    img = papel(img) if modo == "papel" else pantalla(img)
    img = sharpen(img) if modo == "papel" else img
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

def tarjeta(lienzo, img, ancho, y, radio=22):
    img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
    x = (W - ancho) // 2
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((x, y + 10, x + ancho, y + img.height + 10), radio, fill=(0, 0, 0, 120))
    lienzo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)))
    mascara = Image.new("L", img.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *img.size), radio, fill=255)
    lienzo.paste(img.convert("RGBA"), (x, y), mascara)
    return y + img.height

def centrado(d, texto, y, fuente, color, espaciado=0):
    ancho = sum(d.textlength(c, font=fuente) + espaciado for c in texto) - espaciado
    x = (W - ancho) / 2
    for c in texto:
        d.text((x, y), c, font=fuente, fill=color)
        x += d.textlength(c, font=fuente) + espaciado

def main():
    # fondo degradado vertical
    t = np.linspace(0, 1, H)[:, None, None]
    fondo = (np.array(FONDO_ARRIBA) * (1 - t) + np.array(FONDO_ABAJO) * t).astype(np.uint8)
    lienzo = Image.fromarray(np.repeat(fondo, W, axis=1)).convert("RGBA")
    d = ImageDraw.Draw(lienzo)

    # titulo (debajo de la zona superior que tapa la interfaz de Instagram)
    centrado(d, "PALABRA PARA HOY", 215, ImageFont.truetype(FUENTE, 26), DORADO, 6)
    centrado(d, "Gratitud de Pablo", 262, ImageFont.truetype(FONT % "Bold", 96), BLANCO)
    d.line((W / 2 - 60, 392, W / 2 + 60, 392), fill=DORADO, width=4)
    centrado(d, "1 Timoteo 1:12-17", 412, ImageFont.truetype(FONT % "Italic", 38), DORADO)

    # versiculo (captura de pantalla) y reflexion del libro
    verso = recorte("pantalla_1timoteo.jpg", [0.03, 0.225, 0.97, 0.895], "pantalla")
    y = tarjeta(lienzo, verso, 920, 490)
    d.text((70, y + 40), "", font=None)
    libro = recorte("libro_octubre22.jpg", [0.06, 0.05, 0.855, 0.205], "papel")
    y = tarjeta(lienzo, libro, 920, y + 36)
    print("termina en y =", y, "(limite seguro ~1670)")

    lienzo.convert("RGB").save("salida/historia_gratitud_pablo.jpg", quality=95)

main()

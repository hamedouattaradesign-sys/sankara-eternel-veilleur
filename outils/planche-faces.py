#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trace la planche des deux faces du monument, dans la langue demandée.

Les cotes viennent du plan FACE PORTRAIT INDICE E et du dossier institutionnel
signé du 17 août 2026. Le dessin est fait en millimètres réels puis mis à
l'échelle : les bossages de 139 mm sur une face de 700 mm se touchent presque,
et c'est ce que l'on doit voir.

Usage :  python3 outils/planche-faces.py fr > planche.svg
         python3 outils/planche-faces.py it > planche.svg
         python3 outils/planche-faces.py en > planche.svg
"""

import sys

E = 0.20                       # px par millimètre
LF, HF = 700.0, 2000.0         # face : 700 × 2000 mm
R = 139.0 / 2                  # rayon d'un bossage
CX = [99.5, 266.5, 433.5, 600.5]

TRAIT = "#5c564d"; CORTEN = "#8a4f2b"; ACIER = "#f4efe6"; CREUX = "#1f1c18"; ENCRE = "#1c1a17"
X_T, X_P, Y0 = 72.0, 322.0, 64.0

MOTS = {
    "fr": {
        "texture": "FACE DE TEXTURE", "portrait": "FACE PORTRAIT",
        "opposees": "deux faces opposées",
        "colonnes": "quatre colonnes", "rangees": "onze rangées",
        "n44": "44 bossages", "n28": "28 bossages",
        "aucune": "aucune découpe", "haut_bas": "4 en haut + 24 en bas",
        "traversants": "portrait, nom et signature traversants",
        "visage": "visage", "nom": "nom et dates",
        "a_visage": "visage découpé", "a_nom": "nom et dates", "a_sig": "signature",
        "total": "2 faces de texture + 2 faces portrait  =  144 bossages",
        "titre": "Planche des deux types de face du monument",
        "desc": ("Élévation à plat, aux cotes réelles. À gauche, une face de texture : quatre "
                 "colonnes de bossages sur onze rangées, soit quarante-quatre bossages, sans "
                 "aucune découpe. À droite, une face portrait : une rangée haute de quatre "
                 "bossages, le visage et le bloc du nom découpés au travers de la tôle, puis "
                 "vingt-quatre bossages en partie basse, et la signature de l'artiste découpée "
                 "au pied. Les deux faces de texture et les deux faces portrait totalisent cent "
                 "quarante-quatre bossages."),
    },
    "it": {
        "texture": "FACCIA A TESSITURA", "portrait": "FACCIA CON IL VOLTO",
        "opposees": "due facce opposte",
        "colonnes": "quattro colonne", "rangees": "undici file",
        "n44": "44 bugne", "n28": "28 bugne",
        "aucune": "nessun taglio", "haut_bas": "4 in alto + 24 in basso",
        "traversants": "volto, nome e firma passanti",
        "visage": "volto", "nom": "nome e date",
        "a_visage": "volto tagliato", "a_nom": "nome e date", "a_sig": "firma",
        "total": "2 facce a tessitura + 2 facce con il volto  =  144 bugne",
        "titre": "Tavola dei due tipi di faccia del monumento",
        "desc": ("Prospetto in piano, alle quote reali. A sinistra, una faccia a tessitura: "
                 "quattro colonne di bugne su undici file, quarantaquattro bugne in tutto, senza "
                 "alcun taglio. A destra, una faccia con il volto: una fila alta di quattro "
                 "bugne, il volto e il blocco del nome tagliati da parte a parte nella lamiera, "
                 "poi ventiquattro bugne nella parte bassa, e la firma dell'artista tagliata al "
                 "piede. Le due facce a tessitura e le due facce con il volto sommano "
                 "centoquarantaquattro bugne."),
    },
    "en": {
        "texture": "TEXTURED FACE", "portrait": "PORTRAIT FACE",
        "opposees": "two opposite faces",
        "colonnes": "four columns", "rangees": "eleven rows",
        "n44": "44 bosses", "n28": "28 bosses",
        "aucune": "no cut at all", "haut_bas": "4 above + 24 below",
        "traversants": "face, name and signature cut through",
        "visage": "face", "nom": "name and dates",
        "a_visage": "face cut through", "a_nom": "name and dates", "a_sig": "signature",
        "total": "2 textured faces + 2 portrait faces  =  144 bosses",
        "titre": "Drawing of the two types of face of the monument",
        "desc": ("Flat elevation, at true dimensions. On the left, a textured face: four columns "
                 "of bosses over eleven rows, that is forty-four bosses, with no cut at all. On "
                 "the right, a portrait face: a top row of four bosses, the face and the name "
                 "block cut clean through the plate, then twenty-four bosses in the lower part, "
                 "and the artist's signature cut at the foot. The two textured faces and the two "
                 "portrait faces come to one hundred and forty-four bosses in all."),
    },
}


def px(v):
    return v * E


def tracer(langue):
    m = MOTS[langue]
    bas = Y0 + px(HF)
    p = []

    def eti(x, y, t, ancre="middle", taille=11, couleur=TRAIT, gras=False):
        return ('<text x="%.1f" y="%.1f" text-anchor="%s" font-size="%d" fill="%s"%s '
                'font-family="system-ui, sans-serif">%s</text>'
                % (x, y, ancre, taille, couleur, ' font-weight="700"' if gras else "", t))

    def face(x):
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" stroke="%s" '
                'stroke-width="1.4"/>' % (x, Y0, px(LF), px(HF), ACIER, TRAIT))

    def bugne(x, cx_mm, cy_mm):
        return ('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" fill-opacity="0.9"/>'
                % (x + px(cx_mm), Y0 + px(cy_mm), px(R), CORTEN))

    def decoupe(x, x0, y0, l, h, label=None):
        out = ['<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"/>'
               % (x + px(x0), Y0 + px(y0), px(l), px(h), CREUX)]
        if label:
            out.append('<text x="%.2f" y="%.2f" text-anchor="middle" font-size="7" '
                       'fill="#ece6db" font-family="system-ui, sans-serif">%s</text>'
                       % (x + px(x0 + l / 2), Y0 + px(y0 + h / 2) + 2.5, label))
        return out

    # Face de texture : 4 colonnes × 11 rangées = 44
    p.append(eti(X_T + px(LF) / 2, 26, m["texture"], gras=True, couleur=ENCRE))
    p.append(eti(X_T + px(LF) / 2, 44, m["opposees"], taille=9))
    p.append(face(X_T))
    entraxe = 165.0
    premier = (HF - entraxe * 10) / 2
    for r in range(11):
        for cx in CX:
            p.append(bugne(X_T, cx, premier + r * entraxe))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8"/>'
             % (X_T, bas + 12, X_T + px(LF), bas + 12, TRAIT))
    p.append(eti(X_T + px(LF) / 2, bas + 26, m["colonnes"], taille=9))
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.8"/>'
             % (X_T - 13, Y0, X_T - 13, bas, TRAIT))
    p.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="9" fill="%s" '
             'font-family="system-ui, sans-serif" transform="rotate(-90 %.1f %.1f)">%s</text>'
             % (X_T - 18, Y0 + px(HF) / 2, TRAIT, X_T - 18, Y0 + px(HF) / 2, m["rangees"]))
    p.append(eti(X_T + px(LF) / 2, bas + 48, m["n44"], couleur=CORTEN, taille=13, gras=True))
    p.append(eti(X_T + px(LF) / 2, bas + 64, m["aucune"], taille=9))

    # Face portrait : 4 + 24 = 28
    p.append(eti(X_P + px(LF) / 2, 26, m["portrait"], gras=True, couleur=ENCRE))
    p.append(eti(X_P + px(LF) / 2, 44, m["opposees"], taille=9))
    p.append(face(X_P))
    for cx in CX:
        p.append(bugne(X_P, cx, 95.0))
    p += decoupe(X_P, 155, 190, 390, 552, m["visage"])
    p += decoupe(X_P, 90, 772, 520, 180, m["nom"])
    for r in range(6):
        for cx in CX:
            p.append(bugne(X_P, cx, 1039.5 + r * 165.0))
    p += decoupe(X_P, 180, 1940, 340, 40)

    droite = X_P + px(LF) + 7
    for y_mm, texte in ((466, m["a_visage"]), (862, m["a_nom"]), (1960, m["a_sig"])):
        y = Y0 + px(y_mm)
        p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="0.7"/>'
                 % (X_P + px(LF) - 2, y, droite - 2, y, TRAIT))
        p.append(eti(droite + 2, y + 3, texte, ancre="start", taille=8))

    p.append(eti(X_P + px(LF) / 2, bas + 26, m["haut_bas"], taille=9))
    p.append(eti(X_P + px(LF) / 2, bas + 48, m["n28"], couleur=CORTEN, taille=13, gras=True))
    p.append(eti(X_P + px(LF) / 2, bas + 64, m["traversants"], taille=9))

    p.append('<line x1="72" y1="%.1f" x2="462" y2="%.1f" stroke="#ddd5c7" stroke-width="1"/>'
             % (bas + 82, bas + 82))
    p.append(eti(267, bas + 104, m["total"], taille=13, couleur=ENCRE, gras=True))

    hv = int(bas + 120)
    return ('<svg viewBox="0 0 534 %d" width="534" height="%d" role="img" '
            'aria-labelledby="schema-titre schema-desc" xmlns="http://www.w3.org/2000/svg">\n'
            '  <title id="schema-titre">%s</title>\n'
            '  <desc id="schema-desc">%s</desc>\n' % (hv, hv, m["titre"], m["desc"])
            + "\n".join("  " + e for e in p) + "\n</svg>")


# Contrôles arithmétiques : le dessin ne sort pas si le compte ne tombe pas juste.
assert 4 * 11 == 44 and 4 + 4 * 6 == 28 and 2 * 28 + 2 * 44 == 144 == 12 * 12
from datetime import date
_d, _f = date(1983, 8, 4), date(1987, 10, 15)
assert (_f.year - _d.year, _f.month - _d.month, _f.day - _d.day) == (4, 2, 11)

if __name__ == "__main__":
    langue = sys.argv[1] if len(sys.argv) > 1 else "fr"
    if langue not in MOTS:
        raise SystemExit("Langue inconnue : %s (fr ou it)" % langue)
    sys.stdout.write(tracer(langue))

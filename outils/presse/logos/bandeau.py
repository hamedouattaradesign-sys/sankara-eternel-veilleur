#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compose la bande des partenaires du cartel, à partir des fichiers d'origine.

Elle était jusqu'ici découpée d'un seul bloc dans l'invitation de l'Ambassade.
C'était commode et c'était faux : la bande portait une ancienne version du logo
du Comité, et rien ne permettait d'en remplacer un seul.

Chaque marque est maintenant un fichier à part. Celle dont on n'a pas l'original
est signalée dans LISEZ-MOI.md, et se remplace sans toucher aux autres.

Usage :  python3 outils/presse/logos/bandeau.py
"""

import os
import subprocess
import sys
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))

# Hauteur de travail. La bande est ensuite posée sur 128 mm de large dans le
# cartel : à 300 points par pouce cela fait 1512 points, et on compose plus
# large pour garder de la marge à l'impression.
HAUTEUR = 300
ECART = 150          # l'espace entre deux marques
MARGE = 40           # le blanc de bord

# Une marque trop large écraserait les autres : au-delà, on réduit sur la
# largeur plutôt que sur la hauteur.
LARGEUR_MAX = int(HAUTEUR * 2.1)

MARQUES = [
    # (fichier, part de la hauteur) — le poids optique n'est pas la hauteur
    # brute : un logo tout en texte doit être un peu plus petit qu'un emblème.
    ("pcim-ints.pdf", 1.00),
    ("musee-national-burkina-faso.png", 0.78),
    ("aes-confederation-etats-sahel.png", 1.00),
    ("municipio-iii-roma.webp", 0.74),
]


def charger(nom):
    chemin = os.path.join(ICI, nom)
    if nom.lower().endswith(".pdf"):
        # Le vectoriel est rendu large, puis réduit : les bords restent nets.
        sortie = os.path.join(ICI, ".rendu-" + os.path.splitext(nom)[0])
        subprocess.run(["pdftocairo", "-png", "-r", "400", "-transp",
                        "-f", "1", "-l", "1", chemin, sortie],
                       check=True, capture_output=True)
        chemin = sortie + "-1.png"
        im = Image.open(chemin).convert("RGBA")
        os.unlink(chemin)
        return im
    return Image.open(chemin).convert("RGBA")


def rogner(im):
    """Enlève le blanc et le transparent autour de la marque."""
    fond = Image.new("RGBA", im.size, (255, 255, 255, 255))
    plat = Image.alpha_composite(fond, im).convert("RGB")
    # Tout ce qui n'est pas blanc appartient à la marque.
    masque = plat.point(lambda v: 255 if v < 248 else 0).convert("L")
    boite = masque.getbbox()
    return im.crop(boite) if boite else im


def composer():
    images = []
    for nom, part in MARQUES:
        im = rogner(charger(nom))
        h = int(HAUTEUR * part)
        l = round(im.width * h / im.height)
        if l > LARGEUR_MAX:
            l, h = LARGEUR_MAX, round(im.height * LARGEUR_MAX / im.width)
        images.append(im.resize((l, h), Image.LANCZOS))

    largeur = sum(i.width for i in images) + ECART * (len(images) - 1) + 2 * MARGE
    hauteur = HAUTEUR + 2 * MARGE
    bande = Image.new("RGBA", (largeur, hauteur), (255, 255, 255, 255))
    x = MARGE
    for im in images:
        bande.alpha_composite(im, (x, (hauteur - im.height) // 2))
        x += im.width + ECART
    return bande.convert("RGB")


if __name__ == "__main__":
    bande = composer()
    chemin = os.path.join(ICI, "bandeau-partenaires.png")
    bande.save(chemin, optimize=True)
    print("bandeau-partenaires.png  %d x %d, %d Ko"
          % (bande.width, bande.height, round(os.path.getsize(chemin) / 1024)))

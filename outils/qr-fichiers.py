#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Écrit le code QR du site en SVG et en PNG, dans statique/assets/presse/.

Le SVG est la source : il s'agrandit sans perdre un module, et c'est lui qu'il
faut donner à un imprimeur. Le PNG est là pour tout le reste — un message, une
présentation, un site qui n'accepte pas le vectoriel.

Le PNG est écrit à la main, avec zlib et struct : ce dépôt n'emporte aucune
bibliothèque tierce, et un code QR n'est qu'un damier.

Usage :  python3 outils/qr-fichiers.py
"""

import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qr  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "statique", "assets", "presse")
ADRESSE = "https://sankara.hamedouattara.com"

# Trente-six pixels par module : le PNG fait alors 1476 points de côté, soit
# 125 mm à 300 points par pouce. De quoi couvrir une affiche.
ECHELLE = 36
MARGE = 4            # la zone de silence minimale de la norme
ENCRE = (0x1c, 0x1a, 0x17)
PAPIER = (0xff, 0xff, 0xff)


def png(m, chemin):
    n = len(m)
    cote = (n + 2 * MARGE) * ECHELLE

    lignes = bytearray()
    for y in range(cote):
        lignes.append(0)                      # filtre « aucun »
        i = y // ECHELLE - MARGE
        if not (0 <= i < n):
            lignes.extend(bytes(PAPIER) * cote)
            continue
        ligne = bytearray()
        for x in range(cote):
            j = x // ECHELLE - MARGE
            sombre = 0 <= j < n and m[i][j]
            ligne.extend(ENCRE if sombre else PAPIER)
        lignes.extend(ligne)

    def bloc(nom, donnees):
        morceau = nom + donnees
        return (struct.pack(">I", len(donnees)) + morceau
                + struct.pack(">I", zlib.crc32(morceau) & 0xFFFFFFFF))

    entete = struct.pack(">IIBBBBB", cote, cote, 8, 2, 0, 0, 0)  # 8 bits, couleur vraie
    with open(chemin, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(bloc(b"IHDR", entete))
        f.write(bloc(b"IDAT", zlib.compress(bytes(lignes), 9)))
        f.write(bloc(b"IEND", b""))
    return cote


if __name__ == "__main__":
    print(qr.controler())
    m = qr.matrice(ADRESSE, "Q")

    chemin_svg = os.path.join(SORTIE, "qr-sankara-eternel-veilleur.svg")
    with open(chemin_svg, "w", encoding="utf-8") as f:
        f.write(qr.svg(ADRESSE, "Q", module=ECHELLE, marge=MARGE))
    print("  qr-sankara-eternel-veilleur.svg  %d Ko"
          % round(os.path.getsize(chemin_svg) / 1024))

    chemin_png = os.path.join(SORTIE, "qr-sankara-eternel-veilleur.png")
    cote = png(m, chemin_png)
    print("  qr-sankara-eternel-veilleur.png  %d x %d, %d Ko"
          % (cote, cote, round(os.path.getsize(chemin_png) / 1024)))

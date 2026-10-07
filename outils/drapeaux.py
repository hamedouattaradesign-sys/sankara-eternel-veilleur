#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Produit les deux drapeaux nationaux qui figurent au pied de chaque page.

Le monument est une œuvre burkinabè portée en Italie : les deux pays sont
nommés et montrés. Les couleurs sont celles des drapeaux, non celles de la
palette du site — un drapeau qu'on teinte pour l'accorder à une maquette n'est
plus un drapeau.

L'étoile du drapeau burkinabè est calculée, pas dessinée à l'estime : cinq
branches, pointe en haut, rayon intérieur dans le rapport du pentagramme
régulier. Le script refuse de produire si la géométrie est fausse.
"""
import io
import math
import os

L, H = 30.0, 20.0          # rapport 3:2, celui des deux drapeaux
DOSSIER = "statique/assets/img/identite"

# Couleurs officielles.
BF_ROUGE, BF_VERT, BF_OR = "#ef2b2d", "#009e49", "#fcd116"
IT_VERT, IT_BLANC, IT_ROUGE = "#008c45", "#f4f5f0", "#cd212a"


def etoile(cx, cy, rayon):
    """Les dix sommets d'une étoile à cinq branches, pointe en haut."""
    # Rapport du pentagramme régulier : r_int / r_ext = 1 / phi².
    phi = (1 + 5 ** 0.5) / 2
    interieur = rayon / (phi * phi)
    pts = []
    for k in range(10):
        r = rayon if k % 2 == 0 else interieur
        a = math.radians(-90 + 36 * k)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


_p = etoile(L / 2, H / 2, 4.2)
# La pointe haute doit être exactement au-dessus du centre, et l'étoile doit
# tenir dans le drapeau. Deux vérifications qui attrapent un signe inversé.
assert abs(_p[0][0] - L / 2) < 1e-9, "la pointe n'est pas dans l'axe"
assert _p[0][1] < H / 2, "l'étoile est retournée"
assert all(0 < x < L and 0 < y < H for x, y in _p), "l'étoile déborde"

_points = " ".join("%.3f,%.3f" % p for p in _p)

BURKINA = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" role="img">
<title>Drapeau du Burkina Faso</title>
<rect width="%g" height="%g" fill="%s"/>
<rect y="%g" width="%g" height="%g" fill="%s"/>
<polygon points="%s" fill="%s"/>
</svg>
""" % (L, H, L, H / 2, BF_ROUGE, H / 2, L, H / 2, BF_VERT, _points, BF_OR)

ITALIE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" role="img">
<title>Drapeau de l'Italie</title>
<rect width="%g" height="%g" fill="%s"/>
<rect x="%g" width="%g" height="%g" fill="%s"/>
<rect x="%g" width="%g" height="%g" fill="%s"/>
</svg>
""" % (L, H, L / 3, H, IT_VERT, L / 3, L / 3, H, IT_BLANC, 2 * L / 3, L / 3, H, IT_ROUGE)

if not os.path.isdir(DOSSIER):
    os.makedirs(DOSSIER)
for nom, contenu in (("drapeau-burkina.svg", BURKINA), ("drapeau-italie.svg", ITALIE)):
    chemin = os.path.join(DOSSIER, nom)
    io.open(chemin, "w", encoding="utf-8").write(contenu)
    print("  %s  %d octets" % (chemin, len(contenu.encode("utf-8"))))

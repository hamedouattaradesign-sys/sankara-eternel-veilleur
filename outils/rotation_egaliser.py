#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rend les trente vues de la rotation homogènes : cadrage, distance, lumière.

Première version : la fenêtre était calée sur la hauteur du monument et la
lumière corrigée aux deux tiers. Le monument ne sautait plus, mais il
respirait encore — la luminance allait de 81 à 155 d'une vue à l'autre, et
l'acier virait au chaud à mesure que le soleil descendait.

Trois corrections, dans cet ordre.

LA DISTANCE. La hauteur du monument est ramenée à une valeur unique, mais
elle est d'abord LISSÉE le long de la série : le repérage a sa propre
imprécision, de l'ordre du pour-cent, et la corriger vue par vue
réintroduirait le tremblement qu'on cherche à retirer. On lisse la hauteur et
le centre sur cinq vues glissantes, en circulaire puisque la rotation boucle.

LA LUMIÈRE, MESURÉE SUR L'ACIER ET NON SUR L'IMAGE. Égaliser l'image entière
ne marche pas ici : d'une vue à l'autre la part de ciel et d'ombre change, et
la correction transforme cette différence de contenu en différence
d'exposition. La luminance restait de 75 à 116 après coup. On mesure donc une
bande prise AU MILIEU DU MONUMENT, que le recadrage place au même endroit sur
les trente vues, et on ramène sa couleur à la médiane de la série. Ce qui
cesse de clignoter, c'est l'acier — c'est lui qu'on regarde. Le fond, lui, a
le droit de changer : on tourne autour d'un objet réel.

CE QUI N'EST PAS CORRIGÉ. La direction de la lumière. Le soleil tournait
pendant la prise, et aucune correction de couleur ne déplacera une ombre. On
le voit sur les faces de bossages, dont le relief se creuse puis s'adoucit.
C'est vrai, et c'est le sujet de l'œuvre.
"""
import numpy as np
from PIL import Image
import glob, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rotation_reperer import boite

# Les vues d'origine sont en pleine définition et ne vont pas dans le dépôt :
# on les lui passe en argument.
#   python3 outils/rotation_egaliser.py <dossier-des-vues> [dossier-de-sortie]
SOURCE = sys.argv[1] if len(sys.argv) > 1 else "rotation"
SORTIE = sys.argv[2] if len(sys.argv) > 2 else "statique/assets/img/visite"
L, H = 600, 800
PART_MONUMENT = 0.70
DESCENTE = 0.12
FORCE = 0.92                    # part de l'écart de lumière corrigée
LISSAGE = 5                     # vues glissantes sur le cadrage

def lisser_circulaire(v, n):
    v = np.asarray(v, dtype=float)
    noyau = np.ones(n) / n
    etendu = np.concatenate([v[-n:], v, v[:n]])
    return np.convolve(etendu, noyau, mode="same")[n:-n]

vues = sorted(glob.glob(os.path.join(SOURCE, "*.jpg")))
if not vues:
    raise SystemExit(f"aucune vue dans {SOURCE}/")
boites = [boite(c) for c in vues]

for i, b in enumerate(boites):
    if not (b and (b[2] - b[0]) > 0.10 * Image.open(vues[i]).size[0]):
        a, z = boites[i - 1], boites[(i + 1) % len(boites)]
        boites[i] = tuple((a[k] + z[k]) / 2 for k in range(4))
        print(f"vue {i+1:02d} : cadrage interpolé depuis ses voisines")

cx = lisser_circulaire([(b[0] + b[2]) / 2 for b in boites], LISSAGE)
cy = lisser_circulaire([(b[1] + b[3]) / 2 for b in boites], LISSAGE)
haut = lisser_circulaire([b[3] - b[1] for b in boites], LISSAGE)
haut_cible = float(np.median(haut))
print(f"hauteur du monument : {haut.min():.0f} à {haut.max():.0f} px, "
      f"ramenée à {haut_cible:.0f} pour les trente")

cadres = []
for chemin, x, y in zip(vues, cx, cy):
    im = Image.open(chemin).convert("RGB")
    W0, H0 = im.size
    hc = haut_cible / PART_MONUMENT
    lc = hc * L / H
    yy = y + DESCENTE * hc
    x = min(max(x, lc / 2), W0 - lc / 2)
    yy = min(max(yy, hc / 2), H0 - hc / 2)
    cadres.append(im.crop((round(x - lc / 2), round(yy - hc / 2),
                           round(x + lc / 2), round(yy + hc / 2)))
                    .resize((L, H), Image.LANCZOS))

# --- lumière, mesurée sur une bande prise au milieu du monument ------------
# Après recadrage, le monument occupe la même place sur les trente vues.
#
# LA BANDE EST BASSE, ET C'EST TOUT L'ENJEU. Prise à hauteur du portrait, elle
# mesurait du vide noir sur les deux faces à visage et de l'acier plein sur les
# deux autres : la correction se mettait alors à suivre la face présentée au
# lieu de suivre la lumière, et la rotation aurait battu au rythme des faces.
# Plus bas, sous le bloc du nom, les quatre faces portent des bossages. La
# bande y mesure toujours la même chose : de l'acier frappé.
BANDE = (0.44, 0.56, 0.45, 0.63)

piles = [np.asarray(c).astype(np.float32) for c in cadres]
def acier(p):
    x0, x1 = int(L * BANDE[0]), int(L * BANDE[1])
    y0, y1 = int(H * BANDE[2]), int(H * BANDE[3])
    return p[y0:y1, x0:x1].reshape(-1, 3)

med = np.array([np.median(acier(p), axis=0) for p in piles])
med_ref = np.median(med, axis=0)
print(f"acier : médiane RVB par vue de {med.min(axis=0).round(0)} "
      f"à {med.max(axis=0).round(0)}, ramenée à {med_ref.round(0)}")

# PAR COURBE, ET NON PAR FACTEUR. Multiplier toute l'image pour relever
# l'acier des vues à contre-jour brûlait le reste : l'herbe virait au jaune et
# le gravier au blanc. Une puissance corrige la même valeur de référence sans
# toucher aux extrêmes — le noir reste noir, le blanc reste blanc, et c'est
# le milieu du registre, là où se trouve l'acier, qui se déplace.
os.makedirs(SORTIE, exist_ok=True)
for i, (p, m) in enumerate(zip(piles, med)):
    vise = m + FORCE * (med_ref - m)
    a = p / 255.0
    for c in range(3):
        depart = min(max(m[c] / 255.0, 0.004), 0.996)
        arrivee = min(max(vise[c] / 255.0, 0.004), 0.996)
        gamma = np.log(arrivee) / np.log(depart)
        a[..., c] = np.power(a[..., c], gamma)
    Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).save(
        f"{SORTIE}/rotation-{i*12:03d}.webp", "WEBP", quality=56, method=6)

apres = []
for i in range(len(piles)):
    q = np.asarray(Image.open(f"{SORTIE}/rotation-{i*12:03d}.webp").convert("RGB")).astype(np.float32)
    apres.append(float(np.median(acier(q))))
total = sum(os.path.getsize(f"{SORTIE}/{f}") for f in os.listdir(SORTIE))
avant = [float(np.median(acier(p))) for p in piles]
print(f"luminance de l'acier — avant : {min(avant):.0f} à {max(avant):.0f}   "
      f"après : {min(apres):.0f} à {max(apres):.0f}")
print(f"{len(piles)} vues, {total//1024} Ko")

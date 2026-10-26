#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repère le monument sur chaque vue, par profil plutôt que par nuage de points.

Première tentative : masque de couleur puis centiles sur le nuage de pixels.
Elle échoue, parce que les briques des immeubles sont du même brun que l'acier
et qu'elles traversent tout le cadre : les centiles se font tirer vers elles.

Ici on raisonne sur la FORME. Le monument est la seule masse haute et continue
au centre de l'image. On compte les pixels de couleur acier colonne par
colonne, on cherche le plus long palier au-dessus de la moitié du maximum, et
ce palier donne la largeur. Les immeubles, eux, font un fond bas et étalé qui
ne forme pas de palier.
"""
import numpy as np
from PIL import Image, ImageDraw
import glob, os

FENETRE = (0.22, 0.78, 0.10, 0.92)

def masque_corten(rvb):
    r, v, b = (rvb[..., i].astype(np.float32) / 255 for i in range(3))
    mx, mn = np.maximum.reduce([r, v, b]), np.minimum.reduce([r, v, b])
    diff = np.maximum(mx - mn, 1e-6)
    sat = diff / np.maximum(mx, 1e-6)
    teinte = np.zeros_like(r)
    m = (mx == r); teinte[m] = ((v - b)[m] / diff[m]) % 6
    m = (mx == v); teinte[m] = ((b - r)[m] / diff[m]) + 2
    m = (mx == b); teinte[m] = ((r - v)[m] / diff[m]) + 4
    teinte /= 6
    return (teinte > 0.010) & (teinte < 0.090) & (sat > 0.30) & (mx > 0.06)

def lisser(p, n=15):
    noyau = np.ones(n) / n
    return np.convolve(p, noyau, mode="same")

def palier(profil, fraction=0.45):
    """Le plus long segment continu au-dessus d'une fraction du maximum."""
    seuil = profil.max() * fraction
    dessus = profil > seuil
    meilleur, debut, courant = (0, 0, 0), None, 0
    for i, d in enumerate(dessus):
        if d:
            if debut is None: debut = i
            courant += 1
            if courant > meilleur[0]: meilleur = (courant, debut, i)
        else:
            debut, courant = None, 0
    return meilleur[1], meilleur[2]

def boite(chemin):
    a = np.asarray(Image.open(chemin).convert("RGB"))
    H, W = a.shape[:2]
    x0, x1 = int(W * FENETRE[0]), int(W * FENETRE[1])
    y0, y1 = int(H * FENETRE[2]), int(H * FENETRE[3])
    m = masque_corten(a[y0:y1, x0:x1])
    if m.sum() < 2000:
        return None
    gx, dx = palier(lisser(m.sum(axis=0).astype(float), 25))
    bande = m[:, gx:dx + 1]
    hy, by = palier(lisser(bande.sum(axis=1).astype(float), 25), 0.35)
    return (gx + x0, hy + y0, dx + x0, by + y0)

if __name__ == "__main__":
    vignettes, lignes = [], []
    for c in sorted(glob.glob("rotation/*.jpg")):
        b = boite(c)
        im = Image.open(c).convert("RGB")
        W, H = im.size
        if b:
            d = ImageDraw.Draw(im)
            d.rectangle(b, outline=(0, 255, 60), width=14)
            lignes.append(f"{os.path.basename(c)}  cx={((b[0]+b[2])/2)/W:.3f}  "
                          f"l={(b[2]-b[0])/W:.3f}  h={(b[3]-b[1])/H:.3f}")
        else:
            lignes.append(f"{os.path.basename(c)}  AUCUNE")
        vignettes.append(im.resize((W // 7, H // 7), Image.LANCZOS))
    print("\n".join(lignes))
    lv, hv = vignettes[0].size
    planche = Image.new("RGB", (lv * 6, hv * 5), (20, 20, 20))
    for i, v in enumerate(vignettes):
        planche.paste(v, ((i % 6) * lv, (i // 6) * hv))
    planche.save("controle-reperage.jpg", quality=86)
    print("\nplanche de contrôle : controle-reperage.jpg", planche.size)

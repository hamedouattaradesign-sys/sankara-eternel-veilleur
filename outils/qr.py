#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trace un code QR, en SVG, sans aucune dépendance.

Ce site n'appelle aucun service extérieur, et ce qu'il imprime non plus. Un
code QR fabriqué par un générateur en ligne, c'est une adresse confiée à un
tiers qui la compte, parfois la redirige, et peut cesser d'exister. Celui-ci
est calculé ici, à partir de l'adresse, et ne mène qu'à elle.

Modes : octet seul, versions 1 à 6 (jusqu'à 134 octets utiles), quatre niveaux
de correction. C'est plus qu'il n'en faut pour une adresse de site, et cela
évite les blocs d'information de version des grandes tailles.

Usage :  python3 outils/qr.py "https://sankara.hamedouattara.com" > qr.svg
         python3 outils/qr.py ADRESSE NIVEAU FOND
         NIVEAU : L, M, Q ou H — Q par défaut.
         FOND   : la couleur du fond, blanc par défaut.
         python3 outils/qr.py --controle   vérifie le traceur contre la norme.
"""

import sys

# ——— Le corps fini GF(256), celui de la norme : polynôme 0x11D ——————————

_EXP = [0] * 512
_LOG = [0] * 256
_x = 1
for _i in range(255):
    _EXP[_i] = _x
    _LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    _EXP[_i] = _EXP[_i - 255]


def _mul(a, b):
    if a == 0 or b == 0:
        return 0
    return _EXP[_LOG[a] + _LOG[b]]


def _polynome_generateur(n):
    """Le polynôme générateur de Reed-Solomon pour n mots de contrôle."""
    g = [1]
    for i in range(n):
        g = _multiplier_polynomes(g, [1, _EXP[i]])
    return g


def _multiplier_polynomes(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            r[i + j] ^= _mul(a, b)
    return r


def _mots_de_controle(donnees, n):
    """Les n mots de contrôle de Reed-Solomon pour ce bloc de données."""
    g = _polynome_generateur(n)
    reste = list(donnees) + [0] * n
    for i in range(len(donnees)):
        coef = reste[i]
        if coef:
            for j, gj in enumerate(g):
                reste[i + j] ^= _mul(gj, coef)
    return reste[len(donnees):]


# ——— Les tables de la norme, versions 1 à 6 ——————————————————————————————

# version -> nombre total de mots de code
TOTAL = {1: 26, 2: 44, 3: 70, 4: 100, 5: 134, 6: 172}

# (version, niveau) -> (mots de contrôle par bloc, [(nombre de blocs, mots de données), …])
BLOCS = {
    (1, "L"): (7,  [(1, 19)]),            (1, "M"): (10, [(1, 16)]),
    (1, "Q"): (13, [(1, 13)]),            (1, "H"): (17, [(1, 9)]),
    (2, "L"): (10, [(1, 34)]),            (2, "M"): (16, [(1, 28)]),
    (2, "Q"): (22, [(1, 22)]),            (2, "H"): (28, [(1, 16)]),
    (3, "L"): (15, [(1, 55)]),            (3, "M"): (26, [(1, 44)]),
    (3, "Q"): (18, [(2, 17)]),            (3, "H"): (22, [(2, 13)]),
    (4, "L"): (20, [(1, 80)]),            (4, "M"): (18, [(2, 32)]),
    (4, "Q"): (26, [(2, 24)]),            (4, "H"): (16, [(4, 9)]),
    (5, "L"): (26, [(1, 108)]),           (5, "M"): (24, [(2, 43)]),
    (5, "Q"): (18, [(2, 15), (2, 16)]),   (5, "H"): (22, [(2, 11), (2, 12)]),
    (6, "L"): (18, [(2, 68)]),            (6, "M"): (16, [(4, 27)]),
    (6, "Q"): (24, [(4, 19)]),            (6, "H"): (28, [(4, 15)]),
}

# version -> centres des motifs d'alignement
ALIGNEMENT = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34]}

# niveau -> les deux bits qui le désignent dans l'information de format
BITS_NIVEAU = {"L": 0b01, "M": 0b00, "Q": 0b11, "H": 0b10}


def capacite(version, niveau):
    """Mots de données disponibles pour cette version et ce niveau."""
    _, groupes = BLOCS[(version, niveau)]
    return sum(n * k for n, k in groupes)


def _plus_petite_version(octets, niveau):
    for v in range(1, 7):
        # 4 bits de mode + 8 bits de longueur + les données
        if 4 + 8 + 8 * octets <= 8 * capacite(v, niveau):
            return v
    raise ValueError("trop long pour les versions 1 à 6 : %d octets" % octets)


# ——— Les données, mises en bits puis en mots de code ——————————————————————

def _flux_de_donnees(texte, version, niveau):
    octets = texte.encode("utf-8")
    if len(octets) > 255:
        raise ValueError("le champ de longueur du mode octet tient sur 8 bits")
    bits = []

    def pousser(valeur, largeur):
        for i in range(largeur - 1, -1, -1):
            bits.append((valeur >> i) & 1)

    pousser(0b0100, 4)            # mode octet
    pousser(len(octets), 8)       # longueur, 8 bits pour les versions 1 à 9
    for o in octets:
        pousser(o, 8)

    maximum = 8 * capacite(version, niveau)
    pousser(0, min(4, maximum - len(bits)))          # terminateur
    while len(bits) % 8:                             # jusqu'au mot entier
        bits.append(0)

    mots = [int("".join(str(b) for b in bits[i:i + 8]), 2)
            for i in range(0, len(bits), 8)]
    remplissage = (0xEC, 0x11)                       # les deux mots de bourrage
    i = 0
    while len(mots) < capacite(version, niveau):
        mots.append(remplissage[i % 2])
        i += 1
    return mots


def _entrelacer(mots, version, niveau):
    """Découpe en blocs, calcule les contrôles, et entrelace comme la norme."""
    n_controle, groupes = BLOCS[(version, niveau)]
    blocs, controles, i = [], [], 0
    for nombre, taille in groupes:
        for _ in range(nombre):
            bloc = mots[i:i + taille]
            i += taille
            blocs.append(bloc)
            controles.append(_mots_de_controle(bloc, n_controle))
    assert i == len(mots), "les blocs ne consomment pas toutes les données"

    sortie = []
    for k in range(max(len(b) for b in blocs)):
        for b in blocs:
            if k < len(b):
                sortie.append(b[k])
    for k in range(n_controle):
        for c in controles:
            sortie.append(c[k])
    assert len(sortie) == TOTAL[version], (
        "mots de code attendus : %d, obtenus : %d" % (TOTAL[version], len(sortie)))
    return sortie


# ——— La matrice ————————————————————————————————————————————————————————————

def _matrice_vide(version):
    n = 17 + 4 * version
    return [[None] * n for _ in range(n)], n


def _poser_motifs(m, n, version):
    def chercheur(haut, gauche):
        for i in range(-1, 8):
            for j in range(-1, 8):
                y, x = haut + i, gauche + j
                if 0 <= y < n and 0 <= x < n:
                    bord = (0 <= i <= 6 and j in (0, 6)) or (0 <= j <= 6 and i in (0, 6))
                    coeur = 2 <= i <= 4 and 2 <= j <= 4
                    m[y][x] = 1 if (bord or coeur) else 0

    chercheur(0, 0); chercheur(0, n - 7); chercheur(n - 7, 0)

    for i in range(8, n - 8):                        # les deux lignes de rythme
        m[6][i] = m[i][6] = 1 - (i % 2)

    centres = ALIGNEMENT[version]
    for cy in centres:
        for cx in centres:
            if m[cy][cx] is not None:                # jamais sur un chercheur
                continue
            for i in range(-2, 3):
                for j in range(-2, 3):
                    m[cy + i][cx + j] = 1 if max(abs(i), abs(j)) != 1 else 0

    m[n - 8][8] = 1                                  # le module toujours sombre

    for i in range(9):                               # réservé au format
        if m[i][8] is None:
            m[i][8] = 0
        if m[8][i] is None:
            m[8][i] = 0
    for i in range(8):
        if m[8][n - 1 - i] is None:
            m[8][n - 1 - i] = 0
        if m[n - 1 - i][8] is None:
            m[n - 1 - i][8] = 0


def _reserve(version):
    """Une copie de la matrice où seules les cases fixes sont occupées."""
    m, n = _matrice_vide(version)
    _poser_motifs(m, n, version)
    return [[c is not None for c in ligne] for ligne in m], n


def _poser_donnees(m, n, occupe, mots):
    bits = [(o >> i) & 1 for o in mots for i in range(7, -1, -1)]
    k, montant, colonne = 0, True, n - 1
    while colonne > 0:
        if colonne == 6:                             # la colonne de rythme
            colonne -= 1
        lignes = range(n - 1, -1, -1) if montant else range(n)
        for ligne in lignes:
            for dx in (0, 1):
                x = colonne - dx
                if not occupe[ligne][x]:
                    m[ligne][x] = bits[k] if k < len(bits) else 0
                    k += 1
        montant = not montant
        colonne -= 2
    assert k >= len(bits), "des bits de données n'ont pas trouvé de place"


MASQUES = (
    lambda i, j: (i + j) % 2 == 0,
    lambda i, j: i % 2 == 0,
    lambda i, j: j % 3 == 0,
    lambda i, j: (i + j) % 3 == 0,
    lambda i, j: (i // 2 + j // 3) % 2 == 0,
    lambda i, j: (i * j) % 2 + (i * j) % 3 == 0,
    lambda i, j: ((i * j) % 2 + (i * j) % 3) % 2 == 0,
    lambda i, j: ((i + j) % 2 + (i * j) % 3) % 2 == 0,
)


MOTIF_CHERCHEUR = [1, 0, 1, 1, 1, 0, 1]


def _occurrences_du_chercheur(bande, n):
    """Règle 3 : le motif 1:1:3:1:1 bordé de quatre modules clairs.

    Ce n'est pas une suite de onze modules à trouver telle quelle : la norme
    compte le motif dès que le blanc de quatre est d'UN SEUL côté, et le bord
    du symbole vaut blanc. Compter la suite de onze, comme on le fait
    naturellement, revient à ne presque rien compter — et le masque choisi
    n'est alors plus le bon.
    """
    total, i = 0, 0
    while True:
        i = _trouver(bande, MOTIF_CHERCHEUR, i)
        if i < 0:
            return total
        avant_clair = not any(bande[max(i - 4, 0):i])
        apres_clair = not any(bande[i + 7:i + 11])
        if avant_clair or apres_clair:
            total += 40
            i += 7
        else:
            # Le motif se chevauche lui-même : on repart au troisième module
            # sombre, seul endroit où un autre motif peut commencer.
            i += 4


def _trouver(bande, motif, depuis):
    for i in range(depuis, len(bande) - len(motif) + 1):
        if bande[i:i + len(motif)] == motif:
            return i
    return -1


def _penalite(m, n):
    """Les quatre règles de pénalité de la norme. Le plus bas l'emporte."""
    bandes = list(m) + [[m[i][j] for i in range(n)] for j in range(n)]
    total = 0

    # Règle 1 : les suites de cinq modules de même teinte, et plus.
    for bande in bandes:
        suite, precedent = 1, bande[0]
        for c in bande[1:]:
            if c == precedent:
                suite += 1
            else:
                if suite >= 5:
                    total += suite - 2
                suite, precedent = 1, c
        if suite >= 5:
            total += suite - 2

    # Règle 2 : les carrés de deux sur deux d'une seule teinte.
    for i in range(n - 1):
        for j in range(n - 1):
            if m[i][j] == m[i][j + 1] == m[i + 1][j] == m[i + 1][j + 1]:
                total += 3

    # Règle 3 : le motif qui imite un chercheur.
    for bande in bandes:
        total += _occurrences_du_chercheur(bande, n)

    # Règle 4 : l'écart à la moitié de modules sombres.
    part = sum(sum(ligne) for ligne in m) / float(n * n)
    total += 10 * int(abs(part * 100 - 50) / 5)
    return total


def _information_de_format(niveau, masque):
    v = (BITS_NIVEAU[niveau] << 3) | masque
    reste = v << 10
    for i in range(4, -1, -1):
        if reste & (1 << (i + 10)):
            reste ^= 0b10100110111 << i
    return ((v << 10) | reste) ^ 0b101010000010010


def _poser_format(m, n, niveau, masque):
    bits = _information_de_format(niveau, masque)

    def b(i):
        return (bits >> i) & 1

    # Première copie, autour du chercheur du haut à gauche : les bits montent
    # la colonne 8, puis repartent vers la gauche sur la ligne 8. La case 6 de
    # chacune est sautée — c'est la ligne de rythme.
    for i in range(6):
        m[i][8] = b(i)
    m[7][8] = b(6); m[8][8] = b(7); m[8][7] = b(8)
    for i in range(9, 15):
        m[8][14 - i] = b(i)
    # Seconde copie, découpée entre les deux autres chercheurs.
    for i in range(8):
        m[8][n - 1 - i] = b(i)
    for i in range(8, 15):
        m[n - 15 + i][8] = b(i)
    m[n - 8][8] = 1


def matrice(texte, niveau="Q", version=None):
    """La matrice du code, en 0 et 1, sans marge."""
    if niveau not in BITS_NIVEAU:
        raise ValueError("niveau inconnu : %s (L, M, Q ou H)" % niveau)
    octets = len(texte.encode("utf-8"))
    version = version or _plus_petite_version(octets, niveau)
    mots = _entrelacer(_flux_de_donnees(texte, version, niveau), version, niveau)

    occupe, n = _reserve(version)
    meilleure, meilleur_score = None, None
    for masque in range(8):
        m, _ = _matrice_vide(version)
        _poser_motifs(m, n, version)
        _poser_donnees(m, n, occupe, mots)
        for i in range(n):
            for j in range(n):
                if not occupe[i][j] and MASQUES[masque](i, j):
                    m[i][j] ^= 1
        _poser_format(m, n, niveau, masque)
        assert all(c is not None for ligne in m for c in ligne), "matrice incomplète"
        score = _penalite(m, n)
        if meilleur_score is None or score < meilleur_score:
            meilleure, meilleur_score = m, score
    return meilleure


def svg(texte, niveau="Q", module=8, marge=4, couleur="#1c1a17", fond="#ffffff"):
    """Le code en SVG. La marge vaut quatre modules : c'est le minimum de la norme."""
    m = matrice(texte, niveau)
    n = len(m)
    cote = (n + 2 * marge) * module
    # Un seul chemin pour tous les modules sombres : le fichier reste petit et
    # l'imprimeur n'a pas des milliers d'objets à traiter.
    d = []
    for i, ligne in enumerate(m):
        j = 0
        while j < n:
            if ligne[j]:
                k = j
                while k < n and ligne[k]:
                    k += 1
                d.append("M%d %dh%dv%dh-%dz" % ((marge + j) * module, (marge + i) * module,
                                                (k - j) * module, module, (k - j) * module))
                j = k
            else:
                j += 1
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" '
            'height="%d" role="img" aria-label="Code QR vers %s" shape-rendering="crispEdges">\n'
            '  <rect width="%d" height="%d" fill="%s"/>\n'
            '  <path fill="%s" d="%s"/>\n</svg>\n'
            % (cote, cote, cote, cote, texte, cote, cote, fond, couleur, "".join(d)))


# ——— Le contrôle du générateur —————————————————————————————————————————————

# Modules libres par version, d'après la norme : c'est le nombre de bits de
# données, reste compris. Si la réservation des motifs fixes se trompe d'une
# seule case, ce compte le dit.
LIBRES = {1: 208, 2: 359, 3: 567, 4: 807, 5: 1079, 6: 1383}

# Quelques informations de format publiées, un niveau après l'autre.
FORMATS = {("L", 0): "111011111000100", ("L", 1): "111001011110011",
           ("M", 0): "101010000010010", ("Q", 0): "011010101011111",
           ("H", 0): "001011010001001"}


def controler():
    """Vérifie le générateur contre la norme. Lève à la première faute."""
    for version, attendu in LIBRES.items():
        occupe, n = _reserve(version)
        libres = sum(1 for i in range(n) for j in range(n) if not occupe[i][j])
        assert libres == attendu, (
            "version %d : %d modules libres, la norme en veut %d"
            % (version, libres, attendu))

    for (niveau, masque), attendu in FORMATS.items():
        obtenu = format(_information_de_format(niveau, masque), "015b")
        assert obtenu == attendu, (
            "format %s masque %d : %s, attendu %s" % (niveau, masque, obtenu, attendu))

    # Aller-retour : on relit la matrice dans l'ordre de pose, on retire le
    # masque, et les mots de code doivent revenir intacts.
    for texte in ("a", "https://sankara.hamedouattara.com",
                  "SANKARA, L'ÉTERNEL VEILLEUR — Parco Thomas Sankara"):
        for niveau in "LMQH":
            version = _plus_petite_version(len(texte.encode("utf-8")), niveau)
            attendus = _entrelacer(_flux_de_donnees(texte, version, niveau), version, niveau)
            m = matrice(texte, niveau)
            nn = len(m)
            masque = _masque_relu(m, nn, niveau)
            occupe, _ = _reserve(version)
            bits, montant, colonne = [], True, nn - 1
            while colonne > 0:
                if colonne == 6:
                    colonne -= 1
                for ligne in (range(nn - 1, -1, -1) if montant else range(nn)):
                    for dx in (0, 1):
                        x = colonne - dx
                        if not occupe[ligne][x]:
                            b = m[ligne][x]
                            if MASQUES[masque](ligne, x):
                                b ^= 1
                            bits.append(b)
                montant = not montant
                colonne -= 2
            relus = [int("".join(str(b) for b in bits[i:i + 8]), 2)
                     for i in range(0, 8 * TOTAL[version], 8)]
            assert relus == attendus, (
                "aller-retour raté : %s, niveau %s" % (texte[:30], niveau))
    return "contrôle du générateur : tout passe"


def _masque_relu(m, n, niveau):
    """Le masque, relu dans l'information de format de la matrice."""
    for masque in range(8):
        if _information_de_format(niveau, masque) == sum(
                m[8][n - 1 - i] << i for i in range(8)) + sum(
                m[n - 15 + i][8] << i for i in range(8, 15)):
            return masque
    raise AssertionError("information de format illisible")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--controle":
        print(controler())
    elif len(sys.argv) < 2:
        raise SystemExit(__doc__.strip())
    else:
        sys.stdout.write(svg(sys.argv[1],
                             sys.argv[2] if len(sys.argv) > 2 else "Q",
                             fond=sys.argv[3] if len(sys.argv) > 3 else "#ffffff"))

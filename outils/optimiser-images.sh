#!/usr/bin/env bash
# Convertit les photographies en WebP aux dimensions servies par le site.
#
# Au Burkina Faso, l'essentiel du trafic est mobile et souvent facturé au
# volume : le poids des images est la première dépense imposée au visiteur.
# Ce script ramène chaque image à ce qui est réellement affiché.
#
# Usage :
#   outils/optimiser-images.sh rotation <dossier-source>
#       36 vues de la rotation, nommées dans l'ordre alphabétique du dossier.
#       Sortie : statique/assets/img/visite/rotation-000.webp … rotation-350.webp
#
#   outils/optimiser-images.sh galerie <dossier-source>
#       Photographies de la galerie, conservant leur nom de fichier.
#       Sortie : statique/assets/img/galerie/<nom>.webp
#
# Outils : cwebp (paquet webp) de préférence, sinon ImageMagick.

set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Largeurs cibles et qualité. La rotation est plus petite et plus compressée :
# elle est vue en séquence, et multipliée par trente-six.
LARGEUR_ROTATION=900
QUALITE_ROTATION=72
LARGEUR_GALERIE=1600
QUALITE_GALERIE=80

if command -v cwebp >/dev/null 2>&1; then
  MOTEUR=cwebp
elif command -v magick >/dev/null 2>&1; then
  MOTEUR=magick
elif command -v convert >/dev/null 2>&1; then
  MOTEUR=convert
else
  echo "Il faut cwebp (paquet webp) ou ImageMagick. Aucun des deux n'est installé." >&2
  exit 1
fi

convertir() {   # convertir <source> <cible> <largeur> <qualité>
  local src="$1" cible="$2" largeur="$3" qualite="$4"
  case "$MOTEUR" in
    cwebp)   cwebp -quiet -resize "$largeur" 0 -q "$qualite" -m 6 "$src" -o "$cible" ;;
    magick)  magick "$src" -resize "${largeur}>" -quality "$qualite" -strip "$cible" ;;
    convert) convert "$src" -resize "${largeur}>" -quality "$qualite" -strip "$cible" ;;
  esac
}

mode="${1:-}"
source_dir="${2:-}"

if [ -z "$mode" ] || [ -z "$source_dir" ] || [ ! -d "$source_dir" ]; then
  sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
  exit 1
fi

case "$mode" in
  rotation)
    cible_dir="$RACINE/statique/assets/img/visite"
    mkdir -p "$cible_dir"
    mapfile -t fichiers < <(find "$source_dir" -maxdepth 1 -type f \
      \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \) | sort)
    if [ "${#fichiers[@]}" -ne 36 ]; then
      echo "Il faut exactement 36 vues, une tous les 10 degrés. Trouvé : ${#fichiers[@]}." >&2
      exit 1
    fi
    angle=0
    for f in "${fichiers[@]}"; do
      cible=$(printf "%s/rotation-%03d.webp" "$cible_dir" "$angle")
      convertir "$f" "$cible" "$LARGEUR_ROTATION" "$QUALITE_ROTATION"
      printf "  %3d°  %s\n" "$angle" "$(basename "$cible")"
      angle=$((angle + 10))
    done
    echo
    echo "36 vues converties. Retirez ensuite les rotation-*.svg de substitution :"
    echo "  rm $cible_dir/rotation-*.svg"
    echo "puis remplacez data-ext=\".svg\" par data-ext=\".webp\" dans contenu/fr/01-visite.html."
    ;;

  galerie)
    cible_dir="$RACINE/statique/assets/img/galerie"
    mkdir -p "$cible_dir"
    n=0
    while IFS= read -r f; do
      nom="$(basename "${f%.*}")"
      convertir "$f" "$cible_dir/$nom.webp" "$LARGEUR_GALERIE" "$QUALITE_GALERIE"
      echo "  $nom.webp"
      n=$((n + 1))
    done < <(find "$source_dir" -maxdepth 1 -type f \
      \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.tif' -o -iname '*.tiff' \) | sort)
    echo
    echo "$n photographies converties. Pour chacune, retirez l'emplacement .svg"
    echo "correspondant et passez l'extension à .webp dans contenu/fr/07-galerie.html."
    ;;

  *)
    echo "Mode inconnu : $mode. Utilisez « rotation » ou « galerie »." >&2
    exit 1
    ;;
esac

echo "Pensez à relancer : python3 outils/build.py && python3 outils/verifier.py"

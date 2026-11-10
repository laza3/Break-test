# The Break Lounge — teaser 15 s (composition HyperFrames)

Composition HyperFrames autonome : HTML + CSS + timeline GSAP **en pause**, pilotée
image par image par le moteur de rendu. Aucun `Math.random()`, `Date.now()`,
`setTimeout` ni `requestAnimationFrame` — le rendu est strictement déterministe.

## Fichiers

| Fichier | Rôle |
| --- | --- |
| `template.html` | Source éditable de la composition (polices et images en placeholders) |
| `build.py` | Injecte polices `.woff2` et images JPEG en base64 → `index.html` |
| `index.html` | **La composition** : un seul fichier auto-suffisant (~1,4 Mo), prêt à importer |
| `render.js` | Rendu déterministe : Playwright seek la timeline → PNG → ffmpeg → MP4 |
| `make_audio.py` | Bande-son 15 s synthétisée avec numpy (aucun échantillon sous licence) |
| `fonts/` | Sous-ensembles latins d'Anton, Barlow Condensed, Space Mono |

## Contrat de composition

- Racine unique `#main` avec `data-composition-id="main"`, `data-width="1920"`,
  `data-height="1080"`, `data-start="0"`, `data-duration="15"`
- 7 scènes tuilées bout à bout, sans trou, chacune avec `data-start` + `data-duration`
- Timeline enregistrée sur `window.__timelines["main"]`
- Coupes franches uniquement (bascule `autoAlpha` par scène), aucune transition shader

## Découpage (15 s, 120 BPM — les coupes tombent sur le temps)

| Scène | Temps | Contenu |
| --- | --- | --- |
| s1 | 0 – 2,0 | « LEAK » — dossier intercepté, glitch RGB, ligne de scan, image floutée |
| s2 | 2,0 – 4,5 | Carte isométrique plein cadre : « QUELQUE / CHOSE / ARRIVE » |
| s3 | 4,5 – 6,0 | « À ANDRANOMENA » — stagger par lettre, traînées néon |
| s4 | 6,0 – 9,5 | Triptyque isométrique distribué : BILLARD · BAR · LOUNGE |
| s5 | 9,5 – 12,0 | Révélation du logo mural réel + verrou typographique |
| s6 | 12,0 – 13,5 | « COMING SOON » — impact, flash, screen shake |
| s7 | 13,5 – 15,0 | Carte finale : lieu + « OUVERTURE TRÈS BIENTÔT » |

## Reproduire le rendu

```bash
# 1. composer le fichier unique
python3 build.py

# 2. récupérer GSAP 3.14.2 (servi localement au moteur de rendu)
curl -sL https://registry.npmjs.org/gsap/-/gsap-3.14.2.tgz | tar -xz -C /tmp package/dist/gsap.min.js

# 3. rendre la vidéo (1920×1080, 60 fps)
node render.js --gsap /tmp/package/dist/gsap.min.js --fps 60 --out video_silent.mp4

# 4. bande-son + mixage
python3 make_audio.py audio.wav
ffmpeg -i video_silent.mp4 -i audio.wav -c:v copy -c:a aac -b:a 192k -shortest teaser.mp4
```

`render.js --snaps 2.4,7.4,10.6` exporte des images fixes pour contrôler une scène
sans relancer tout le rendu.

## Voix off

La vidéo est livrée avec musique et effets uniquement. Texte prévu pour une voix off
française grave (environ 7 s, à poser sur 1,2 s → 4,4 s, 6 s → 9 s et 13,6 s) :

> « Un nouveau spot arrive à Andranomena. Billard. Bar. Lounge. The Break Lounge. Très bientôt. »

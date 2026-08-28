# Digital Showroom — case study page

Source for the case study page of **Digital Showroom**, an interactive
real-time sales system for residential developments built in Unreal Engine 5.7.

**Live page → https://danis812.github.io/digital-showroom/**
English: [`?lang=en`](https://danis812.github.io/digital-showroom/?lang=en) ·
Russian: [`?lang=ru`](https://danis812.github.io/digital-showroom/?lang=ru)

The application itself is not in this repository. This is the page that
documents it: how it is put together, what the five sections do, and what the
optimisation pass actually moved.

## What's here

```
index.html          built page — do not edit, it is regenerated
media/              video loops, the walkthrough, poster frames
src/
  build.py          the build
  page.tpl.html     the source template
  img/              interface screenshots, 1400 px
  sounds/           the nine UI sounds, 48 kHz stereo PCM16
```

## Build

```bash
python src/build.py
```

No dependencies beyond the standard library. Edit `src/page.tpl.html`, never
`index.html` — the latter is overwritten on every run.

The FPS figures live in `src/build.py` as the `FPS` list, and the sound board's
order and tail markers in `SOUNDS`. Waveforms and durations are measured from
the WAV files at build time, so changing the pack needs no hand-editing.

## Two languages, one page

Russian and English both ship inside `index.html`; one is hidden by CSS. A
`?lang=` parameter forces a language, the choice is remembered, and with no
parameter the page follows the browser. The language lives in a query
parameter rather than the hash because the section nav already uses `#task`,
`#parts` and friends — a hash would be wiped by the first anchor click.

The CSS only ever *hides*: the visible language keeps whatever `display` its
own component rule gives it. Toggling display in both directions loses to the
flex containers on specificity and prints both languages at once.

Every translatable element is marked `lang="ru"` / `lang="en"`, and the build
counts them. A block written in one language and forgotten in the other fails
the build instead of reaching the page.

## Why some assets are inlined and some are not

Screenshots, poster frames and the sound pack are embedded as data URIs.
Videos are referenced from `media/`.

The split follows one rule: **the page has to survive being sent as a single
file.** Detached from `media/`, it still reads end to end — every section shows
its poster frame, every sound still plays. What's lost is motion, not content.
Videos are the one thing too large for that, so they stay external and each
`<video>` falls back to its inlined poster.

The sounds are inlined as WAV rather than transcoded on purpose. A lossy
encoder's priming delay eats the attack transient, and for a 46 ms hover blip
the attack is the entire sound. Nine files cost about 560 KB.

## Rights

Code, interface, design system, page and sound design: Danis Ziakaev.

The architectural model of the MOD Fusion quarter and part of the static
visualisations were provided by Whila. Architectural modelling and the
authorship of those images are not mine, and neither the model nor the
renderings derived from it are offered for reuse here.

## Contact

Danis Ziakaev — Unreal Engine developer
[ziakaev.danis@gmail.com](mailto:ziakaev.danis@gmail.com)

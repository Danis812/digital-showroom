# -*- coding: utf-8 -*-
"""Builds ../index.html from page.tpl.html.

Screenshots, video poster frames and the UI sound pack are inlined as data
URIs; the video files themselves stay in ../media/ and are referenced by path.
That split is deliberate — see README.md.

    python src/build.py
"""
import array
import base64
import io
import os
import re
import wave

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)

TPL = os.path.join(SRC, "page.tpl.html")
IMGDIR = os.path.join(SRC, "img")
SNDDIR = os.path.join(SRC, "sounds")
MEDIADIR = os.path.join(ROOT, "media")
OUT = os.path.join(ROOT, "index.html")


def data_uri(path, mime):
    b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
    return "data:%s;base64,%s" % (mime, b64)


# --- Screenshots ------------------------------------------------------------

SHOTS = ["menu", "walk", "film", "map", "zones", "units", "compare"]

# Poster frames are inlined too, so the page still shows every section when it
# travels as a single file without media/. You lose the motion, not the
# picture — the <video> elements fall back to these same frames.
POSTERS = ["walk", "film", "map", "zones", "units", "full", "intro", "danis"]


# --- UI sound board ---------------------------------------------------------

# The nine pack sounds are inlined as WAV rather than transcoded. They total
# under half a megabyte, and a lossy encoder's priming delay eats the attack
# transient — which, for a 46 ms hover blip, is the entire sound.
#
# Third field marks the sounds carrying the freeze-decay tail from the logo
# intro. The signature sits in confirm, toggle on, panel open and the logo
# lock; hover and press stay deliberately bare, because they fire constantly
# and character in them gets tiring fast.
SOUNDS = [
    ("ui_hover_01.wav",       "Наведение",             False),
    ("ui_press_03.wav",       "Нажатие",               False),
    ("ui_confirm_02.wav",     "Подтверждение",         True),
    ("ui_back_01.wav",        "Назад",                 False),
    ("ui_toggle_on_03.wav",   "Переключатель · вкл",   True),
    ("ui_toggle_off_02.wav",  "Переключатель · выкл",  False),
    ("ui_panel_open_02.wav",  "Панель · открыть",      True),
    ("ui_panel_close_01.wav", "Панель · закрыть",      False),
    ("ui_logo_lock_01.wav",   "Фиксация знака",        True),
]

BUCKETS = 96   # envelope resolution across a card's width


def envelope(path):
    """Peak envelope (0..1) and duration in seconds, from the raw PCM frames.

    Deliberately array-based rather than audioop: that module was removed in
    Python 3.13, and this file should still build years from now.
    """
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        width, rate, ch = w.getsampwidth(), w.getframerate(), w.getnchannels()
        raw = w.readframes(n)
    if width != 2:
        raise SystemExit("%s: expected 16-bit PCM, got %d-bit" % (path, width * 8))

    samples = array.array("h")
    samples.frombytes(raw)
    if ch > 1:                                  # collapse to frame-wise peak
        samples = array.array("h", [max(samples[i:i + ch], key=abs)
                                    for i in range(0, len(samples), ch)])

    step = max(1, n // BUCKETS)
    full = float(max((abs(s) for s in samples), default=0)) or 1.0
    peaks = [max((abs(s) for s in samples[i:i + step]), default=0) / full
             for i in range(0, len(samples), step)]
    return peaks[:BUCKETS], n / float(rate)


SOUND_CARD = (
    '<button class="snd{tail_class}" type="button" data-src="{src}">'
    '<span class="snd-head"><span class="micro">{mark}</span>'
    '<span class="snd-ms">{ms:d} ms</span></span>'   # thin space before the unit
    '<svg class="snd-wave" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
    '<polygon points="{top} {bottom}"></polygon></svg>'
    '<span class="snd-name">{label}</span>'
    '</button>'
)


def sound_cards():
    cards = []
    for fname, label, tail in SOUNDS:
        path = os.path.join(SNDDIR, fname)
        peaks, dur = envelope(path)
        last = len(peaks) - 1
        # Mirrored envelope, drawn as one filled polygon around the centre line.
        top = " ".join("%.2f,%.3f" % (i * 100.0 / last, 50 - p * 46)
                       for i, p in enumerate(peaks))
        bottom = " ".join("%.2f,%.3f" % (i * 100.0 / last, 50 + p * 46)
                          for i, p in reversed(list(enumerate(peaks))))
        cards.append(SOUND_CARD.format(
            tail_class=" has-tail" if tail else "",
            src=data_uri(path, "audio/wav"),
            mark="Хвост" if tail else "",
            ms=round(dur * 1000),
            top=top, bottom=bottom, label=label,
        ))
    return "\n          ".join(cards)


# --- Performance chart ------------------------------------------------------

MAX = 70.0                      # shared scale for both panels
REF = 60.0 / MAX * 100.0        # the 60 fps reference line

# section, avg before, avg after, 1% low before, 1% low after
# Measured over 12-second windows, same machine, same scenario.
# name RU, name EN, avg before, avg after, 1% low before, 1% low after
FPS = [
    ("Зоны",          "Amenities",   12.0, 65.6,  5.9, 50.9),
    ("Поиск квартир", "Apartments",  12.4, 65.4,  8.0, 50.3),
    ("Фильм",         "Film",        20.3, 65.4, 16.1, 45.3),
    ("Меню",          "Main menu",   20.4, 64.5, 14.6, 41.7),
    ("Прогулка",      "Walkthrough", 49.4, 65.6, 31.6, 47.8),
    ("Карта",         "Map",         49.5, 57.0, 32.7, 41.8),
]

CHART_ROW = (
    '<div class="db-row" tabindex="0" style="--a:{a:.2f}%;--b:{b:.2f}%;--w:{w:.2f}%">'
    '<span class="db-name"><span lang="ru">{ru}</span><span lang="en">{en}</span></span>'
    '<span class="db-num">{before:.1f}</span>'
    '<span class="db-track">'
    '<i class="db-ref" style="--ref:{ref:.2f}%"></i>'
    '<i class="db-line"></i>'
    '<i class="db-dot is-before"></i>'
    '<i class="db-dot is-after"></i>'
    '</span>'
    '<span class="db-num is-after">{after:.1f}</span>'
    '<span class="db-tip"><span>{before:.1f} &rarr; {after:.1f} &middot; '
    '<b>+{delta:d}%</b></span></span>'
    '</div>'
)


def chart_rows(i_before, i_after):
    rows = []
    for row in FPS:
        before, after = row[i_before], row[i_after]
        a, b = before / MAX * 100.0, after / MAX * 100.0
        rows.append(CHART_ROW.format(
            a=a, b=b, w=b - a, ru=row[0], en=row[1], ref=REF,
            before=before, after=after,
            delta=round((after - before) / before * 100.0),
        ))
    return "\n          ".join(rows)


# --- Build ------------------------------------------------------------------

def main():
    html = io.open(TPL, encoding="utf-8", newline="").read()

    for key in SHOTS:
        html = html.replace("__IMG_%s__" % key,
                            data_uri(os.path.join(IMGDIR, key + ".jpg"), "image/jpeg"))
    for key in POSTERS:
        html = html.replace("__POSTER_%s__" % key,
                            data_uri(os.path.join(MEDIADIR, "poster-%s.jpg" % key), "image/jpeg"))

    html = html.replace("__ROWS_AVG__", chart_rows(2, 3))
    html = html.replace("__ROWS_LOW__", chart_rows(4, 5))
    html = html.replace("__SOUNDS__", sound_cards())

    # Case-sensitive on purpose: the image keys are lowercase, and a stricter
    # pattern here is what catches a renamed placeholder before it ships.
    leftover = sorted(set(re.findall(r"__[A-Za-z_]+__", html)))
    if leftover:
        raise SystemExit("unfilled placeholders: %s" % ", ".join(leftover))


    # Both languages ship in the page, so a block written in one and forgotten
    # in the other is the failure mode worth guarding against. Style and script
    # are cut out first: the CSS carries [lang="en"] selectors and
    # data-lang="en", and counting those would drown the signal.
    markup = re.sub(r"<(style|script)\b.*?</\1>", "", html, flags=re.S)
    ru = len(re.findall(r'\slang="ru"', markup))
    en = len(re.findall(r'\slang="en"', markup))
    if ru != en:
        raise SystemExit("language blocks unbalanced: %d ru vs %d en" % (ru, en))

    io.open(OUT, "w", encoding="utf-8", newline="").write(html)
    print("wrote %s  %d KB" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    main()

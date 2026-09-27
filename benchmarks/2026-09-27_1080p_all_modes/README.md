# Digital Showroom — expanded 1080p benchmark

27 September 2026 · RTX 4070 Laptop · Ryzen 9 7940HS · 1920×1080

**Up to 5.60× higher average FPS after optimisation.** The dataset covers one loaded state in each of the five sections plus the main menu: 36 runs in total. The maximum is Apartment Search, 10.04 → 56.19 FPS. Gains across the measured states range from 1.12× to 5.60×; no application-wide average is claimed.

## Results

Each value is the median of three 30-second runs after warm-up. Gain is the ratio of the two median average-FPS values.

| Mode | Before avg | After avg | Gain | Before 1% low | After 1% low |
|---|---:|---:|---:|---:|---:|
| Main menu | 17.89 | 46.73 | 2.61× | 14.58 | 38.71 |
| Walkthrough: courtyard | 11.36 | 50.09 | 4.41× | 7.52 | 41.97 |
| Amenities | 10.96 | 48.65 | 4.44× | 6.46 | 42.67 |
| Apartment Search | 10.04 | 56.19 | 5.60× | 6.34 | 49.11 |
| Map | 42.09 | 47.05 | 1.12× | 33.14 | 40.65 |
| Film / Gallery* | 27.82 | 77.02 | 2.77× | 22.78 | 58.73 |

### What was measured

- **Main menu:** the default menu after loading, without input.
- **Walkthrough:** entered the first courtyard entry point in both builds, then remained at the spawn location. This measures the actual 3D courtyard, not the entry-selection screen. No walking route was replayed; framing differs between versions.
- **Amenities and Apartment Search:** retained from the earlier [1080p session](../2026-09-27_1080p/README.md), without changing its intervals or results. These are loaded views without input.
- **Map:** default loaded view without input. The current build starts an automatic category tour; the original remained static.
- **Film / Gallery\*:** the original build remained on its static “02 ГАЛЕРЕЯ” landing screen; the current Film automatically advanced through chapters. These are different section states, not a matched video-playback test. The row records their runtime performance and should not be presented as an isolated video-decoding speedup.

## Method

- Same laptop, NVIDIA driver 610.62, AC power, Performance power plan. Unreal Editor closed. Browser and other work applications remained open during the earlier Amenities/Apartment Search session; the browser was closed for the four additional states. Each before/after pair belongs to the same session group.
- Three consecutive 30-second intervals per build and state after warm-up, with no user input during capture. Screenshots were taken before and after the intervals. Initial loading, user navigation and transitions between sections are excluded; built-in animations and automatic changes within the active section remain included.
- DXGI instrumentation records QPC timestamps before Present, frame intervals, swapchain identity and output dimensions. Every selected frame has a 1920×1080 output buffer, one swapchain per interval and Present SyncInterval=0.
- The current build's Unreal log confirms DLAA with 1920×1080 input and output, 100% render scale, VSync off and t.MaxFPS=0. The original build's internal render resolution was not independently confirmed.
- Average FPS = 1000 / mean frame time in milliseconds. 1% low = 1000 / mean duration of the slowest ceil(N×0.01) frames. Only frame intervals wholly within the recorded QPC boundaries are included. Long frames are retained; none reached 1000 ms in the 36 runs.
- This measures application Present calls, not GPU execution time or every monitor-displayed frame. Frame Generation and instrumentation overhead were not independently measured.

## Interpretation

The original and optimised builds are versions of the same architectural project. The author reports limited scene changes, primarily arising from optimisation. Asset, geometry, texture, rendering and scene-setting changes are part of the work being compared. Cameras and interfaces also differ. This comparison measures the combined outcome; it does not isolate any one technique or establish identical visual quality.

The original build is Shipping; the current build is Development. The original was tested first in each session group. GPU temperature samples ranged from 80–89 °C in the original across both groups and 86–87 °C in the current build. Thermal throttling was not independently ruled out. These results describe the tested laptop and states, not a guaranteed minimum FPS throughout the application.

## Run ranges

| Mode | Build | Average FPS | Run range | 1% low |
|---|---|---:|---:|---:|
| Main menu | Before | 17.89 | 17.85–17.93 | 14.58 |
| Main menu | After | 46.73 | 46.59–46.76 | 38.71 |
| Walkthrough: courtyard | Before | 11.36 | 11.36–11.42 | 7.52 |
| Walkthrough: courtyard | After | 50.09 | 50.09–50.24 | 41.97 |
| Amenities | Before | 10.96 | 8.75–10.98 | 6.46 |
| Amenities | After | 48.65 | 48.54–48.68 | 42.67 |
| Apartment Search | Before | 10.04 | 10.01–10.12 | 6.34 |
| Apartment Search | After | 56.19 | 56.10–56.19 | 49.11 |
| Map | Before | 42.09 | 41.96–42.27 | 33.14 |
| Map | After | 47.05 | 47.03–47.08 | 40.65 |
| Film / Gallery* | Before | 27.82 | 27.79–27.83 | 22.78 |
| Film / Gallery* | After | 77.02 | 76.85–77.20 | 58.73 |

## Recalculate

Run `python analyze.py` in this folder. It uses only the Python standard library and does not launch or modify the application.

- [results.csv](results.csv): all 36 runs, frame counts, average FPS, 1% low, p99 and maximum frame time.
- [summary.json](summary.json): medians and run ranges.
- [intervals.csv](intervals.csv): explicit QPC boundaries and source filename for each interval.
- [baseline-old-present.csv](baseline-old-present.csv): original Amenities capture.
- [baseline-old-unit-present.csv](baseline-old-unit-present.csv): original Apartment Search capture.
- [baseline-current-present.csv](baseline-current-present.csv): current Amenities and Apartment Search capture.
- [old-present.csv](old-present.csv): additional original Menu, Map, Walkthrough and Gallery captures.
- [current-present.csv](current-present.csv): additional current Menu, Map, Walkthrough and Film captures.
- [analyze.py](analyze.py): calculation and output-resolution validation.

Raw captures include warm-up and navigation outside the selected intervals. Only the boundaries in `intervals.csv` contribute to the reported numbers. The three `baseline-` logs are unchanged copies of the earlier session's source data.

## Кратко по-русски

В CV: **«Оптимизировал Digital Showroom: ускорение до 5,6 раза по среднему FPS (1920×1080, RTX 4070 Laptop)».**

Проверены пять разделов и главное меню: 36 прогонов по 30 секунд, по три для каждого состояния и билда. Максимальный прирост — 5,60×; весь диапазон — 1,12–5,60×. В таблице медианы, а не среднее ускорение приложения.

Прогулка измерена в 3D-дворе без движения. В новой карте работает автоматический обзор. Film / Галерея сравнивает статичный экран старой галереи с автоматической сменой глав в новом разделе: одинаковое видео в обеих версиях не тестировалось. Благоустройство и квартиры перенесены из предыдущего замера того же дня; остальные четыре состояния измерены дополнительно. Подробные условия и ограничения приведены выше.

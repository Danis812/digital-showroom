# Digital Showroom — optimisation benchmark

27 September 2026 · RTX 4070 Laptop · Ryzen 9 7940HS · 1920×1080

The optimisation increased average FPS by **4.44× in Amenities** and **5.60× in Apartment Search**. “Roughly 5× faster” refers to these two measured modes, not an average across the whole application. Asset, rendering and scene-setting changes are part of the optimisation work on the same architectural project.

## Results

Each row summarises three 30-second runs after warm-up. Average FPS and 1% low are medians of the three run results. The range is the minimum and maximum average FPS across those runs.

| Mode | Build | Average FPS | Range | 1% low |
|---|---|---:|---:|---:|
| Amenities | Before | 10.96 | 8.75–10.98 | 6.46 |
| Amenities | After | 48.65 | 48.54–48.68 | 42.67 |
| Apartment Search | Before | 10.04 | 10.01–10.12 | 6.34 |
| Apartment Search | After | 56.19 | 56.10–56.19 | 49.11 |

## Method

- Same laptop, NVIDIA driver 610.62, AC power and Performance power plan. Unreal Editor closed; browser and other working applications remained open.
- DXGI instrumentation records QPC timestamps before Present, frame intervals and swapchain dimensions. Every included frame has a 1920×1080 output buffer, a single swapchain and Present SyncInterval=0.
- The current build's Unreal log confirms DLAA at 1920×1080 input and output, render scale 100%, VSync off and t.MaxFPS=0. The old build's internal render scale was not independently confirmed.
- Each section was opened and allowed to settle before three consecutive 30-second intervals with no user input. Mode state was checked with screenshots before and after. Loading, mode transitions and navigation routes are outside these intervals.
- Average FPS = 1000 / mean frame time in milliseconds. 1% low = 1000 / mean frame time of the slowest ceil(N×0.01) frames. Each frame interval must lie wholly within its recorded QPC boundaries. Long frames are retained; none exceeded 1000 ms in these 12 runs.
- The instrument measures application Present calls, not GPU execution time or all frames displayed by the monitor. Frame Generation was not independently checked. Instrumentation overhead was not separately measured.

## Scope

This is a before/after comparison of the original and optimised application builds. The author confirms that changes to the architectural scene are limited and primarily arise from optimisation. UI, camera framing, assets and settings are not pixel-identical; the original executable is Shipping and the current one is Development. The test measures the combined result of the work, not the isolated contribution of any one setting or technique, and does not establish identical visual quality.

The original build was tested first. GPU temperature readings were 84–89 °C before and 86–87 °C after. Thermal throttling was not independently ruled out. The measured current build remains below 60 FPS in these states.

This dataset replaces the earlier 1280×720, 12-second figures on the case-study page. Menu, Film, Map and Walkthrough were not remeasured under this protocol and are not mixed into the new charts.

## Source data

- [results.csv](results.csv): all 12 runs, including frame counts, 1% low, p99 and maximum frame time.
- [summary.json](summary.json): medians and ranges used on the page.
- [intervals.csv](intervals.csv): explicit QPC boundaries for each run.
- [old-present.csv](old-present.csv): original build, Amenities.
- [old-unit-present.csv](old-unit-present.csv): original build, Apartment Search, captured after a separate launch.
- [current-present.csv](current-present.csv): current build, both modes.
- [analyze.py](analyze.py): recalculates the results from these files using the Python standard library. Run `python analyze.py`.

The capture CSVs include warm-up and navigation outside the selected intervals; only the intervals listed above enter the reported results. Recalculating the dataset does not launch or modify the application.

## Кратко по-русски

Оптимизация увеличила средний FPS в **4,44 раза в благоустройстве** и **5,60 раза в поиске квартир**. Формулировка «примерно в 5 раз» относится к этим двум режимам. Изменения ассетов, рендеринга и настроек сцены входят в выполненную работу по оптимизации.

Замер: один ноутбук, 1920×1080, по три 30-секундных прогона после прогрева. В таблице — медианы среднего FPS и 1% low. Текущий билд использует DLAA при рендере 100%. Это результат двух разделов после загрузки, а не средний FPS всего приложения или тест переходов и подгрузок. Полные условия, границы метода и исходные данные приведены выше.

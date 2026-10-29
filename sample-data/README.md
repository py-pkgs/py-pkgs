# Gartersnake growth data (data source for `pysnakes`)

**`gartersnake_growth.csv` is the dataset that `pysnakes` and the book use from here on.** It has one row per snake: the snake's body length at two captures, and the number of days between them. It is a reshaped copy of US Geological Survey (USGS) data, not the original product; the source and the changes are described below.

Data is sourced from:

> Rose, J.P., Kim, R., Schoenig, E.J., Lien, P.C., and Halstead, B.J., 2022, Growth and capture-mark-recapture data for San Francisco gartersnakes, *Thamnophis sirtalis tetrataenia*, in San Mateo County, California from 2007 to 2020: U.S. Geological Survey data release, <https://doi.org/10.5066/P9SC36I8>.

## Columns

| Column | Meaning |
|---|---|
| `snake_id` | Number identifying one individual snake (the original USGS ID; ID 113 does not exist in the source) |
| `sex` | `female`, `male` or `unknown` (2 snakes are `unknown`) |
| `site` | Letter code for the study site: C, I, N, P or S. The USGS data gives no site names. |
| `study_year_start` | Year of the study (1 = first year) in which the snake was first captured and measured |
| `study_year_end` | Year of the study in which the snake was captured and measured a second time |
| `days_between_captures` | Days between the two captures |
| `body_length_start_mm` | Body length in millimetres at the first capture |
| `body_length_end_mm` | Body length in millimetres at the second capture |

Body length here is the original "snout-vent length": measured from the snout to the vent (the opening at the base of the tail), so the tail is excluded. Study years run from 1 to 14 and the study covers 2007 to 2020, but we have not confirmed that study year 1 is 2007.

## Where the data comes from

- **Data release:** Rose, J.P., Kim, R., Schoenig, E.J., Lien, P.C., and Halstead, B.J. Published 9 May 2022 by the USGS Western Ecological Research Center. DOI: <https://doi.org/10.5066/P9SC36I8>. Landing page: <https://www.usgs.gov/data/growth-and-capture-mark-recapture-data-san-francisco-gartersnakes-thamnophis-sirtalis>.
- **What it is:** captures of San Francisco gartersnakes (*Thamnophis sirtalis tetrataenia*), an endangered subspecies, at five sites in San Mateo County, California, from 2007 to 2020. The data were collected to study the snake's demography and estimate vital rates for conservation planning.
- **File used:** `SFGS_growth_data.R`, an R data frame of 163 snakes that were captured and measured at least twice (accessed October 2026). The same release's `SFGS_CMR_data.R` (capture histories for survival modelling) is not used.
- **Paper that uses the data:** Rose, J.P., Kim, R., Schoenig, E.J., Lien, P.C., and Halstead, B.J. (2022). Integrating growth and survival models for flexible estimation of size-dependent survival in a cryptic, endangered snake. *Ecology and Evolution*, 12(4). <https://doi.org/10.1002/ece3.8799>

## What we changed

1. Converted the R data frame to CSV.
2. Renamed the columns and recoded sex (1 = `male`, 0 = `female`, blank = `unknown`).
3. Dropped `t0` (always 0) and `ncaps` (the number of captures, which can be counted).
4. Kept only the first growth interval for each snake (first capture to second capture). Fifteen snakes were measured a third time; their second interval (`t2`, `SVL2`, `year2` in the source) was dropped so that there is one row per snake.
5. Corrected nothing. The file includes 4 snakes whose measured length decreased between captures and 1 that did not change, which are presumably measurement error in the field data.

## Licence

The USGS data release is marked CC0 1.0 Universal (public domain), so the data may be used, copied and redistributed without permission. The metadata XML supplied with the release states no licence of its own, only the standard USGS disclaimer: no warranty is made about the data, and the USGS and the US Government are not liable for incorrect use. We treat the data as CC0 and still credit the authors as described above.

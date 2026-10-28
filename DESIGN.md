# 🔦 SF AI Event Search — Design Spec (as built)

Updated Oct 26, 2026 · @Aaron

The visual design of `index.html`. The product behaviour lives in `SPEC.md`; this file covers
look and feel: typography, themes, colour rules, header layout and the per-view details.
It all lives in the skin `<style>` block and the theme script in `<head>` of `index.html`.

## Principles

- **Cave Day look.** Pastel panels, white cards, rounded corners (12–16px, 22px on the
  Halloween and black & gold themes), soft shadows, no hard outlines.
- **One typeface.** Poppins everywhere, including form controls. Only size, weight, italics
  and caps vary. Emoji fall through to the system emoji font.
- **Nothing moves between views.** Header controls stay in the same place when switching
  Calendar ⇄ List; only the range menu and Today (both calendar only) appear or disappear on the left.
- **Adapts to aspect ratio.** Landscape fills one month; portrait (Aaron uses a vertical
  monitor) stacks months. Everything is checked in both, plus phone width.

## Themes

Six colours, each with a light and a dark version. Light blue is the default.

| Colour | Light (`data-skin`) | Dark (`data-skin`) | Sun / moon icon |
| --- | --- | --- | --- |
| Blue | `blue` | `night-blue` | ☀️ / 🌙 |
| Pink | `pink` | `night-pink` | ☀️ / 🌙 |
| Purple | `purple` | `night-purple` | ☀️ / 🌙 |
| Green | `green` | `night-green` | ☀️ / 🌙 |
| Orange (Halloween) | `pumpkin` | `night-orange` | 🎃 / 🦇 |
| Gold | `gold` | `bat` (black & gold) | ☀️ / 🌙 |

- The header has a sun / moon segmented toggle.
  - **Sun:** in light mode, it steps to the next light colour (blue → pink → purple → green → 🎃 → gold → blue). In dark mode, it switches to the same colour's light version.
  - **Moon:** in light mode, it switches to the same colour's dark version. In dark mode, it steps to the next dark colour in the same order.
- `<html>` carries `data-skin` (the theme) and `data-mode="light|dark"`. Dark-generic rules key off `data-mode`; light-only rules use `:root:not([data-mode="dark"])`.
- The choice is saved in `localStorage` under `radar-skin`. It's a per-viewer convenience only.
- Halloween garnish: 🎃 legend line on light orange, 🦇 legend line on black & gold.

### Theme tokens

Each theme sets these CSS custom properties. Every rule reads them, so a new theme is just a new token block.

- **Panels:** `--panel` (pastel panel fill), `--panel-line` (its edge) and `--panel-title` (deep heading colour: month name, "This week", mm/dd dates).
- **Surfaces:** `--card` and `--surface…` (white/near-white cards).
- **Chips:** `--chip` and `--chip-line` (event fill and edge).
- **Accent family:** `--accent`, `--accent-ink`, `--accent-weak`, `--accent-strong-weak`, `--accent-line` and `--accent-fg`.
- **Light-only:** `--hot`, the bright hue.

## Colour rules

**Light themes: the bright hue is for extreme emphasis only.**
- `--hot` (blue `#2563EB`, rose `#E11D48`, purple `#9333EA`, green `#16A34A`, orange `#EE7A12`, gold `#CA8A04`) is used only for:
  - region warning tags (South Bay / East Bay / Online): `--hot` fill, white text, in list rows and the calendar day popover
  - the score dots of 5/5 events
- Everything else that used to be the accent takes `--panel-title`, the deep heading colour:
  - the Today button, Open event and the "new" tag
  - the today day-number badge and strong-fit chip edges
  - the Add to calendar outline and menu border, "Why it fits you" and the detail labels (WHEN … SOURCE)

**Dark themes:** near-black surfaces tinted with the theme hue. The hue's 400 shade is the accent (buttons, chips, dots, today badge). Region tags use the hue's soft fill and light text. Black & gold keeps its own gold/salmon palette.

**Calendar day popover text:**
- Time, location, setting, detail values and description bullets are pure black (`#000`) in light themes and pure white (`#FFF`) in dark themes, with no greys.
- In dark themes, the detail labels match the date / title colour.

**Event chips:**
- fits (1–3): hue-100 fill and hue-300 edge
- strong fit (4–5): hue-200 fill, a deeper edge and semi-bold text
- unconfirmed: dashed edge
- past: dimmed but never hidden

## Header

Left to right:

- **Title:** "🔦 SF AI Event Search". It's the same size as the month heading.
- **Range menu:** calendar view only.
- **Today:** calendar view only. It returns to the current month or week; List has no use for it.
- **Sun / moon toggle**
- **Calendar / List toggle:** icon-only, calendar and notepad icons.
- **🔍:** toggles Filter & search, and shows a dot when filters are on.

Layout details:

- **Sizes:**
  - Range menu, Today, sun / moon and Calendar / List: identical 88×38 boxes.
  - 🔍: a 38×38 square.
- **Alignment:** the header is full-bleed. The flashlight's left edge lines up with the Sunday column and the 🔍's right edge with the Saturday column. List and day views use the page column inset plus 15px.
- **Scaling:**
  - A scale unit `--u: clamp(0.72px, 0.105vw, 1px)` shrinks the title and all controls together on narrow screens.
  - Under about 560px the controls wrap to a second row, filling from the right.

## Calendar view

- **Month rows** are sized by content:
  - empty week: `minmax(34px, .35fr)`
  - past week with events: `minmax(52px, (0.6 + 0.3n)fr)`
  - current or future week: `minmax(72px, (1 + 0.6n)fr)`
  - n is the max chips per day, capped at 4. This only applies to grids with 4 or more rows.
- **Chips** are not links. Clicking one opens the day popover. Only **Open event** leaves the page.
- **Day popover:** white sheet with a pastel header, radius 16. Rows expand to the full detail.
  - **Draggable:** the header is the handle (6-dot grip on the left, grab cursor). Drag it with mouse, finger or pen.
    It can slide partly off the bottom or sides to uncover the grid, but the header always stays on-screen.
    It keeps the dragged spot while you click other days; closing it (×, Esc, click outside, scroll, resize)
    resets it, so the next one opens beside its day. Double-click the header to snap it back.

## List view

- **Panel:** in light themes, the list sits on the theme's pastel panel, like the calendar. Rows are white cards with a hue left edge.
- **Date column:** each row shows the day abbreviation (WED) centred above mm/dd, in the deep heading colour. Day popover rows share it.
- **Text sizes:** the meta line under each title (time · place · setting) matches the detail text size, 0.86rem, in every theme.
- **Detail actions:** only **Open event** and **Add to calendar**. Add to calendar opens a themed menu with a 2px border in the Open event colour, offering Google Calendar and Apple / iOS (.ics).

## Default view

Phones (600px wide or less at load) always open in **List**. Calendar is still there, one
deliberate tap on the Calendar / List toggle away. Everything wider, including phone landscape
and the vertical monitor, opens in **Calendar**, or in the last view tapped on the toggle
(remembered per viewer as `radar-view-pick`). A `?v=` deep link wins over both.

On phones (560px or less), calendar chips show **tiny names**: 7.5px text, up to 3 lines,
no emojis. Names often break mid-word; it's a glanceable overview, and tapping a day opens
the readable popover.

## Filter & search

Hidden by default, opened and closed with 🔍. It auto-opens when a deep link carries filters. Its border takes the page background colour, so there's no coloured outline.

## Known issues

- TBC shelf chips still link straight to the event site, unlike calendar chips.

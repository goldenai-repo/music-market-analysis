#!/usr/bin/env python3
"""
Generate chart images from Five_Country_AI_Music_Investment_Matrix.md.

Outputs:
  Charts/comprehensive_score_bar.png
  Charts/ai_interest_market_value_bubble.png

The script intentionally uses only Pillow plus Python standard-library modules,
so it can run in this workspace without installing matplotlib/seaborn/plotly.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
MATRIX_FILE = ROOT / "Five_Country_AI_Music_Investment_Matrix.md"
OUTPUT_DIR = ROOT / "Charts"


@dataclass
class CountryData:
    country: str
    population_m: float
    market_value_usd_m: float
    ai_interest_index: float
    comprehensive_score: float


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


FONT_TITLE = load_font(32, bold=True)
FONT_SUBTITLE = load_font(18)
FONT_AXIS = load_font(17)
FONT_LABEL = load_font(16)
FONT_SMALL = load_font(14)
FONT_BOLD = load_font(16, bold=True)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def parse_markdown_tables(markdown: str) -> list[list[dict[str, str]]]:
    lines = markdown.splitlines()
    tables: list[list[dict[str, str]]] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            i += 1
            continue
        if i + 1 >= len(lines) or "---" not in lines[i + 1]:
            i += 1
            continue

        headers = [cell.strip() for cell in line.strip("|").split("|")]
        rows: list[dict[str, str]] = []
        i += 2
        while i < len(lines) and lines[i].strip().startswith("|"):
            values = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
            if len(values) == len(headers):
                rows.append(dict(zip(headers, values)))
            i += 1
        tables.append(rows)
    return tables


def strip_markdown(value: str) -> str:
    return value.replace("**", "").replace("~", "").strip()


def parse_millions(value: str) -> float:
    text = strip_markdown(value)
    match = re.search(r"([\d.]+)\s*M", text, re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not parse million value from: {value!r}")
    return float(match.group(1))


def parse_market_usd_m(value: str) -> float:
    """Return a single USD-million value.

    If the matrix stores a range such as "$38.3M-$44.0M", use the midpoint.
    If it stores a single value such as "~$93M", use that value.
    """
    text = strip_markdown(value)
    values = [float(number) for number in re.findall(r"\$?\s*([\d.]+)\s*M", text, re.IGNORECASE)]
    if not values:
        raise ValueError(f"Could not parse USD market value from: {value!r}")
    return sum(values) / len(values)


def parse_score(value: str) -> float:
    return float(strip_markdown(value))


def load_country_data() -> list[CountryData]:
    markdown = MATRIX_FILE.read_text(encoding="utf-8-sig")
    tables = parse_markdown_tables(markdown)

    original_data = next(table for table in tables if table and "Approx. Music Revenue (USD)" in table[0])
    score_data = next(table for table in tables if table and "Comprehensive score / 5" in table[0])

    base_by_country = {
        row["Country"]: {
            "population_m": parse_millions(row["Population"]),
            "market_value_usd_m": parse_market_usd_m(row["Approx. Music Revenue (USD)"]),
            "ai_interest_index": float(strip_markdown(row["AI Interest Index"])),
        }
        for row in original_data
    }

    countries: list[CountryData] = []
    for row in score_data:
        country = row["Country"]
        base = base_by_country[country]
        countries.append(
            CountryData(
                country=country,
                population_m=base["population_m"],
                market_value_usd_m=base["market_value_usd_m"],
                ai_interest_index=base["ai_interest_index"],
                comprehensive_score=parse_score(row["Comprehensive score / 5"]),
            )
        )
    return countries


def score_color(score: float) -> tuple[int, int, int]:
    # Interpolate from muted blue to vivid purple as score rises from 3.0 to 4.2.
    t = max(0.0, min(1.0, (score - 3.0) / 1.2))
    start = (104, 153, 209)
    end = (98, 54, 164)
    return tuple(round(start[i] + (end[i] - start[i]) * t) for i in range(3))


def draw_title(draw: ImageDraw.ImageDraw, title: str, subtitle: str, width: int) -> None:
    title_w, _ = text_size(draw, title, FONT_TITLE)
    draw.text(((width - title_w) / 2, 28), title, fill=(28, 35, 47), font=FONT_TITLE)
    subtitle_w, _ = text_size(draw, subtitle, FONT_SUBTITLE)
    draw.text(((width - subtitle_w) / 2, 70), subtitle, fill=(91, 99, 112), font=FONT_SUBTITLE)


def generate_score_bar_chart(data: list[CountryData]) -> Path:
    sorted_data = sorted(data, key=lambda item: item.comprehensive_score, reverse=True)

    width, height = 1280, 780
    margin_left, margin_right = 220, 130
    margin_top, margin_bottom = 130, 95
    chart_w = width - margin_left - margin_right
    row_gap = 28
    bar_h = 62
    max_score = 5.0

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw_title(
        draw,
        "Comprehensive Score by Country",
        "Final AI music localization priority score, sorted high to low",
        width,
    )

    x0 = margin_left
    x1 = width - margin_right
    y0 = margin_top

    # Grid and x-axis ticks.
    for tick in range(0, 6):
        x = x0 + chart_w * tick / max_score
        draw.line((x, y0 - 15, x, height - margin_bottom + 10), fill=(230, 234, 240), width=1)
        label = str(tick)
        label_w, _ = text_size(draw, label, FONT_SMALL)
        draw.text((x - label_w / 2, height - margin_bottom + 22), label, fill=(87, 96, 111), font=FONT_SMALL)

    axis_label = "Comprehensive score / 5"
    axis_w, _ = text_size(draw, axis_label, FONT_AXIS)
    draw.text(((x0 + x1 - axis_w) / 2, height - 48), axis_label, fill=(65, 73, 86), font=FONT_AXIS)

    for idx, item in enumerate(sorted_data):
        y = y0 + idx * (bar_h + row_gap)
        bar_w = chart_w * item.comprehensive_score / max_score
        color = score_color(item.comprehensive_score)

        draw.text((42, y + 18), f"{idx + 1}. {item.country}", fill=(35, 42, 54), font=FONT_BOLD)
        draw.rounded_rectangle((x0, y, x0 + bar_w, y + bar_h), radius=13, fill=color)
        draw.rounded_rectangle((x0, y, x1, y + bar_h), radius=13, outline=(219, 225, 233), width=2)

        score_text = f"{item.comprehensive_score:.2f}"
        score_w, score_h = text_size(draw, score_text, FONT_BOLD)
        label_x = min(x0 + bar_w + 15, x1 - score_w)
        draw.text((label_x, y + (bar_h - score_h) / 2 - 2), score_text, fill=(35, 42, 54), font=FONT_BOLD)

    out = OUTPUT_DIR / "comprehensive_score_bar.png"
    image.save(out)
    return out


def generate_bubble_chart(data: list[CountryData]) -> Path:
    width, height = 1500, 900
    margin_left, margin_right = 140, 320
    margin_top, margin_bottom = 130, 125
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom

    x_min, x_max = 10.0, 48.0
    y_values = [item.market_value_usd_m for item in data]
    y_min, y_max = min(y_values) * 0.75, max(y_values) * 1.25
    log_min, log_max = math.log10(y_min), math.log10(y_max)

    def x_pos(ai_interest: float) -> float:
        return margin_left + (ai_interest - x_min) / (x_max - x_min) * chart_w

    def y_pos(market_value: float) -> float:
        return margin_top + (log_max - math.log10(market_value)) / (log_max - log_min) * chart_h

    def radius(population_m: float) -> float:
        # Population range is tight, so use a deliberately readable bubble scale.
        return 20 + (population_m - 4.8) / (7.1 - 4.8) * 28

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image, "RGBA")
    draw_title(
        draw,
        "AI Interest vs. Music Market Value",
        "x = AI Interest Index, y = music revenue in USD millions (log scale), bubble size = population",
        width,
    )

    # Plot area background.
    draw.rounded_rectangle(
        (margin_left, margin_top, width - margin_right, height - margin_bottom),
        radius=18,
        fill=(248, 250, 253, 255),
        outline=(219, 225, 233, 255),
        width=2,
    )

    # X-axis grid.
    for tick in [10, 20, 30, 40]:
        x = x_pos(tick)
        draw.line((x, margin_top, x, height - margin_bottom), fill=(226, 231, 238, 255), width=1)
        label = str(tick)
        label_w, _ = text_size(draw, label, FONT_SMALL)
        draw.text((x - label_w / 2, height - margin_bottom + 18), label, fill=(87, 96, 111), font=FONT_SMALL)

    # Y-axis grid on log scale.
    for tick in [3, 10, 30, 100]:
        if y_min <= tick <= y_max:
            y = y_pos(tick)
            draw.line((margin_left, y, width - margin_right, y), fill=(226, 231, 238, 255), width=1)
            label = f"${tick}M"
            label_w, label_h = text_size(draw, label, FONT_SMALL)
            draw.text((margin_left - label_w - 15, y - label_h / 2), label, fill=(87, 96, 111), font=FONT_SMALL)

    # Axis labels.
    x_label = "AI Interest Index"
    x_label_w, _ = text_size(draw, x_label, FONT_AXIS)
    draw.text(((margin_left + width - margin_right - x_label_w) / 2, height - 65), x_label, fill=(65, 73, 86), font=FONT_AXIS)

    y_label = "Approx. Music Revenue (USD, log scale)"
    y_label_w, _ = text_size(draw, y_label, FONT_AXIS)
    draw.text((margin_left - 95, margin_top - 38), y_label, fill=(65, 73, 86), font=FONT_AXIS)

    label_offsets = {
        "Finland": (-115, -38),
        "Norway": (-110, -48),
        "Kuwait": (14, -4),
        "Oman": (14, 12),
        "Paraguay": (14, 10),
    }

    for item in data:
        x = x_pos(item.ai_interest_index)
        y = y_pos(item.market_value_usd_m)
        r = radius(item.population_m)
        color = score_color(item.comprehensive_score)
        fill = (*color, 205)
        outline = (*color, 255)

        draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=3)
        label = f"{item.country}\nAI {item.ai_interest_index:.1f} | ${item.market_value_usd_m:.1f}M"
        dx, dy = label_offsets.get(item.country, (12, -8))
        lx, ly = x + dx, y + dy
        for line_idx, line in enumerate(label.splitlines()):
            font = FONT_BOLD if line_idx == 0 else FONT_SMALL
            draw.text((lx, ly + line_idx * 20), line, fill=(33, 40, 52), font=font)

    # Legend.
    legend_x = width - margin_right + 40
    legend_y = margin_top + 20
    draw.text((legend_x, legend_y), "Encoding", fill=(33, 40, 52), font=FONT_BOLD)
    draw.text((legend_x, legend_y + 32), "Bubble size = population", fill=(87, 96, 111), font=FONT_SMALL)
    draw.text((legend_x, legend_y + 56), "Color = score", fill=(87, 96, 111), font=FONT_SMALL)

    for i, (score, label) in enumerate([(3.2, "Lower score"), (3.8, "Mid score"), (4.2, "Higher score")]):
        cy = legend_y + 105 + i * 48
        color = score_color(score)
        draw.ellipse((legend_x, cy - 12, legend_x + 24, cy + 12), fill=(*color, 220), outline=(*color, 255), width=2)
        draw.text((legend_x + 36, cy - 9), label, fill=(65, 73, 86), font=FONT_SMALL)

    draw.text((legend_x, legend_y + 265), "Population examples", fill=(33, 40, 52), font=FONT_BOLD)
    for i, (pop, label) in enumerate([(5.0, "5M"), (6.0, "6M"), (7.0, "7M")]):
        cy = legend_y + 315 + i * 58
        r = radius(pop)
        draw.ellipse((legend_x + 8 - r, cy - r, legend_x + 8 + r, cy + r), outline=(115, 129, 150, 255), width=2)
        draw.text((legend_x + 62, cy - 9), label, fill=(65, 73, 86), font=FONT_SMALL)

    note = "Paraguay revenue uses 2020 data; Kuwait/Oman are regional projections."
    draw.text((margin_left, height - 35), note, fill=(112, 121, 136), font=FONT_SMALL)

    out = OUTPUT_DIR / "ai_interest_market_value_bubble.png"
    image.save(out)
    return out


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = load_country_data()
    outputs = [
        generate_score_bar_chart(data),
        generate_bubble_chart(data),
    ]
    print("Generated charts:")
    for output in outputs:
        print(f"- {output}")


if __name__ == "__main__":
    main()

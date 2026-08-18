import json
import urllib.parse
import urllib.request
from datetime import datetime
import textwrap
import html

USER = "PizzaWIzza"

query = """
query ($name: String) {
  User(name: $name) {
    statistics {
      anime {
        count
        episodesWatched
        minutesWatched
        meanScore
      }
    }
    statistics {
      anime {
        statuses {
          status
          count
        }
      }
    }
  }
}
"""

watching_query = """
query ($name: String) {
  MediaListCollection(
    userName: $name
    type: ANIME
    status: CURRENT
  ) {
    lists {
      entries {
        media {
          title {
            romaji
            english
          }
          status
        }
      }
    }
  }
}
"""

monthly_query = """
query ($name: String) {
  MediaListCollection(
    userName: $name
    type: ANIME
    status: COMPLETED
  ) {
    lists {
      entries {
        completedAt {
          year
          month
          day
        }
        media {
          title {
            english
            romaji
          }
        }
      }
    }
  }
}
"""

data = json.dumps({
    "query": query,
    "variables": {"name": USER}
}).encode()

watching_data = json.dumps({
    "query": watching_query,
    "variables": {"name": USER}
}).encode()

monthly_data = json.dumps({
    "query": monthly_query,
    "variables": {"name": USER}
}).encode()

req = urllib.request.Request(
    "https://graphql.anilist.co",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PizzaWizzas-AniList-Banner/1.0"
    }
)

with urllib.request.urlopen(req) as r:
    result = json.loads(r.read().decode())

watching_req = urllib.request.Request(
    "https://graphql.anilist.co",
    data=watching_data,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PizzaWizzas-AniList-Banner/1.0"
    }
)

with urllib.request.urlopen(watching_req) as r:
    watching_result = json.loads(r.read().decode())

monthly_req = urllib.request.Request(
    "https://graphql.anilist.co",
    data=monthly_data,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PizzaWizzas-AniList-Banner/1.0"
    }
)

with urllib.request.urlopen(monthly_req) as r:
    monthly_result = json.loads(r.read().decode())

today = datetime.today()

target_year = today.year
target_month = today.month - 1

if target_month == 0:
    target_month = 12
    target_year -= 1

completed_last_month = []

for anime_list in monthly_result["data"]["MediaListCollection"]["lists"]:
    for entry in anime_list["entries"]:
        completed = entry["completedAt"]

        if completed["year"] == target_year and completed["month"] == target_month:
            title = html.escape(
    entry["media"]["title"]["english"] or
    entry["media"]["title"]["romaji"]
)
            completed_last_month.append(title)

watching_lines = ["Currently Watching"]

for anime_list in watching_result["data"]["MediaListCollection"]["lists"]:
    for entry in anime_list["entries"]:
        if entry["media"]["status"] == "RELEASING":
            watching_lines.append(entry["media"]["title"]["english"])

# ------------------------
# Build Currently Watching SVG
# ------------------------

watching_width = 380
watching_height = 40
watching_font_size = 15
watching_color = "#e13333"

# Timing:
# Each character takes the same amount of time to appear/disappear,
# regardless of how long the title is.
watching_appear_char_time = 0.06
watching_disappear_char_time = 0.02
watching_pause = 1

# Build a true letter-by-letter typing/deleting animation.
watching_svg_parts = []

start_time = 0.0
watching_line_starts = []

for line in watching_lines:
    watching_line_starts.append(start_time)

    # The total time for this title depends on its character count.
    watching_appear = len(line) * watching_appear_char_time
    watching_disappear = len(line) * watching_disappear_char_time
    watching_line_duration = (
        watching_appear + watching_pause + watching_disappear
    )

    start_time += watching_line_duration

watching_total_duration = start_time

for line_number, line in enumerate(watching_lines):
    start_time = watching_line_starts[line_number]

    watching_appear = len(line) * watching_appear_char_time
    watching_disappear = len(line) * watching_disappear_char_time

    char_width = watching_font_size * 0.602
    line_width = max(len(line) * char_width, 1)
    start_x = (watching_width - line_width) / 2

    char_elements = []

    for char_number, char in enumerate(line):
        x = start_x + char_number * char_width

        # Appear one character at a time from LEFT to RIGHT.
        appear_offset = (
            start_time
            + (char_number / max(len(line), 1)) * watching_appear
        )

        # Disappear one character at a time from RIGHT to LEFT.
        reverse_char_number = len(line) - 1 - char_number
        disappear_offset = (
            start_time
            + watching_appear
            + watching_pause
            + (reverse_char_number / max(len(line), 1))
            * watching_disappear
        )

        appear_times = ";".join(
            f"{appear_offset + cycle * watching_total_duration:.3f}s"
            for cycle in range(100)
        )

        disappear_times = ";".join(
            f"{disappear_offset + cycle * watching_total_duration:.3f}s"
            for cycle in range(100)
        )

        escaped_char = html.escape(char) or " "

        char_svg = (
            f'<text x="{x:.2f}" y="25" fill="{watching_color}" '
            f'font-size="{watching_font_size}px" '
            f'font-family="JetBrains Mono, monospace" '
            f'xml:space="preserve" opacity="0">'
            f'{escaped_char}'
            f'<animate attributeName="opacity" values="0;1" '
            f'dur="0.01s" begin="{appear_times}" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;0" '
            f'dur="0.01s" begin="{disappear_times}" fill="freeze"/>'
            f'</text>'
        )

        char_elements.append(char_svg)

    watching_svg_parts.append(
        "<g>\n" + "\n".join(char_elements) + "\n</g>"
    )

watching_svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{watching_width}" height="{watching_height}" '
    f'viewBox="0 0 {watching_width} {watching_height}">\n'
    f'{chr(10).join(watching_svg_parts)}\n'
    f'</svg>'
)

with open("watching.svg", "w", encoding="utf-8") as f:
    f.write(watching_svg)

anime = result["data"]["User"]["statistics"]["anime"]

completed = anime["count"]
episodes = anime["episodesWatched"]
days = round(anime["minutesWatched"] / 60 / 24, 1)
mean = anime["meanScore"]

planned = 0
for s in anime["statuses"]:
    if s["status"] == "PLANNING":
        planned = s["count"]

lines = [
    f"{completed} Anime Completed",
    f"{episodes} Episodes Watched",
    f"{days} Days Watched",
    f"Mean Score ★ {mean}"
]

# ------------------------
# Build Continuous Scrolling Banner
# ------------------------

banner_text = "  •  ".join(lines)
font_size = 15
svg_width = 380
svg_height = 40

# Estimate text width so two copies can form a seamless loop.
# The actual SVG uses a monospace font, so this gives a stable spacing.
text_width = max(len(banner_text) * 9, svg_width)

# Duplicate the text. The second copy begins exactly where the first ends.
# This makes the animation loop continuously without a visible reset.
banner_svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{svg_width}"
    height="{svg_height}"
    viewBox="0 0 {svg_width} {svg_height}">

  <defs>
    <clipPath id="bannerClip">
      <rect x="0" y="0" width="{svg_width}" height="{svg_height}"/>
    </clipPath>
  </defs>

  <g clip-path="url(#bannerClip)">
    <g>
      <text x="0"
            y="25"
            fill="#e13333"
            font-size="{font_size}px"
            font-family="JetBrains Mono, monospace"
            xml:space="preserve">
        {banner_text}
      </text>

      <text x="{text_width}"
            y="25"
            fill="#e13333"
            font-size="{font_size}px"
            font-family="JetBrains Mono, monospace"
            xml:space="preserve">
        {banner_text}
      </text>

      <animateTransform
        attributeName="transform"
        type="translate"
        from="0 0"
        to="-{text_width} 0"
        dur="12s"
        repeatCount="indefinite"/>
    </g>
  </g>
</svg>"""

with open("banner.svg", "w", encoding="utf-8") as f:
    f.write(banner_svg)

month_name = datetime(target_year, target_month, 1).strftime("%B")

# ------------------------
# Build Monthly Recap Text
# ------------------------

anime_text = ""
line_count = 0

for number, anime in enumerate(completed_last_month, start=1):
    wrapped = textwrap.wrap(anime, width=70)

    for i, line in enumerate(wrapped):
        x = 40 if i == 0 else 76
        prefix = f"{number}. " if i == 0 else ""

        anime_text += f"""
<text x="{x}" y="{170 + line_count * 24}"
      fill="white"
      font-size="18"
      font-family="monospace">
    {prefix}{line}
</text>"""

        line_count += 1

    # Extra spacing between anime
    line_count += 1

# ------------------------
# Footer
# ------------------------

footer_y = 170 + line_count * 24 + 10

anime_text += f"""
<line x1="40"
      y1="{footer_y}"
      x2="860"
      y2="{footer_y}"
      stroke="#ff3333"
      stroke-width="2"/>

<text x="40"
      y="{footer_y + 35}"
      fill="#b0b0b0"
      font-size="18"
      font-family="monospace">
    Total Completed: {len(completed_last_month)}
</text>
"""

# ------------------------
# SVG Size
# ------------------------

svg_height = footer_y + 60

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
     width="900"
     height="{svg_height}">

<text x="450"
      y="105"
      text-anchor="middle"
      fill="#b0b0b0"
      font-size="18"
      font-family="monospace">
{month_name} {target_year}
</text>

<line x1="40"
      y1="130"
      x2="860"
      y2="130"
      stroke="#ff3333"
      stroke-width="2"/>

{anime_text}

</svg>"""

with open("monthly.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Generated banner.svg, watching.svg, and monthly.svg")

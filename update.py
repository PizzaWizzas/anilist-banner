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

watching_# ------------------------
# Build continuously scrolling Banner SVG
# ------------------------

banner_text = (
    f"{completed} Anime Completed"
    "   •   "
    f"{episodes} Episodes Watched"
    "   •   "
    f"{days} Days Watched"
    "   •   "
    f"Mean Score ★ {mean}"
    "   •   "
)

# Keep the banner visually consistent with watching.svg.
banner_width = 600
banner_height = 40
font_size = 15

# The text is duplicated so the second copy follows the first seamlessly.
banner_svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
    width="{banner_width}"
    height="{banner_height}"
    viewBox="0 0 {banner_width} {banner_height}">

  <defs>
    <clipPath id="bannerClip">
      <rect width="{banner_width}" height="{banner_height}"/>
    </clipPath>
  </defs>

  <g clip-path="url(#bannerClip)"
     fill="#e13333"
     font-family="JetBrains Mono, monospace"
     font-size="{font_size}px"
     dominant-baseline="middle">

    <text y="{banner_height / 2}">
      <tspan x="0">{banner_text}</tspan>
      <tspan x="{banner_width}">{banner_text}</tspan>

      <animateTransform
        attributeName="transform"
        type="translate"
        from="0 0"
        to="-{banner_width} 0"
        dur="12s"
        repeatCount="indefinite"/>
    </text>

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

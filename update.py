import json
import urllib.parse
import urllib.request
from datetime import datetime
import textwrap

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
            title = entry["media"]["title"]["english"] or entry["media"]["title"]["romaji"]
            completed_last_month.append(title)

print(completed_last_month)

print(monthly_result)

watching_lines = ["Currently Watching", ""]

for anime_list in watching_result["data"]["MediaListCollection"]["lists"]:
    for entry in anime_list["entries"]:
        if entry["media"]["status"] == "RELEASING":
            watching_lines.append(entry["media"]["title"]["english"])

watching_params = {
    "font": "JetBrains Mono",
    "size": "15",
    "duration": "2300",
    "pause": "700",
    "color": "e13333",
    "center": "true",
    "vCenter": "true",
    "width": "600",
    "lines": ";".join(watching_lines)
}

watching_url = (
    "https://readme-typing-svg.demolab.com/?"
    + urllib.parse.urlencode(watching_params)
)

watching_req = urllib.request.Request(
    watching_url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(watching_req) as r:
    watching_svg = r.read()

with open("watching.svg", "wb") as f:
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

params = {
    "font": "JetBrains Mono",
    "size": "15",
    "duration": "2300",
    "pause": "700",
    "color": "e13333",
    "center": "true",
    "vCenter": "true",
    "width": "380",
    "lines": ";".join(lines)
}

url = "https://readme-typing-svg.demolab.com/?" + urllib.parse.urlencode(params)

request = urllib.request.Request(
    url,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

with urllib.request.urlopen(request) as response:
    svg = response.read()

with open("banner.svg", "wb") as f:
    f.write(svg)

month_name = datetime(target_year, target_month, 1).strftime("%B")

anime_text = ""

y = 140

for anime in completed_last_month:
    wrapped = textwrap.wrap(anime, width=50)

    for i, line in enumerate(wrapped):
        x = 70 if i == 0 else 92
        prefix = "✓ " if i == 0 else ""

        anime_text += f"""
<text x="{x}" y="{y}"
      fill="white"
      font-size="18"
      font-family="Arial">
    {prefix}{line}
</text>
"""
        y += 24

    y += 6

svg_height = 170 + len(completed_last_month) * 30

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{svg_height}">

<rect width="100%" height="100%" fill="#111111"/>

<text x="300" y="50"
      text-anchor="middle"
      fill="white"
      font-size="28"
      font-family="Arial"
      font-weight="bold">
    MONTHLY RECAP
</text>

<text x="300" y="85"
      text-anchor="middle"
      fill="#b0b0b0"
      font-size="18"
      font-family="Arial">
    {month_name} {target_year}
</text>

{anime_text}

</svg>"""

with open("monthly.svg", "w", encoding="utf-8") as f:
    f.write(svg)

print("Generated banner.svg, watching.svg, and monthly.svg")

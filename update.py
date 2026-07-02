import json
import urllib.parse
import urllib.request

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

data = json.dumps({
    "query": query,
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
    "color": "DC2626",
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

with open("watching.svg", "wb") as f:
    f.write(svg)

print("Generated banner.svg and watching.svg")

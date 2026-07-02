import json
import urllib.request

USER_ID = 713691

query = """
query ($id: Int) {
  User(id: $id) {
    statistics {
      anime {
        count
        episodesWatched
        minutesWatched
        meanScore
      }
    }
  }
}
"""

variables = {
    "id": USER_ID
}

data = json.dumps({
    "query": query,
    "variables": variables
}).encode("utf-8")

request = urllib.request.Request(
    "https://graphql.anilist.co",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PizzaWizzas-AniList-Banner/1.0"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode())

print(result)

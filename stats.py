# Fetches public stats for the profile card and writes stats.json. Runs in the GitHub Action with its GITHUB_TOKEN.
import json, os, pathlib, urllib.request
USER = os.environ.get('PROFILE_USER', 'Harris-py')
Q = '''query($login: String!) { user(login: $login) {
  repositories(ownerAffiliations: OWNER, privacy: PUBLIC) { totalCount }
  contributionsCollection { contributionCalendar { totalContributions } totalCommitContributions totalPullRequestContributions } } }'''
req = urllib.request.Request('https://api.github.com/graphql', json.dumps({'query': Q, 'variables': {'login': USER}}).encode(),
                             {'Authorization': f"bearer {os.environ['GITHUB_TOKEN']}", 'Content-Type': 'application/json'})
u = json.load(urllib.request.urlopen(req))['data']['user']
c = u['contributionsCollection']
stats = {'repos': f"{u['repositories']['totalCount']:,}", 'contributions': f"{c['contributionCalendar']['totalContributions']:,}",
         'commits': f"{c['totalCommitContributions']:,}", 'prs': f"{c['totalPullRequestContributions']:,}"}
(pathlib.Path(__file__).parent / 'stats.json').write_text(json.dumps(stats, indent=2) + '\n')
print(stats)

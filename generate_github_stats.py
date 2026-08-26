import os
import urllib.request
import json
import datetime
from datetime import timedelta

USERNAME = "Hour-Meng"
THEME = {
    "bg": "#1a1b27",
    "title": "#70a5fd",
    "text": "#9aa5ce",
    "stat": "#bf91f3",
    "icon": "#38bdae",
    "ring": "#38bdae"
}

def fetch_graphql(token, query):
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query}).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_contribution_data(token):
    # Fetch contribution data for the past year to calculate streaks
    query = """
    query {
      user(login: "%s") {
        createdAt
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """ % USERNAME
    return fetch_graphql(token, query)

def get_historical_data(token, created_at):
    # Ideally, we should fetch from created_at to now, but that requires multiple queries.
    # For simplicity, we just use the past year's data for streak calculation, which is standard
    # unless we do complex multi-year queries. Let's do a multi-year query if we want accurate longest streak.
    # To avoid API rate limits and complexity in a simple script, we'll fetch up to 3 years back.
    # But let's start with just the last year for this script.
    pass

def calculate_stats(data):
    if not data or 'data' not in data or not data['data']['user']:
        return None

    calendar = data['data']['user']['contributionsCollection']['contributionCalendar']
    total_contributions = calendar['totalContributions']

    days = []
    for week in calendar['weeks']:
        for day in week['contributionDays']:
            days.append({
                'date': day['date'],
                'count': day['contributionCount']
            })

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    # Check today's date
    today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')

    for i, day in enumerate(days):
        if day['count'] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Current streak calculation (backwards from today)
    days_reversed = list(reversed(days))

    has_contributed_today = False

    for i, day in enumerate(days_reversed):
        if i == 0 and day['date'] == today:
            if day['count'] > 0:
                has_contributed_today = True
                current_streak += 1
            continue

        if day['count'] > 0:
            current_streak += 1
        else:
            # If we didn't contribute today, but we contributed yesterday, the streak is valid
            if i == 1 and not has_contributed_today and day['date'] == yesterday:
                if day['count'] > 0:
                    current_streak += 1
                else:
                    break
            else:
                break

    return {
        'total': total_contributions,
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'days': days
    }

def generate_streak_svg(stats):
    svg = f"""<svg width="495" height="195" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 600; font-size: 18px; fill: {THEME['title']}; }}
        .stat {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 700; font-size: 28px; fill: {THEME['stat']}; }}
        .label {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 400; font-size: 14px; fill: {THEME['text']}; }}
        .date {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 400; font-size: 12px; fill: {THEME['text']}; opacity: 0.8; }}
    </style>
    <rect x="0" y="0" width="495" height="195" fill="{THEME['bg']}" rx="15"/>
    <!-- Total Contributions -->
    <g transform="translate(80, 40)">
        <circle cx="0" cy="50" r="40" fill="none" stroke="{THEME['ring']}" stroke-width="4" opacity="0.2"/>
        <circle cx="0" cy="50" r="40" fill="none" stroke="{THEME['ring']}" stroke-width="4" stroke-dasharray="250" stroke-dashoffset="0"/>
        <text x="0" y="45" class="stat" text-anchor="middle" dominant-baseline="middle">{stats['total'] if stats else 0}</text>
        <text x="0" y="110" class="label" text-anchor="middle">Total Contributions</text>
    </g>

    <!-- Current Streak -->
    <g transform="translate(247.5, 40)">
        <circle cx="0" cy="50" r="40" fill="none" stroke="{THEME['ring']}" stroke-width="4" opacity="0.2"/>
        <circle cx="0" cy="50" r="40" fill="none" stroke="{THEME['ring']}" stroke-width="4" stroke-dasharray="250" stroke-dashoffset="0"/>
        <text x="0" y="45" class="stat" text-anchor="middle" dominant-baseline="middle">{stats['current_streak'] if stats else 0}</text>
        <text x="0" y="110" class="label" text-anchor="middle">Current Streak</text>
    </g>

    <!-- Longest Streak -->
    <g transform="translate(415, 40)">
        <circle cx="0" cy="50" r="40" fill="none" stroke="{THEME['ring']}" stroke-width="4" opacity="0.2"/>
        <circle cx="0" cy="50" r="40" fill="none" stroke="{THEME['ring']}" stroke-width="4" stroke-dasharray="250" stroke-dashoffset="0"/>
        <text x="0" y="45" class="stat" text-anchor="middle" dominant-baseline="middle">{stats['longest_streak'] if stats else 0}</text>
        <text x="0" y="110" class="label" text-anchor="middle">Longest Streak</text>
    </g>
</svg>"""
    with open("github_streak.svg", "w") as f:
        f.write(svg)

def generate_graph_svg(stats):
    if not stats:
        days = [{'count': 0}] * 365
    else:
        days = stats['days'][-365:] # Last 365 days

    width = 1000
    height = 300

    # Calculate graph path
    points = []
    x_step = width / (len(days) or 1)
    max_count = max([d['count'] for d in days]) if days else 1
    if max_count == 0: max_count = 1

    for i, day in enumerate(days):
        x = i * x_step
        y = height - 50 - (day['count'] / max_count * (height - 100))
        points.append(f"{x},{y}")

    path_d = f"M0,{height-50} L" + " L".join(points) + f" L{width},{height-50} Z"
    line_d = "M" + " L".join(points)

    svg = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 600; font-size: 20px; fill: {THEME['title']}; }}
        .text {{ font-family: 'Segoe UI', Ubuntu, sans-serif; font-weight: 400; font-size: 14px; fill: {THEME['text']}; }}
    </style>
    <rect x="0" y="0" width="{width}" height="{height}" fill="{THEME['bg']}" rx="15"/>
    <text x="30" y="40" class="title">Contribution Graph</text>

    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="{THEME['icon']}" stop-opacity="0.5" />
            <stop offset="100%" stop-color="{THEME['bg']}" stop-opacity="0.1" />
        </linearGradient>
    </defs>

    <g transform="translate(0, 20)">
        <path d="{path_d}" fill="url(#grad)" />
        <path d="{line_d}" fill="none" stroke="{THEME['icon']}" stroke-width="2" />
    </g>
</svg>"""
    with open("github_contribution_graph.svg", "w") as f:
        f.write(svg)

def main():
    token = os.environ.get('GH_TOKEN')

    if token:
        print("Fetching data from GitHub...")
        data = get_contribution_data(token)
        stats = calculate_stats(data)
    else:
        print("GH_TOKEN not found. Generating sample SVG for local testing.")
        stats = {
            'total': 1337,
            'current_streak': 42,
            'longest_streak': 100,
            'days': [{'count': i % 5} for i in range(365)]
        }

    print("Generating SVGs...")
    generate_streak_svg(stats)
    generate_graph_svg(stats)
    print("Done!")

if __name__ == "__main__":
    main()

from app.tools.datetime_tool import get_datetime
from app.tools.weather import get_weather
from app.tools.filesystem import read_file, count_files, create_file
from app.tools.github import github_trending, git_commit
from app.tools.habr import habr_articles
from app.tools.slack import slack_channels, slack_send

ALL_TOOLS = [get_datetime, get_weather,
             read_file, count_files, create_file,
             github_trending, git_commit,
             habr_articles,
             slack_channels, slack_send]

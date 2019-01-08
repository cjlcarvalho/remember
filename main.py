import argparse
import random
import requests
import yaml

from datetime import datetime
from termcolor import colored


AUTH_PATH = "auth.yaml"


def load_configuration():

    with open(AUTH_PATH, "r") as f:
        config = yaml.load(f)

    return config


def repositories(config):

    repositories_url = f"{config['api']}/user/repos"
    page = 1
    result = []

    while True:
        req = requests.get(
            repositories_url,
            params={"access_token": config["token"], "per_page": 200, "page": page},
        )

        if req.status_code == 200:
            js = req.json()
            if js == []:
                break
            for elem in js:
                result.append(
                    (
                        elem["name"],
                        elem["html_url"],
                        elem["description"],
                        elem["updated_at"],
                    )
                )
            page += 1
        else:
            break

    return result


def get_contents(config, repository_name):

    contents_url = (
        f"{config['api']}/repos/{config['username']}/{repository_name}/contents"
    )

    req = requests.get(contents_url, params={"access_token": config["token"]})

    if req.status_code == 200:
        return req.json()
    return []


def print_info(repository):

    print("#", colored(repository[0], "cyan"))
    print("\t- Description:", colored(repository[2], "red"))
    print("\t- URL:", colored(repository[1], "red"), "\n")


def print_quote():

    quotes = [
        '"When we die, we will turn into songs, and we will hear each other and remember each other."',
        "\"If you didn't remember something happening, was it because it never had happened? Or because you wished it hadn't?\"",
        '"Remember to breathe. It is after all, the secret of life."',
        '"But the thing about remembering is that you don\'t forget."',
        '"Memory was a curse, yes, he thought, but it was also the greatest gift. Because if you lost memory you lost everything."',
    ]

    quote = random.choice(quotes)

    print(colored("\t" + quote, "red"), "\n\n")


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--empty", help="shows empty repositories", action="store_true")
    parser.add_argument(
        "--abandoned",
        type=int,
        help="shows repositories abandoned for a specific number of days",
    )
    args = parser.parse_args()

    config = load_configuration()
    repos = repositories(config)

    print(
        colored(
            """

 _  .-')     ('-.  _   .-')       ('-.  _   .-')   .-. .-')    ('-.  _  .-')
( \( -O )  _(  OO)( '.( OO )_   _(  OO)( '.( OO )_ \  ( OO ) _(  OO)( \( -O )
 ,------. (,------.,--.   ,--.)(,------.,--.   ,--.);-----.\(,------.,------.
 |   /`. ' |  .---'|   `.'   |  |  .---'|   `.'   | | .-.  | |  .---'|   /`. '
 |  /  | | |  |    |         |  |  |    |         | | '-' /_)|  |    |  /  | |
 |  |_.' |(|  '--. |  |'.'|  | (|  '--. |  |'.'|  | | .-. `.(|  '--. |  |_.' |
 |  .  '.' |  .--' |  |   |  |  |  .--' |  |   |  | | |  \  ||  .--' |  .  '.'
 |  |\  \  |  `---.|  |   |  |  |  `---.|  |   |  | | '--'  /|  `---.|  |\  \ 
 `--' '--' `------'`--'   `--'  `------'`--'   `--' `------' `------'`--' '--'

            """,
            "yellow",
        )
    )

    print_quote()

    if args.empty:
        empty_repos = filter(
            lambda repo: len(get_contents(config, repo[0])) == 0, repos
        )
        print(colored("\t[[ EMPTY REPOSITORIES ]]\n", "magenta"))
        for repo in empty_repos:
            print_info(repo)

    if args.abandoned:
        abandoned_repos = filter(
            lambda repo: (
                datetime.now() - datetime.strptime(repo[3], "%Y-%m-%dT%H:%M:%SZ")
            ).days
            >= args.abandoned,
            repos,
        )
        print(colored("\t[[ ABANDONED REPOSITORIES ]]\n", "magenta"))
        for repo in abandoned_repos:
            print_info(repo)


if __name__ == "__main__":

    main()

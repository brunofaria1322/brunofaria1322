from github import Github
import re
import os

def make_graph(percent: float):
    '''Make progress graph from API graph'''
    done_block = '█'
    empty_block = '░'
    pc_rnd = round(percent)
    return done_block * int(pc_rnd / 4)+empty_block *(25 - int(pc_rnd / 4))


def make_commit_list(data: list):
    '''Make List'''
    data_list = []
    for l in data:
        ln = len(l['name'])
        ln_text = len(l['text'])
        op = l['name']+ ' ' * (13 - ln) + l['text']+ ' ' * (15 - ln_text) + make_graph(l['percent']) + "\t" + str(l['percent']) +"%"
        data_list.append(op)
    return ' \n'.join(data_list)


def generate_content(user):

    morning = 0  # 6 - 12
    daytime = 0  # 12 - 18
    evening = 0  # 18 - 24
    night = 0    # 0 - 6

    languages = dict()

    # Then play with your Github objects:
    for repo in user.get_repos():
        if repo.fork:
            continue
        
        for commit in repo.get_commits():
            if commit.commit.author.name != user.login:
                continue

            hour = commit.commit.author.date.hour
        
            if 6 <= hour < 12:
                morning += 1
            elif 12 <= hour < 18:
                daytime += 1
            elif 18 <= hour < 24:
                evening += 1
            else:
                night += 1

        for key, value in repo.get_languages().items():
            if key not in languages:
                languages[key] = value
            else:
                languages[key] += value 


    sumAll = morning + daytime + evening + night

    title = 'I am an Early guy 🌞' if morning + daytime >= evening + night else 'I am a Night guy 🌙'
    one_day = [
        {"name": "🌞 Morning", "text": str(morning) + " commits", "percent": round((morning / sumAll) * 100, 2)},
        {"name": "🌆 Daytime", "text": str(daytime) + " commits", "percent": round((daytime / sumAll) * 100, 2)},
        {"name": "🌃 Evening", "text": str(evening) + " commits", "percent": round((evening / sumAll) * 100, 2)},
        {"name": "🌙 Night"  , "text": str(night)   + " commits", "percent": round((night   / sumAll) * 100, 2)}
    ]

    string = "**" + title + "** \n\n" + "```text\n" + make_commit_list(one_day) + "\n\n```\n"

    title = 'What I most programm'


    languages_full = []
    sum_lang = sum(languages.values())

    languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)

    for lang in languages:
        temp = dict()
        temp['name'] = lang[0]
        temp['text'] = str(lang[1]) + " bytes"
        temp['percent'] = round((lang[1]/sum_lang) * 100,2)

        languages_full.append(temp)

    string = string + "**" + title + "** \n\n" + "```text\n" + make_commit_list(languages_full) + "\n```\n\n"
    return string

if __name__ == "__main__":
    START_COMMENT = '<!--START_SECTION:waka-->'
    END_COMMENT = '<!--END_SECTION:waka-->'
    listReg = f"{START_COMMENT}[\\s\\S]+{END_COMMENT}"


    # Create a Github instance using an access token:
    ghtoken = os.getenv('INPUT_GH_TOKEN')
        
    if ghtoken is None:
        print('Token not available')
        exit()

    g = Github(ghtoken)
    user = g.get_user()

    stats = generate_content(user)

    readme_repo = user.get_repo(user.login)
    readme = readme_repo.get_readme()

    readme_decoded =  str(readme.decoded_content, 'utf-8')

    readme_new_sats = "{}\n{}\n{}".format(START_COMMENT,stats,END_COMMENT)

    readme_new = re.sub(listReg, readme_new_sats, readme_decoded)

    readme_repo.update_file(path=readme.path, message= "Automatically updated", content=readme_new, sha=readme.sha, branch='master')

    print("Readme updated")
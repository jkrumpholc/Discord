import re
import difflib
import Mal_Api
anime_correct_names = {}
with open("../Anime.txt", encoding="utf-8") as source:
    content = source.read()
    list_anime = re.findall("\*\*\*Watched\*\*\*:\n([^\*]+)\n\n", content)[0].split("\n")
    for anime_name in list_anime:
        anime_name = anime_name.split("(")[0].split("[")[0].split("{")[0]
        anime_list = Mal_Api.find_anime(anime_name)
        titles = [i['node']['title'] for i in anime_list]
        guess = difflib.get_close_matches(word=anime_name, possibilities=titles, cutoff=0.6, n=1)
        if len(guess) > 0:
            guess = guess[0]
        else:
            print(f'{anime_name} cannot be found in MAL, using first result')
            if len(anime_list) > 0:
                guess = anime_list[0]['node']['title'] + " **maybe**"
            elif anime_name == '---------------------------------------------------------------':
                continue
            else:
                print(f'{anime_name} cannot be found in MAL')
                exit(1)
        anime_correct_names[anime_name] = guess
print(anime_correct_names)

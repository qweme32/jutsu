#        _       _    _____
#       | |     | |  / ____|
#       | |_   _| |_| (___  _   _
#   _   | | | | | __|\___ \| | | |
#  | |__| | |_| | |_ ____) | |_| |
#   \____/ \__,_|\__|_____/ \__,_|
#
#  Easy download your favorite anime from jut.su
#  by @qweme32

from ctypes import util
import os
import sys
import colorama

import utils


app_meta = utils.AppMetadata(
    title="First release",
    description="+ Anime download\n+ Anime films download\n+ Simple console UI",
    version=1.1,
    timestamp=1660401492
)


def main(argv) -> int:
    utils.clear_con()

    if utils.check_new_version(app_meta):
        print(utils.ERROR_CURSOR + "Вышла новая версия программы\n  Скачать можно на https://github.com/qweme32/jutsu")

    utils.print_logo()

    anime = input(utils.COLOR_CURSOR)
    if anime == "":
        utils.exit_app("Неправильный параметр!")

    anime_page = utils.get_anime_page(anime)
    anime_data = utils.parse_anime_page(anime_page)

    utils.clear_con()
    print(colorama.Fore.LIGHTBLUE_EX +
          f"Название: {colorama.Fore.LIGHTYELLOW_EX}{anime_data['title']}")
    print(colorama.Fore.LIGHTBLUE_EX +
          f"Теги: {colorama.Fore.LIGHTCYAN_EX}{', '.join(anime_data['tags'])}")

    print(colorama.Fore.LIGHTBLACK_EX + "\nСезоны: ")
    for season in anime_data["seasons"]:
        print(colorama.Fore.LIGHTGREEN_EX +
              f" {season}) {len(anime_data['seasons'][season])} эпизодов.")
    if not len(anime_data["seasons"]):
        print(colorama.Fore.LIGHTRED_EX + " Тут ничего нет.")

    print(colorama.Fore.LIGHTBLACK_EX + "\nФильмы: ")
    for film in anime_data["films"]:
        print(colorama.Fore.LIGHTGREEN_EX + f" {film}) Фильм {film}")
    if not len(anime_data["films"]):
        print(colorama.Fore.LIGHTRED_EX + " Тут ничего нет.")

    print(colorama.Fore.WHITE +
          f"\nВведите сезон / фильм который хотите скачать\n{colorama.Fore.LIGHTBLACK_EX}\nПример #1: S1 (скачать первый сезон)\nПример #2: F2 (скачать второй фильм)")
    print(colorama.Fore.LIGHTMAGENTA_EX +
          "\nДоступные параметры: ", end=colorama.Fore.WHITE)

    allow_params = {}
    for s in anime_data["seasons"]:
        allow_params[f"S{s}"] = anime_data["seasons"][s]
        print(f"S{s}", end=", ")

    for f in anime_data["films"]:
        allow_params[f"F{f}"] = anime_data["films"][f]
        print(f"F{f}", end=", ")

    select = input("\n\n" + utils.COLOR_CURSOR)

    if select.upper() not in allow_params:
        utils.exit_app("Неправильный параметр!")

    if select.upper()[0] == "S":
        max_ = len(anime_data['seasons'][int(select.upper()[1])])
        from_ = int(input(colorama.Fore.LIGHTBLUE_EX +
                    f"\nС какой серии качать (Максимум: {max_}): "))
        to_ = int(input(colorama.Fore.LIGHTRED_EX +
                  f"До какой серии качать (Максимум: {max_}): "))
        quality_ = input(colorama.Fore.LIGHTYELLOW_EX +
                         f"Качество видео (360, 480, 720, 1080): ")

        if from_ <= 0 or from_ > max_:
            utils.exit_app("Начальная серия не в списке!")

        if to_ <= 0 or to_ > max_:
            utils.exit_app("Конечная серия не в списке!")

        if from_ > to_:
            utils.exit_app("Начальная серия не может быть больше конечной!")

        if quality_ not in ["360", "480", "720", "1080"]:
            utils.exit_app("Неправильное разрешение!")

        season = anime_data['seasons'][int(select.upper()[1])]

        to_download: list[utils.JutSuVideoSource] = []
        for video in range(from_, to_+1):
            page = utils.JutSuVideoPage(video, season[video-1]["url"])
            page.fetch(utils.session)

            to_download.append(page.srcs[quality_])

        path = f"./{anime_data['title']} (S{select.upper()[1]}) ({quality_}p)"

        if not os.path.exists(path):
            os.mkdir(path)

        utils.clear_con()
        print(colorama.Fore.LIGHTGREEN_EX +
              "Ход работы: \n" + colorama.Fore.LIGHTCYAN_EX)

        download_log = "JutSu Download Log\n"
        errors = 0

        for src in to_download:
            try:
                code = src.download(
                    utils.session, f"{path}/{src.title} (Эпизод {src.ep}).mp4")

                if code == "0":
                    errors += 1
                    download_log += "\n" + \
                        f"[{path}/{src.title} (Эпизод {src.ep}).mp4] - " + \
                        "Ошибка скачивания (invalid session)"
                else:
                    download_log += "\n" + \
                        f"[{path}/{src.title} (Эпизод {src.ep}).mp4] - " + \
                        "Успешно!"
            except Exception as err:
                errors += 1
                download_log += "\n" + \
                    f"[{path}/{src.title} (Эпизод {src.ep}).mp4] - " + \
                    f"Ошибка скачивания ({err})"

        if errors:
            log_file = open(path+"/error.log", "w", encoding="utf-8")
            log_file.write(download_log)
            log_file.close()

        print(colorama.Style.RESET_ALL + "\n\n\nСпасибо что воспользовались моей утилитой, если не сложно поставь звездочку (лайк) на гитхабе\n\nhttps://github.com/qweme32/jutsu")

        return 0

    else:
        quality_ = input(colorama.Fore.LIGHTYELLOW_EX +
                         f"\nКачество видео (360, 480, 720, 1080): ")

        if quality_ not in ["360", "480", "720", "1080"]:
            utils.exit_app("Неправильное разрешение!")

        page = utils.JutSuVideoPage(
            int(select[1]), anime_data["films"][int(select[1])])
        page.fetch(utils.session)

        film_src: utils.JutSuVideoSource = page.srcs[quality_]

        path = f"./{anime_data['title']} (Фильм) ({quality_}p)"
        if not os.path.exists(path):
            os.mkdir(path)

        utils.clear_con()
        print(colorama.Fore.LIGHTGREEN_EX +
              "Ход работы: \n" + colorama.Fore.LIGHTCYAN_EX)
        film_src.download(utils.session, path +
                          f"/{film_src.title} (Фильм {select[1]}).mp4")

        print(colorama.Style.RESET_ALL + "\n\n\nСпасибо что воспользовались моей утилитой, если не сложно поставь звездочку (лайк) на гитхабе\n\nhttps://github.com/qweme32/jutsu")

        return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except KeyboardInterrupt:
        print(colorama.Fore.LIGHTYELLOW_EX + "\n\nBye bye!" + colorama.Style.RESET_ALL)

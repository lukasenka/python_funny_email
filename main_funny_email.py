import requests
import json
import smtplib
import re
import pickle
import os
import logging

from email.message import EmailMessage
from logins import SMTP_SERVER, PASSWORD, USERNAME, DEFAULT_EMAIL, SMTP_PORT
from PIL import Image, ImageEnhance, ImageFilter

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lentele import Emailas

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


desktop = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")

vieta = f"{desktop}\\Projektas"
vieta_failo = f"{desktop}\\Projektas\\stats.txt"

os.makedirs(vieta, exist_ok=True)

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(vieta_failo)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
file_handler.setFormatter(formatter)

engine = create_engine("sqlite:///emails.db")
Session = sessionmaker(bind=engine)
session = Session()


try:
    with open("stats.pkl", "rb") as failas:
        ijungimas = pickle.load(failas)
    if ijungimas == 0:
        print("[INFO] Paveiksleliu parametrai bus isjungti.")
        print("*" * 50)
    elif ijungimas == 1:
        print("[INFO] Paveiksleliu parametrai bus ijungti.")
        print("*" * 50)
except (EOFError, FileNotFoundError):
    print("Nera duomenu!")
    print("[INFO] Paveiksleliu parametrai bus isjungti.")
    print("*" * 50)
    ijungimas = 0

ryskumas = 0


class Anekdotas:

    @staticmethod
    def params(host, endpoint, payload_k="", payload_v=""):

        if payload_k != "" and payload_v != "":
            payload_ = {payload_k: payload_v}
            r = requests.get(host + endpoint, params=payload_)
        else:
            r = requests.get(host + endpoint)

        res_dict = json.loads(r.text)

        logger.info(f"Anekdotas.params() -> {res_dict}")

        return res_dict

    @staticmethod
    def random_joke():

        api_host = "https://api.chucknorris.io/jokes/"

        endpoint = "random"

        res_dict = Anekdotas().params(api_host, endpoint)

        logger.info(f"Anekdotas.random_joke() -> {res_dict['value']}")

        return res_dict["value"]

    @staticmethod
    def joke_filter_by_category(category_):
        api_host = "https://api.chucknorris.io/jokes/"

        endpoint = "categories"
        endpoint2 = "random"

        res_dict_categories = Anekdotas().params(api_host, endpoint)
        res_dict_categories_filter = Anekdotas().params(api_host, endpoint2, "category", category_)

        try:
            if res_dict_categories_filter["status"] == 404:

                logger.info(f"Anekdotas.joke_filter_by_category() [ERROR] -> Category not found. "
                            f"Available categories list: {res_dict_categories}")
                return f"Category not found. Available categories list: {res_dict_categories}"

        except KeyError:
            pass

        logger.info(f"Anekdotas.joke_filter_by_category() -> {res_dict_categories_filter['value']}")

        return res_dict_categories_filter["value"]

    @staticmethod
    def joke_search(joke):
        api_host = "https://api.chucknorris.io/jokes/"

        endpoint = "search"

        res_dict_jokes = Anekdotas().params(api_host, endpoint, "query", joke)

        try:
            if res_dict_jokes["status"] == 400:

                logger.info(f"Anekdotas.joke_search() -> [ERROR] {res_dict_jokes['violations']['search.query']}")

                return f"[ERROR] {res_dict_jokes['violations']['search.query']}"
        except KeyError:
            pass

        if res_dict_jokes["total"] == 0:
            logger.info(f"Anekdotas.joke_search() -> [ERROR] Joke not found.")
            return "Joke not found."

        listas = []
        for xx in range(res_dict_jokes["total"]):
            listas.append(res_dict_jokes["result"][xx]["value"])

        logger.info("Anekdotas.joke_search() -> [OK] Listas sudarytas.")
        return listas


def email_options(pasirink__, emailas):
    if pasirink__ == "":
        with open("dog.jpg", mode="rb") as file:
            content = file.read()
            img = Image.open("dog.jpg")
            emailas.add_attachment(
                content,
                maintype=f"image/{img.format}",
                subtype=f"{img.format}",
                filename="dog.jpg"
            )
    else:
        with open(pasirink__, mode="rb") as file:
            content = file.read()
            img = Image.open(pasirink__)
            emailas.add_attachment(
                content,
                maintype=f"image/{img.format}",
                subtype=f"{img.format}",
                filename=pasirink__
            )


def email_send(emailas):

    with smtplib.SMTP(host=SMTP_SERVER, port=SMTP_PORT) as smpt:
        smpt.ehlo()
        smpt.starttls()
        smpt.login(USERNAME, PASSWORD)
        smpt.send_message(emailas)

    logger.info("email_send() -> [OK] Laiskas issiustas.")


def check_file_exists(choose):
    if choose == "":
        image = Image.open('dog.jpg')
        choose = "dog.jpg"
        return choose, image
    else:
        try:
            image = Image.open(choose)
            return choose, image
        except FileNotFoundError:
            print("Nerastas failas. Bus naudojamas - dog.jpg")
            image = Image.open('dog.jpg')
            choose = "dog.jpg"
            return choose, image


def validate_email(kieno):
    while True:
        emailas = input(f"Iveskite {kieno} el. pasto adresa [Enter - naudojamas sistemis]\n")

        if emailas == "":
            emailas = DEFAULT_EMAIL
            logger.info("validate_email() -> [WARNING] Email laukelis tuscias, bus naudojamas sisteminis.")
            return emailas

        pattern = r"^[0-9a-z._-]+@[0-9a-z._-]+\.[a-z]{2,6}$"
        res = re.search(pattern, emailas.lower())
        if res:
            logger.info(f"validate_email() -> [OK] Gautas email : {emailas}")
            return emailas
        else:
            print("Neteisingas el. pasto adresas.")
            logger.info(f"validate_email() -> [ERROR] Neteisingas el. pasto adresas. Gautas email : {emailas}")
            continue


def get_gender_from_name(name):
    api_host = "https://api.genderize.io"

    payload = {"name": name}

    r = requests.get(api_host, params=payload)

    r_dict = json.loads(r.text)

    if r_dict["gender"] == "male":
        logger.info(f"get_gender_from_name() - GET {r_dict}, VALUE {r_dict['gender']}, RETURN vyras")
        return "vyras"
    elif r_dict["gender"] == "female":
        logger.info(f"get_gender_from_name() - GET {r_dict}, VALUE {r_dict['gender']}, RETURN moteris")
        return "moteris"


def transpose(image, method):

    if method == "b":
        tr = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return tr
    elif method == "r":
        tr = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        return tr
    elif method == "90":
        tr = image.transpose(Image.Transpose.ROTATE_90)
        return tr
    elif method == "180":
        tr = image.transpose(Image.Transpose.ROTATE_180)
        return tr
    elif method == "270":
        tr = image.transpose(Image.Transpose.ROTATE_270)
        return tr
    elif method == "t":
        tr = image.transpose(Image.Transpose.TRANSPOSE)
        return tr
    else:
        return None


if __name__ == "__main__":

    user_choices = """1. Siusti el. laiska
2. Paveiksleliu nustatymai\n3. Laisku statistikos (diagrama)\n"""

    while True:

        pasirinkimas = input(user_choices)

        if pasirinkimas == "":
            break
        elif pasirinkimas == "1":

            from_who = input("Iveskite savo varda: ")
            from_email = validate_email("savo")
            to_email = validate_email("gavejo")
            subjectas = input("Iveskite laisko antrastes tema: ")
            turinys_input = input("Iveskite norima laiska: ")
            parasas = input("Prideti parasa. [Enter - praleisti]: ")
            anekdotas = input("""Prideti anekdota paraso pabaigoje: [Jeigu parasas nenaudojimas - Enter, praleisti]
            1. Atsitiktinis anekdotas
            2. Anekdotas pagal kategorija
            3. Anekdoto paieska\n""")

            email = EmailMessage()

            if from_email == "":
                from_email = DEFAULT_EMAIL
                email["from"] = f"{from_who} <{DEFAULT_EMAIL}>"
            else:
                email["from"] = f"{from_who} <{from_email}>"

            if to_email == "":
                to_email = DEFAULT_EMAIL
                email["to"] = DEFAULT_EMAIL
            else:
                email["to"] = f"{to_email}"

            email["subject"] = subjectas

            if parasas == "":
                turinys = turinys_input

                eilute_obj = Emailas(from_who, get_gender_from_name(from_who), from_email, to_email,
                                     subjectas, turinys_input, parasas, "0")  # sukuriamas eilutes objektas
                session.add(eilute_obj)  # pridedam
                session.commit()  # issaugojimas faile

                email.set_content(turinys)
                email_send(email)
                print("[INFO] Laiskas issiustas.")
                break
            else:
                turinys = turinys_input + "\n---------\n" + parasas

            if anekdotas == "1":
                if parasas != "":
                    while True:
                        rastas_anekdotas = Anekdotas.random_joke()
                        tinkamumas = input(f"Rastas anekdotas: {rastas_anekdotas}."
                                           f" Ar jis jums tinka? Taip - T, Ne - N\n")

                        if tinkamumas == "T":
                            turinys = turinys_input + "\n---------\n" + parasas + "\n---------\n" + rastas_anekdotas

                            eilute_obj = Emailas(from_who, get_gender_from_name(from_who),
                                                 from_email, to_email,
                                                 subjectas, turinys_input, parasas,
                                                 rastas_anekdotas)  # sukuriamas eilutes objektas
                            session.add(eilute_obj)  # pridedam
                            session.commit()  # issaugojimas faile
                            break
                        elif tinkamumas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    email.set_content(turinys)
                    if ijungimas == 0:
                        email_send(email)
                        print("[INFO] Laiskas issiustas.")

            elif anekdotas == "2":
                if parasas != "":
                    while True:
                        category = input("Iveskite anekdoto kategorija: ")

                        rastas_anekdotas = Anekdotas.joke_filter_by_category(category)

                        if rastas_anekdotas[:19] == "Category not found.":
                            print(rastas_anekdotas)
                            continue

                        tinkamumas = input(f"Rastas anekdotas: {rastas_anekdotas}."
                                           f" Ar jis jums tinka? Taip - T, Ne - N\n")

                        if tinkamumas == "T":
                            turinys = turinys_input + "\n---------\n" + parasas + "\n---------\n" + rastas_anekdotas

                            eilute_obj = Emailas(from_who, get_gender_from_name(from_who), from_email, to_email,
                                                 subjectas, turinys_input,
                                                 parasas, rastas_anekdotas)  # sukuriamas eilutes objektas
                            session.add(eilute_obj)  # pridedam
                            session.commit()  # issaugojimas faile
                            break
                        elif tinkamumas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    email.set_content(turinys)
                    if ijungimas == 0:
                        email_send(email)
                        print("[INFO] Laiskas issiustas.")

            elif anekdotas == "3":
                if parasas != "":
                    while True:
                        search = input("Iveskite, koki anekdota norite surasti: ")

                        rastas_anekdotas = Anekdotas.joke_search(search)

                        if rastas_anekdotas[:7] == "[ERROR]":
                            print(rastas_anekdotas)
                            continue

                        if rastas_anekdotas == "Joke not found.":
                            print("Anekdotas nerastas.")
                            continue

                        skaiciai = -1
                        print("-- Rasti anekdotai --")

                        for x in rastas_anekdotas:
                            skaiciai += 1
                            print(skaiciai, x)

                        while True:
                            try:
                                pasirink = int(input("Kuri norite pasirinkti? Iveskite anekdoto eiles numeri.\n"))
                                break
                            except ValueError:
                                print("[KLAIDA] Pasirinktas ne skaicius.")
                                pasirink = 0
                                continue

                        tinkamumas = input(f"Rastas anekdotas: {rastas_anekdotas[pasirink]}"
                                           f". Ar jis jums tinka? Taip - T, Ne - N\n")

                        if tinkamumas == "T":
                            turinys = turinys_input + "\n---------\n" + parasas + "\n---------\n"\
                                      + rastas_anekdotas[pasirink]

                            eilute_obj = Emailas(from_who, get_gender_from_name(from_who), from_email,
                                                 to_email,
                                                 subjectas, turinys_input, parasas,
                                                 rastas_anekdotas[pasirink])  # sukuriamas eilutes objektas
                            session.add(eilute_obj)  # pridedam
                            session.commit()  # issaugojimas faile

                            break
                        elif tinkamumas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    email.set_content(turinys)
                    if ijungimas == 0:
                        email_send(email)
                        print("[INFO] Laiskas issiustas.")

            if ijungimas == 1:

                pasirink_ = input(
                        "- Paveikslelio nustatymai --\n Iveskite atidaromo paveikslelio pavadinima: \n"
                        " [Enter - naudoti standartini] \n")

                if pasirink_ == "":
                    im = Image.open("dog.jpg")
                    im.save("dog_original.jpg")
                    print("[COPY] Failo dog.jpg kopija sukurta -> dog_original.jpg")
                else:
                    pasirink_ = check_file_exists(pasirink_)[0]
                    print(f"[COPY] Failo {pasirink_} kopija sukurta -> original_{pasirink_}")
                    check_file_exists(pasirink_)[1].save("original_" + pasirink_)

                while True:
                    langas = input("- Paveikslelio nustatymai --\n1 - Pakeisti dydi"
                                   " \n2 - Juodai - balta efektas\n3 - Ryskumo reguliavimas\n"
                                   "4 - Blur filtras\n5 - transpose metodai\n[Enter - Iseiti]\n")

                    if langas == "":
                        email_options(pasirink_, email)
                        email_send(email)

                        print("[INFO] Laiskas issiustas.")
                        break

                    if langas == "1":

                        im = check_file_exists(pasirink_)[1]

                        dydis = input("Pasirinkite keiciamo paveikslelio dydi (Formatas : 120x34): \n")

                        index1 = int(dydis.split("x")[0])
                        index2 = int(dydis.split("x")[1])
                        index_correct = (index1, index2)
                        resized = im.resize(index_correct)

                        resized.show()

                        teisingas = input("Ar pasirinkimai tinka? T - Taip, N - Ne\n")

                        if teisingas == "T":
                            if pasirink_ == "":
                                resized.save("dog.jpg")
                            else:
                                pasirink_ = check_file_exists(pasirink_)[0]
                                resized.save(pasirink_)

                            continue

                        elif teisingas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    elif langas == "2":

                        im = check_file_exists(pasirink_)[1]
                        konvertuotas = im.convert("L")

                        konvertuotas.show()

                        teisingas = input("Ar pasirinkimai tinka? T - Taip, N - Ne\n")

                        if teisingas == "T":
                            if pasirink_ == "":
                                konvertuotas.save("dog.jpg")
                            else:
                                pasirink_ = check_file_exists(pasirink_)[0]
                                konvertuotas.save(pasirink_)

                            continue

                        elif teisingas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    elif langas == "3":

                        im = check_file_exists(pasirink_)[1]
                        enh = ImageEnhance.Contrast(im)

                        ryskumas += 1
                        # sviesinam kas 10 proc.
                        im = Image.open('dog.jpg')
                        enhas = ImageEnhance.Brightness(im)
                        enhanced_im = enhas.enhance(2.5*ryskumas)
                        enhanced_im.show()

                        teisingas = input("Ar pasirinkimai tinka? T - Taip, N - Ne\n")

                        if teisingas == "T":
                            if pasirink_ == "":
                                enhanced_im.save("dog.jpg")
                            else:
                                pasirink_ = check_file_exists(pasirink_)[0]
                                enhanced_im.save(pasirink_)

                            continue

                        elif teisingas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    elif langas == "4":

                        im = check_file_exists(pasirink_)[1]
                        im1 = im.filter(ImageFilter.BLUR)

                        im1.show()

                        teisingas = input("Ar pasirinkimai tinka? T - Taip, N - Ne\n")

                        if teisingas == "T":
                            if pasirink_ == "":
                                im1.save("dog.jpg")
                            else:
                                pasirink_ = check_file_exists(pasirink_)[0]
                                im1.save(pasirink_)

                            continue

                        elif teisingas == "N":
                            continue
                        else:
                            print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                            continue

                    elif langas == "5":

                        metodas = input("Kokio metodo noretumete?\n"
                                        "r - FLIP_LEFT_RIGHT\nb - FLIP_TOP_BOTTOM\n"
                                        "90 - ROTATE_90\n180 - ROTATE_180\n270 - ROTATE_270\nt - TRANSPOSE\n")

                        if metodas not in ["r", "b", "90", "180", "270", "t"]:
                            print("Neteisingas pasirinkimas. Perskaitykite instrukcija.")
                            continue
                        else:

                            im = check_file_exists(pasirink_)[1]
                            im1 = transpose(im, metodas)

                            im1.show()

                            teisingas = input("Ar pasirinkimai tinka? T - Taip, N - Ne\n")

                            if teisingas == "T":
                                if pasirink_ == "":
                                    im1.save("dog.jpg")
                                else:
                                    pasirink_ = check_file_exists(pasirink_)[0]
                                    im1.save(pasirink_)

                                continue

                            elif teisingas == "N":
                                continue
                            else:
                                print("Neteisingi pasirinkimai. Galimi tik T - Taip, N - Ne")
                                continue

        elif pasirinkimas == "2":
            pasirink_ = int(input("---- Paveiksleliu nustatymai --- \n"
                                  " 1 - Ijungti paveikslelius \n 2 - Isjungti (nenaudoti)\n"))

            if pasirink_ == 1:
                ijungimas = 1

                with open("stats.pkl", "wb") as failas:
                    pickle.dump(ijungimas, failas)

                print("[IJUNGTA] Paveiksleliu pridejimas ijungtas.")

            elif pasirink_ == 2:
                ijungimas = 0

                with open("stats.pkl", "wb") as failas:
                    pickle.dump(ijungimas, failas)

                print("[ISJUNGTA] Paveiksleliu pridejimas isjungtas.")

        elif pasirinkimas == "3":
            df = pd.read_sql("SELECT * FROM emails", engine)
            sns.countplot(x='lytis', data=df)

            plt.show()
            continue

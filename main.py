import dotenv
import os

dotenv.load_dotenv()

import time
import json

from playwright.sync_api import sync_playwright

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap
import random

PASSWORD = os.getenv("PASSWORD")
ID = os.getenv("ID")


def get_raw_html():
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=False)
        if os.path.exists("storage.json"):
            ctx = browser.new_context(storage_state="storage.json")
        else:
            ctx = browser.new_context()
            ctx.storage_state(path="storage.json")

        page = ctx.new_page()
        page.goto("https://lycee-champollion.prepas-plus.fr/colles/mes_notes")

        time.sleep(1)

        if page.url != "https://lycee-champollion.prepas-plus.fr/colles/mes_notes":
            page.goto("https://lycee-champollion.prepas-plus.fr/connexion")

            page.wait_for_selector('input[id="id_username"]').type(ID)
            page.wait_for_selector('input[id="id_password"]').type(PASSWORD)

            page.wait_for_selector('input[type="submit"]').click()

            page.context.storage_state(path="storage.json")

            page.goto("https://lycee-champollion.prepas-plus.fr/colles/mes_notes")

        # content =  page.wait_for_selector("table").inner_html()
        table = page.wait_for_selector("table")
        rows = table.query_selector_all("tr")[1:]
        notes = []
        for row in rows:
            cells = row.query_selector_all("td")
            for cell in cells:
                span = cell.query_selector("span")
                if not span:
                    continue
                grade = span.text_content()
                attrs = span.get_attribute("title")

                note = {
                    "semaine": row.query_selector("th").text_content(),
                    "grade": grade,
                    "attrs": attrs,
                    "col_index": cells.index(cell),
                }
                notes.append(note)

        print(notes)
        with open("notes.json", "w") as f:
            json.dump(notes, f)

        browser.close()

        # return content


COLORS = ["#aaaa40", "#50e0ff", "#5050ff", "#20ee20"]
SUBJECTS = ["anglais", "info", "maths", "physique"]


def handle_data():
    with open("notes.json", "r") as f:
        notes = json.load(f)

    for note_data in notes:
        note = float(note_data["grade"].replace(",", "."))
        attrs = note_data["attrs"]
        attrs = attrs.split(";")
        semaine = note_data["semaine"].split(":")[0]
        [colleur, rg, moy, et] = attrs
        moy = float(moy.split(":")[1].replace(",", "."))
        et = float(et.split(":")[1].replace(",", "."))

        # Générer une série de valeurs de x autour de la moyenne
        x = np.linspace(moy - 4 * et, moy + 4 * et, 1000)

        # Calculer la fonction de densité de la distribution normale
        y = (1 / (et * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - moy) / et) ** 2)

        # Tracer le graphique
        color = colors.TABLEAU_COLORS[random.choice(list(colors.TABLEAU_COLORS.keys()))]
        plt.cla()
        plt.plot(x, y, label=f"Moy {moy}", color=color)
        plt.xlim([0, 20])
        plt.axvline(note, color=color, linestyle="--", label=f"Note {note}")
        plt.title(note_data["semaine"] + " - " + colleur + "\n" + rg)
        plt.xlabel("Valeurs")
        plt.ylabel("Densité de probabilité")
        plt.legend()

        # Size
        plt.gcf().set_size_inches(12, 8)
        plt.tight_layout()
        # DPI
        # plt.savefig(f"figures/{SUBJECTS[note_data['col_index']]}-{semaine}-{colleur}.png", dpi=300)

    plt.cla()

    curves = {}
    for sub in SUBJECTS:
        curves[sub] = {
            "y0": [],
            "y1": [],
            "et": [],
            "yc": [],
            "ym": [],
            "semaines": [],
            "rank": [],
        }
    for note_data in notes:
        note = float(note_data["grade"].replace(",", "."))
        attrs = note_data["attrs"]
        attrs = attrs.split(";")
        semaine = note_data["semaine"].split(":")[0]
        [colleur, rg, moy, et] = attrs
        moy = float(moy.split(":")[1].replace(",", "."))
        et = float(et.split(":")[1].replace(",", "."))

        # rg_self = int(rg.split("/")[0].split(":")[1])
        # rg_max = int(rg.split("/")[1])

        curves[SUBJECTS[note_data["col_index"]]]["y0"].append(moy - et)
        curves[SUBJECTS[note_data["col_index"]]]["y1"].append(moy + et)

        curves[SUBJECTS[note_data["col_index"]]]["et"].append(et)
        curves[SUBJECTS[note_data["col_index"]]]["yc"].append(moy)
        curves[SUBJECTS[note_data["col_index"]]]["ym"].append(note)
        curves[SUBJECTS[note_data["col_index"]]]["rank"].append(rg.split(":")[1])
        curves[SUBJECTS[note_data["col_index"]]]["semaines"].append(
            int(semaine.removeprefix("S"))
        )

    # print(json.dumps(curves, indent=4))

    for sub in SUBJECTS:
        curves[sub] = {
            "y0": np.array(curves[sub]["y0"]),
            "y1": np.array(curves[sub]["y1"]),
            "et": np.array(curves[sub]["et"]),
            "yc": np.array(curves[sub]["yc"]),
            "ym": np.array(curves[sub]["ym"]),
            "rank": np.array(curves[sub]["rank"]),
            "semaines": np.array(curves[sub]["semaines"]),
        }
    plt.cla()

    def plot_subject(plot, sub, j):
        color = COLORS[j % len(COLORS)]
        # color = colors.TABLEAU_COLORS[random.choice(list(colors.TABLEAU_COLORS.keys()))]

        for i in np.linspace(0, 1, 20):
            plt.fill_between(
                curves[sub]["semaines"],
                curves[sub]["yc"] - curves[sub]["et"] * i,
                curves[sub]["yc"] + curves[sub]["et"] * i,
                color=color,
                alpha=0.006,
            )
        plt.plot(
            curves[sub]["semaines"],
            curves[sub]["yc"],
            alpha=0.2,
            color=color,
        )

        plt.fill_between(
            curves[sub]["semaines"],
            curves[sub]["y0"],
            curves[sub]["y1"],
            color=color,
            alpha=0.1,
            interpolate=True,
        )

        # Rank labels
        for i, r in enumerate(curves[sub]["rank"]):
            plt.text(
                curves[sub]["semaines"][i],
                curves[sub]["ym"][i] + 0.5,
                r,
                horizontalalignment="center",
                verticalalignment="center",
                color=color,
                fontsize=8,
            )

        plt.plot(
            curves[sub]["semaines"],
            curves[sub]["ym"],
            color=color,
            label=f"{sub}",
            marker="o",
            markersize=5,
        )

        plt.grid(True, alpha=0.2, linestyle="--")

        plt.xticks(curves[sub]["semaines"])
        plt.tick_params(labelright=True, right=True, top=True)
        plt.yticks(np.linspace(0, 20, 21))
        plt.xlabel("Semaines")
        plt.ylabel("Notes")
        plt.ylim([0, 20])
        plt.gcf().set_size_inches(12, 8)

        plt.legend()

    sum = 0
    class_sum = 0
    cnt = 0
    old_cnt = -1
    biggest = 0
    i = 0

    global_weeks = []
    my_global_average = []
    class_global_average = []
    while True:  # Parcours par semaine
        # print(i, biggest)

        for j, sub in enumerate(SUBJECTS):  # Pour chaque matière
            if biggest < curves[sub]["semaines"][-1]:
                biggest = curves[sub]["semaines"][-1]
            for k, semaine in enumerate(
                curves[sub]["semaines"]
            ):  # trouver la semaine correspondante
                if i == semaine:
                    print(i)
                    sum += curves[sub]["ym"][k]
                    class_sum += curves[sub]["yc"][k]
                    cnt += 1
                    break

        if old_cnt == cnt and i > biggest:
            # Fin des semaines atteinte
            break

        old_cnt = cnt
        if cnt > 0:
            global_weeks.append(i)
            my_global_average.append(sum / cnt)
            class_global_average.append(class_sum / cnt)
        i += 1

    print(global_weeks)
    print(my_global_average)
            # print(sum / cnt)
    plt.figure(0)
    plt.plot(
        global_weeks, my_global_average, marker="o", markersize=5, label="Moyenne"
    )
    plt.plot(
        global_weeks, class_global_average, marker="o", markersize=5, label="Classe"
    )
    plt.grid(True, alpha=0.2, linestyle="--")

    plt.xticks(global_weeks)
    plt.tick_params(labelright=True, right=True, top=True)
    plt.yticks(np.linspace(0, 20, 21))
    plt.xlabel("Semaines")
    plt.ylabel("Notes")
    plt.ylim([0, 20])
    plt.gcf().set_size_inches(12, 8)
    plt.title("Progression de la moyenne générale")

    for j, sub in enumerate(SUBJECTS):
        plt.figure(1)
        plot_subject(plt, sub, j)
        plt.title("Tous confondus")

        plt.figure(0)
        plt.plot(
            curves[sub]["semaines"] + 0.04 + 0.04 * j,
            curves[sub]["ym"],
            color=COLORS[j % len(COLORS)],
            # yerr=curves[sub]["et"],
            alpha=0.5,
            marker="x",
            markersize=5,
            linestyle="",
            label=sub,
        )
        plt.errorbar(
            curves[sub]["semaines"] + 0.04 + 0.04 * j,
            curves[sub]["yc"],
            yerr=curves[sub]["et"],
            capsize=4,
            # ls="none",
            elinewidth=1,
            color=COLORS[j % len(COLORS)],
            # yerr=curves[sub]["et"],
            alpha=0.4,
            marker="",
            markersize=0,
            linestyle="",
        )
        plt.legend()

        plt.figure(j + 2)
        plt.title(sub)
        plot_subject(plt, sub, j)

    # plt.show()
    pdf = PdfPages("out.pdf")
    for n in plt.get_fignums():
        plt.figure(n).savefig(pdf, format="pdf")
    pdf.close()

get_raw_html()
handle_data()

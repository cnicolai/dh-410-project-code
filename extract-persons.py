import argparse
import os

from funcy import keep, mapcat, count_by
import pandas as pd
import spacy


def get_corpus(path):
    return [
        open(os.path.join(path, f)).read()
        for f in sorted(os.listdir(path))
        if f.endswith(".txt")
    ]


def get_ents(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return doc.ents


def get_person_name(ent):
    if ent.label_ == "PERSON":
        return ent.text
    else:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        default="/Users/christoph/Library/Mobile Documents/com~apple~CloudDocs/Action/Aubrey Maturin/Chapter/",
    )
    args = parser.parse_args()

    # if persons.json exists, use it
    if os.path.exists("persons.json"):
        df = pd.read_json("persons.json")
    else:
        corpus = get_corpus(args.path)
        ents = mapcat(get_ents, corpus)

        persons = keep(get_person_name, ents)

        df = pd.DataFrame(
            dict(count_by(lambda x: x, persons)).items(), columns=["name", "count"]
        )
        df = df.sort_values(by="count", ascending=False).reset_index(drop=True)

    # filter out persons that appear less than 10 times in the corpus
    df = df[df["count"] >= 10]
    print(df.to_string())

    # save to json if file does not exist
    if not os.path.exists("persons.json"):
        df.to_json("persons.json", orient="records")

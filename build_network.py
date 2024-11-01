import argparse
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from tqdm import tqdm
import itertools as it
import funcy as fy
import re
import networkx as nx
import matplotlib.pyplot as plt
from math import log


def get_corpus(path):
    with open(path, "r") as file:
        file_contents = file.read()

    return file_contents


def clean_text(xml_text, filter_stopwords=True):
    soup = BeautifulSoup(xml_text, "xml")

    # Get the text tag content
    text_content = soup.find("text")
    if not text_content:
        raise ValueError("No text tag found in the XML")
    text_content = BeautifulSoup(str(text_content), "xml")

    # Remove all tags except persName
    for tag in tqdm(text_content.find_all(), desc="Cleaning tags"):
        if tag.name != "persName":
            tag.unwrap()

    text_with_persons = text_content.prettify().split("\n", 1)[1].strip()

    if filter_stopwords:
        # Remove stopwords
        stop_words = set(stopwords.words("english"))
        punctuation = set([".", ",", ":", ";", "!", "?", "(", ")", "[", "]", "{", "}"])
        text_with_persons = " ".join(
            [
                word
                for word in tqdm(text_with_persons.split(), desc="Filtering stopwords")
                if word.lower() not in fy.merge(stop_words, punctuation)
            ]
        )

    return str(text_with_persons)


def get_text_windows(text, window_size):
    words = text.split()

    if window_size <= 0:
        raise ValueError("Window size must be positive")
    if not words:
        return
    if window_size > len(words):
        yield words
        return

    for i in range(0, len(words) - window_size + 1):
        yield words[i : i + window_size]


def get_person_refs(window):
    """Count complete person references in text window."""
    # Ensure window is a string
    if isinstance(window, list):
        window = " ".join(window)

    # Find complete persName tags
    pattern = r'<persName\s+ref="([^"]+)"[^>]*>([^<]+)</persName>'
    matches = re.finditer(pattern, window)

    refs = {match.group(1) for match in matches}

    return refs


def visualize_network(G, title="Character Co-occurrence Network"):
    # Create the spring layout
    pos = nx.spring_layout(G, k=5, iterations=100)

    # Create a new figure with a large size
    plt.figure(figsize=(20, 13))

    # Draw the network
    nx.draw_networkx_nodes(G, pos, node_size=100, node_color="lightblue")
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)

    # Add edge labels (weights) with rounded values
    edge_labels = {(u, v): f'{d["weight"]:.2f}' for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def number_of_windows(cleaned_text, window_size):
    words = cleaned_text.split()
    if window_size <= 0:
        raise ValueError("Window size must be positive")
    if not words:
        return 0
    if window_size > len(words):
        return 1
    return len(words) - window_size + 1


def export_to_gephi(G, output_path="network.gexf"):
    nx.write_gexf(G, output_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Process XML corpus and build character network."
    )
    parser.add_argument(
        "--path",
        default="/Users/christoph/Library/Mobile Documents/com~apple~CloudDocs/Action/Aubrey Maturin/aubrey-maturin.xml",
        help="Path to the XML corpus file",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Get the XML text
    xml_text = get_corpus(args.path)

    # Clean the text
    cleaned_text = clean_text(xml_text, filter_stopwords=True)

    # Get windows of text
    windows = get_text_windows(cleaned_text, window_size=200)

    # Create an empty graph
    G = nx.Graph()

    # Iterate over windows and update the graph
    for window in tqdm(
        windows,
        desc="Processing windows",
        total=number_of_windows(cleaned_text, window_size=10),
    ):
        persons_in_window = get_person_refs(window)

        # Get all unique pairs of persons in the window
        for person1, person2 in it.combinations(persons_in_window, 2):
            if G.has_edge(person1, person2):
                # Increment weight of existing edge
                G[person1][person2]["weight"] += 1
            else:
                # Create new edge with weight 1
                G.add_edge(person1, person2, weight=1)

    # Dampen the weights
    for node1, node2, data in tqdm(
        G.edges(data=True), desc="Dampening weights", total=G.number_of_edges()
    ):
        data["weight"] = log(1 + 0.5 * data["weight"])

    # Export to Gephi
    export_to_gephi(G)

    # Visualize the network
    visualize_network(G)

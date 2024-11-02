import pytest
from build_network import (
    get_corpus,
    clean_text,
    get_text_windows,
    build_network_from_windows,
)


@pytest.fixture
def cleaned_text():
    xml_text = get_corpus("test_corpus.xml")
    return clean_text(xml_text, filter_stopwords=True)


@pytest.mark.parametrize("window_size", [1, 2, 3, 4])
def test_too_small_window(cleaned_text, window_size):
    windows = get_text_windows(cleaned_text, window_size=window_size)
    G = build_network_from_windows(windows, cleaned_text, window_size)

    assert G.number_of_nodes() == 0, "Graph should have no nodes with small window"
    assert G.number_of_edges() == 0, "Graph should have no edges with small window"


@pytest.mark.parametrize("window_size", [5, 6, 7, 8, 9])
def test_medium_window(cleaned_text, window_size):
    windows = get_text_windows(cleaned_text, window_size=window_size)
    G = build_network_from_windows(windows, cleaned_text, window_size)

    assert G.number_of_nodes() > 0, "Graph should have nodes with medium window"
    assert G.number_of_edges() == 0, "Graph should have no edges with medium window"


@pytest.mark.parametrize("window_size", range(1, 109))
def test_monotonic_network_growth(cleaned_text, window_size):
    # Create graph with window_size
    windows1 = get_text_windows(cleaned_text, window_size=window_size)
    G1 = build_network_from_windows(windows1, cleaned_text, window_size)

    # Create graph with window_size + 1
    windows2 = get_text_windows(cleaned_text, window_size=window_size + 1)
    G2 = build_network_from_windows(windows2, cleaned_text, window_size + 1)

    # Assert monotonic growth
    assert (
        G2.number_of_nodes() >= G1.number_of_nodes()
    ), f"Nodes should not decrease at window size {window_size}"
    assert (
        G2.number_of_edges() >= G1.number_of_edges()
    ), f"Edges should not decrease at window size {window_size}"


def test_full_text_window(cleaned_text):
    # Get window size from text length
    window_size = len(cleaned_text.split())
    window_size = 109

    windows = get_text_windows(cleaned_text, window_size=window_size)

    G = build_network_from_windows(windows, cleaned_text, window_size)

    assert (
        G.number_of_nodes() == 20
    ), "Graph should have all 20 nodes with full text window"
    edges_in_fully_connected_graph = 20 * 19 / 2
    assert (
        G.number_of_edges() == edges_in_fully_connected_graph
    ), "Graph should have all possible edges with full text window"

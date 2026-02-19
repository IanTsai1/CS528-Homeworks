'''
to test if my code works, I create temporary html files that I know for certian the page rank ranking
I use my pagerank and parse graph code from 'analyze_pagerank.py' and validate if the output from the file
returns the expected output from the temp html files I created

given that the temp html files are hard coded, I can find out the pagerank itself and then verify it

This is a e2e test on parse graph of html files and pagerank
'''
import os
import tempfile
import math

from analyze_pagerank import parse_graph, pagerank

def write_file(folder, name, body):
    with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
        f.write(body)

def test_parse_graph_and_degrees_and_pagerank():
    with tempfile.TemporaryDirectory() as d:
        # 0 links to 1 and 2; 1 links to 2; 2 links to 0
        write_file(d, "0.html", '<a href="1.html">x</a><a href="2.html">y</a>')
        write_file(d, "1.html", '<a href="2.html">x</a>')
        write_file(d, "2.html", '<a href="0.html">x</a>')

        nodes, out_links, in_links = parse_graph(d)

        assert set(nodes) == {0, 1, 2}
        assert out_links[0] == {1, 2}
        assert out_links[1] == {2}
        assert out_links[2] == {0}

        assert in_links[0] == {2}
        assert in_links[1] == {0}
        assert in_links[2] == {0, 1}

        pr, _ = pagerank(nodes, out_links, in_links)
        assert all(v >= 0.0 for v in pr.values())
        assert math.isclose(sum(pr.values()), 1.0, rel_tol=1e-6, abs_tol=1e-9)

        # 2 has more inbound than 1, so PR(2) > PR(1)
        assert pr[2] > pr[1]

if __name__ == "__main__":
    test_parse_graph_and_degrees_and_pagerank()
    print("Test passed")

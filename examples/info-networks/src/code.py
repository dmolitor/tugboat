import numpy as np
import pandas as pd
import plotnine as pn
import re
from tqdm import tqdm

# Classes/Functions -------------------------------------------------------

class Author:
    """Contains information about each author"""
    
    def __init__(self, name):
        self.name = name
        self.degree = 0
        self.coauthors = set()
        self.papers = set()
        self.journals = set()
    
    def __repr__(self):
        return f"{self.name}; d = {self.degree}"
    
    def __str__(self):
        return f"{self.name}; d = {self.degree}"
    
    def append(self, paper: str, journal: str, authors: set, year: int):
        """Append author information"""
        coauthors = authors.difference(set([self.name]))
        if len(coauthors) > 0:
            for auth in coauthors:
                self.coauthors.add(auth)
        self.degree = len(self.coauthors)
        self.papers.add(paper)
        self.journals.add(journal)


class Network:
    """Coauthorship network structure"""
    
    def __init__(self):
        self.author_components = {}
        self.connected_components = {}
        self.n_authors = 0
        self.n_date_out_of_range = 0
        self.n_entries = 0
        self.n_malformed = 0
        self.authors = {}
    
    def __repr__(self):
        print_str = (
            f"No. Authors            : {self.n_authors}\n"
            + f"No. Total Entries      : {self.n_entries}\n"
            + f"No. Bad Entries        : {self.n_malformed}\n"
            + f"No. Outside Date Range : {self.n_date_out_of_range}"
        )
        return print_str
    
    def __str__(self):
        print_str = (
            f"No. Authors            : {self.n_authors}\n"
            + f"No. Total Entries      : {self.n_entries}\n"
            + f"No. Bad Entries        : {self.n_malformed}\n"
            + f"No. Outside Date Range : {self.n_date_out_of_range}"
        )
        return print_str
    
    def _traverse_author(self, author_name):
        """For a given author return their connected component as a set"""
        connections = set()
        node_stack = set([author_name])
        while len(node_stack) > 0:
            node = node_stack.pop()
            connections.add(node)
            for a in self.authors[node].coauthors:
                if a in connections:
                    continue
                node_stack.add(a)
        return connections
    
    def append(self, x):
        """Append coauthorship network entry"""
        self.n_entries += 1
        network_entry = parse_entry(x)
        if network_entry is None:
            self.n_malformed += 1
            return None
        if network_entry["year"] < 1985 or network_entry["year"] > 2005:
            self.n_date_out_of_range += 1
            return None
        for author_name in network_entry["authors"]:
            if author_name not in self.authors.keys():
                author = Author(author_name)
            else:
                author = self.authors[author_name]
            author.append(
                paper=network_entry["paper"],
                authors=network_entry["authors"],
                journal=network_entry["journal"],
                year=network_entry["year"]
            )
            self.set_author(author_name, author)
        self.n_authors = len(self.authors)
    
    def construct_connected_components(self, progress=False):
        """Calculate all connected components in the network"""
        cc = {}
        author_cc = {}
        if progress:
            author_iter = tqdm(self.authors.keys())
        else:
            author_iter = self.authors.keys()
        for author_name in author_iter:
            author_seen = [
                author_name in s 
                for s in cc.values()
            ]
            if sum(author_seen) > 0:
                [seen_index] = [i for i, x in enumerate(author_seen) if x]
                author_cc[author_name] = f"cc{seen_index}"
                continue
            author_component = self._traverse_author(author_name)
            cc_len = len(cc)
            cc[f"cc{cc_len}"] = author_component
            author_cc[author_name] = f"cc{cc_len}"
        self.author_components = author_cc
        self.connected_components = cc
    
    def set_author(self, name: str, author: Author):
        """Update entry for or add new author in network"""
        author_dict = {name: author}
        self.authors.update(author_dict)
    
    def tabulate_path_distance(self, author_name):
        """
        For any author tabulate the number of nodes that are exactly distance n
        away, for n in {0, max(distance away from author)}.
        """
        connection_names = set([author_name])
        connections = {0: set([author_name])}
        node_stack = [set([author_name])]
        dist_counter = 1
        while len(node_stack) > 0:
            node_set = node_stack.pop()
            layer_connections = set()
            for node in node_set:
                coauths = self.authors[node].coauthors
                for auth in coauths:
                    if not auth in connection_names:
                        layer_connections.add(auth)
                        connection_names.add(auth)
            if len(layer_connections) != 0:
                connections[dist_counter] = layer_connections
                node_stack.append(layer_connections)
            dist_counter += 1
        connections_tab = {k: len(v) for k, v in connections.items()}
        con_dist = []
        for k, v in connections_tab.items():
            con_dist.append([k] * v)
        con_dist = [x for y in con_dist for x in y]
        out = {
            "connections_raw": con_dist,
            "connections_tab": connections_tab,
            "connections": connections
        }
        return out


def format_num(x):
    """
    StackOverflow question
    https://stackoverflow.com/questions/38282697/how-can-i-remove-0-of-float-numbers
    """
    if x % 1 == 0:
        return int(x)
    else:
        return x

def parse_entry(x):
    """Parse coauthorship network entry"""
    author_info = x.split(",", 1)
    if (len(author_info) != 2):
        return None
    author_info, paper = author_info
    author_info = re.split(r"\s{2,}", author_info)
    paper = " ".join(paper.strip().lower().split())
    if (len(author_info) < 3 or len(author_info) > 4):
        return None
    try:
        year = int(author_info.pop(0).split(" ")[0])
    except ValueError:
        return None
    names = re.sub(r"\(.*\)", "", author_info.pop())
    names = set([name.strip().lower() for name in names.split("&")])
    journal = author_info.pop().lower()
    if author_info:
        vol_number = author_info.pop()
    else:
        vol_number = None
    entry = {
      "paper": paper,
      "year": year,
      "volume_no": vol_number,
      "journal": journal,
      "authors": names
    }
    return entry


# Import and structure data -----------------------------------------------

with open("data/ps1data.txt") as fp:
    network = [line.rstrip() for line in fp]

authorship_nw = Network()
for entry in range(0, len(network)):
    authorship_nw.append(network[entry])

# Prep hw1solution.txt
h1solution = ["djm484"]

## Problem 1

### (1a)

author_degrees = [author.degree for author in authorship_nw.authors.values()]
degree_tab = {
    degree: sum([value == degree for value in author_degrees]) for 
    degree in range(0, max(author_degrees) + 1)
}
for d, n in degree_tab.items():
    h1solution.append(f"@ 1 {d} {n}")

### (1b)

degree_tab_nz = {d: v for d, v in degree_tab.items() if v > 0 and d > 0}
deg_scatter = (pd
               .DataFrame(degree_tab_nz.items(), columns=["log(Degree)", "log(N)"])
               .apply(np.log, axis=1))
log_scatter = (pn.ggplot(deg_scatter, pn.aes(x="log(Degree)", y="log(N)"))
               + pn.geom_point()
               + pn.theme(
                     panel_background=pn.element_rect(fill="white"),
                     panel_grid=pn.element_line(color="#DEDEDE")
                 ))
log_scatter.save(
    filename="output/plot1.png",
    height=8,
    width=6,
    dpi=1000,
    verbose=False
)

## Problem 2

### (2a)

authorship_nw.construct_connected_components(progress=True)
biggest_cc = max([len(x) for x in authorship_nw.connected_components.values()])
total_nodes = authorship_nw.n_authors
cc_fraction = round(biggest_cc/total_nodes, 3)
h1solution.append(f"@ 2 {biggest_cc} {total_nodes} {cc_fraction}")

### (2b)

cstar = max([len(x) for x
             in authorship_nw.connected_components.values()
             if len(x) < biggest_cc])
cc_counts = {
    i: sum([
        len(x) == i for x
        in authorship_nw.connected_components.values()
    ])
    for i in range(1, cstar + 1)
}
for k, v in cc_counts.items():
    h1solution.append(f"@ 2 {k} {v}")

### (2c)

cc_tab_nz = {d: v for d, v in cc_counts.items() if v > 0 and d > 0}
cc_scatter = (pd
              .DataFrame(
                  cc_tab_nz.items(),
                  columns=["log(Connected Component Size)", "log(N)"]
              )
              .apply(np.log, axis=1))
log_cc_scatter = (
    pn.ggplot(
          data=cc_scatter,
          mapping=pn.aes(x="log(Connected Component Size)", y="log(N)")
      )
    + pn.geom_point()
    + pn.theme(
          panel_background=pn.element_rect(fill="white"),
          panel_grid=pn.element_line(color="#DEDEDE")
      )
)
log_cc_scatter.save(
    filename="output/plot2.png",
    height=8,
    width=6,
    dpi=1000,
    verbose=False
)

## Problem 3

### (3a)

hartmanis_dist = authorship_nw.tabulate_path_distance("hartmanis")
hartmanis_dist_tab = {
    k: v for k, v
    in hartmanis_dist["connections_tab"].items()
    if k > 0
}
for k, v in hartmanis_dist_tab.items():
    h1solution.append(f"@ 3 {k} {v}")

### (3b)

hartmanis_hist_dat = pd.DataFrame(
    [x for x in hartmanis_dist["connections_raw"] if x > 0],
    columns=["distance"]
)
hartmanis_hist = (pn.ggplot(hartmanis_hist_dat, pn.aes(x="distance"))
 + pn.geom_bar()
 + pn.theme(
       panel_background=pn.element_rect(fill="white"),
       panel_grid=pn.element_line(color="#DEDEDE"),
       panel_grid_minor=pn.element_blank()
   )
 + pn.labs(x="Distance from root node (Hartmanis)", y="Count")
 + pn.scale_x_continuous(breaks=list(range(1, 13)))
 + pn.scale_y_continuous(breaks=list(range(0, 12000, 1000))))
hartmanis_hist.save(
    filename="output/plot3.png",
    height=8,
    width=6,
    dpi=1000,
    verbose=False
)

## Problem 4

### (4a)

bf_tree = {}
for j in tqdm([x for x in hartmanis_dist["connections_tab"].keys() if x > 0]):
    j_prev = j - 1
    children = hartmanis_dist["connections"][j]
    parent_pool = hartmanis_dist["connections"][j_prev]
    potential_parents = []
    for child in children:
        coauthors = authorship_nw.authors[child].coauthors
        pot_par = [x for x in parent_pool if x in coauthors]
        potential_parents.append(len(pot_par))
    bf_tree[j] = round(np.mean(potential_parents), 3)
for k, v in bf_tree.items():
    h1solution.append(f"@ 4 {k} {format_num(v)}")

### (4b)

bf_tree_dat = pd.DataFrame(bf_tree.items(), columns=["distance", "avg_parent"])
bf_tree_hist = (pn.ggplot(bf_tree_dat, pn.aes(x="distance", y="avg_parent"))
 + pn.geom_bar(stat="identity")
 + pn.theme(
       panel_background=pn.element_rect(fill="white"),
       panel_grid=pn.element_line(color="#DEDEDE"),
       panel_grid_minor=pn.element_blank()
   )
 + pn.labs(
       x="Distance from root node (Hartmanis)",
       y="Average potential parents"
   )
 + pn.scale_x_continuous(breaks=list(range(1, 13)))
 + pn.scale_y_continuous(breaks=list([0, .5, 1, 1.5, 2, 2.5])))
bf_tree_hist.save(
    filename="output/plot4.png",
    height=8,
    width=6,
    dpi=1000,
    verbose=False
)

# Output hw1solution.txt
with open("output/hw1solution.txt", "w") as fp:
    fp.writelines([line + "\n" for line in h1solution])

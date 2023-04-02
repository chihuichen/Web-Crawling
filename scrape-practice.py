from collections import deque
import time
import pandas as pd
import string 
from urllib.parse import urlparse
import requests

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set and order list
        # 2. start recursive search by calling dfs_visit
        self.visited.clear()
        self.order.clear()
        self.dfs_visit(node)


    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return        
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        # 3. call self.visit_and_get_children(node) to get the children
        children = self.visit_and_get_children(node)
        self.order.append(node)
        # 4. in a loop, call dfs_visit on each of the children
        for k in children:
            self.dfs_visit(k)
            
    def bfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        queue = deque([node])
        while queue:
            nownode = queue.popleft()
            if nownode not in self.visited:
                self.visited.add(nownode)
                self.order.append(nownode)
                children = self.visit_and_get_children(nownode)
                for h in children:
                    if h not in self.visited:
                        queue.append(h)


df = pd.DataFrame([
    [0,1,0,1],
    [0,0,1,0],
    [0,0,0,1],
    [0,0,1,0],
], index=["A", "B", "C", "D"], columns=["A", "B", "C", "D"])
df


for node, has_edge in df.loc["B"].items():
    if has_edge:
        print(node)
        
        
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def visit_and_get_children(self, node):
        # TODO: Record the node value in self.order
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for t, edge in self.df.loc[node].items():
            if edge:
                children.append(t)
        return children

  
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        
    def visit_and_get_children(self, node):
        try:
            with open(f'file_nodes/{node}') as f:
                value = f.readline().strip()
                self.order.append(value)
                children = f.readline().strip().split(',')
                return children
        except FileNotFoundError:
            children = []
        return children
        
    def concat_order(self):
        return ''.join(filter(lambda c: c in string.ascii_letters, self.order))


class WebSearcher(GraphSearcher):
    
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.tables = []
    
    def visit_and_get_children(self, node):
        self.visited.add(node)
        self.driver.get(node)
        children = []
        for l in self.driver.find_elements_by_tag_name('a'):
            web = l.get_attribute('href')
            if web is not None:
                web_url = urlparse(web)
                if web_url.scheme in ('https') and web_url.netloc:
                    children.append(web)
        self.tables.append(pd.concat(pd.read_html(self.driver.page_source)))
        return children

    def table(self):
        return pd.concat(self.tables, ignore_index=True).dropna(axis=1)
    

def reveal_secrets(driver, url, travellog):
    driver.get(url)
    passcode = "".join(str(int(clue)) for clue in travellog["clue"].values)

    password_input = driver.find_element("id", "password")
    go_button = driver.find_element("id", "attempt-button")

    password_input.send_keys(passcode)
    go_button.click()
    time.sleep(5)

    checkbutton = driver.find_element("id", "locationBtn")
    checkbutton.click()

    time.sleep(5)
    
    img = driver.find_element("id", "image")

    img_url = img.get_attribute("src")

    download = requests.get(img_url)
    with open("Current_Location.jpg", "wb") as file:
        file.write(download.content)

    location = driver.find_element("id", "location")
    current_location = location.text
    
    return current_location






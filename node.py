class Node:
    def __init__(self, next=None, prev=None, vidID=None, fulltitle=None):
        self.next = next
        self.prev = prev
        self.vidID = vidID
        self.fulltitle = fulltitle
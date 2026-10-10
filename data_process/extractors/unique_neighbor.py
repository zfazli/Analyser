from collections import defaultdict

import pandas as pd

from extractors.base_extractor import BaseExtractor

from core.event_mapper import (
    READ_EVENTS,
    WRITE_EVENTS,
    MODIFY_EVENTS,
    CREATE_EVENTS,
    SEND_EVENTS,
    RECEIVE_EVENTS,
)



class UniqueNeighborExtractor(BaseExtractor):

    def __init__(self):

        super().__init__("unique_neighbor")

        self.neighbors = defaultdict(set)
        self.node_index = None

    ######################################################

    def update(self, edge, node_index):
        src = edge["src"]
        dst = edge["dst"]
        event = edge["event"]
        if (
            event in READ_EVENTS
            or event in WRITE_EVENTS
            or event in MODIFY_EVENTS
            or event in CREATE_EVENTS
            or event in SEND_EVENTS
            or event in RECEIVE_EVENTS
        ):

            self.neighbors[dst].add(src)
            self.neighbors[src].add(dst)
            self.node_index = node_index

    ######################################################

    def finalize(self):

        rows = []

        for uuid, nbrs in self.neighbors.items():
            subject = 0 
            file = 0 
            net = 0 
            principle = 0 
            unkown = 0 
            for x in nbrs :
                node_type  = self.node_index.get_type(x)

                if node_type == 'Subject':
                    subject +=1
                elif node_type  == 'FileObject':
                    file +=1
                elif node_type  == 'NetFlowObject':
                    net +=1

            rows.append({

                "uuid": uuid,


                "process_neighbor": subject,

                "file_neighbor": file,

                "socket_neighbor": net,

            })

        return pd.DataFrame(rows)
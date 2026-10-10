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


class OutDegreeExtractor(BaseExtractor):

    def __init__(self):

        super().__init__("out_degree")

        self.degree = defaultdict(set)

    ####################################################

    def update(self, edge):

        src = edge["src"]
        dst = edge["dst"]
        event = edge["event"]

        ################################################
        # Information leaves process
        ################################################

        if event in WRITE_EVENTS:
            self.degree[src].add(dst)

        elif event in SEND_EVENTS:
            self.degree[src].add(dst)

        ################################################
        # Information leaves file/socket
        ################################################

        elif event in READ_EVENTS:
            self.degree[dst].add(src)

        elif event in RECEIVE_EVENTS:
            self.degree[dst].add(src)

        ################################################
        # Metadata / object operations
        ################################################

        elif event in MODIFY_EVENTS :
            self.degree[src].add(dst)

        ################################################
        # Process → Process
        ################################################

        elif event in CREATE_EVENTS:
            self.degree[src].add(dst)

        else:
            return

    ####################################################

    def finalize(self):

        return pd.DataFrame([
            {
                "uuid": u,
                "out_degree": len(d)
            }
            for u, d in self.degree.items()
        ])
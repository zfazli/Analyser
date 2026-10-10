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


class InteractionExtractor(BaseExtractor):

    def __init__(self):

        super().__init__("interaction")

        self.node_index = None

        self.features = defaultdict(lambda: defaultdict(int))
        self.neighbors = defaultdict(set)

    #######################################################

    def update(self, edge, node_index):

        if self.node_index is None:
            self.node_index = node_index

        src = edge["src"]
        dst = edge["dst"]
        event = edge["event"]

        src_type = node_index.get_type(src)
        dst_type = node_index.get_type(dst)

        ###################################################
        # Process -> File
        ###################################################

        if src_type == "Subject" and dst_type == "FileObject":

            pf = self.features[src]
            ff = self.features[dst]

            if event in READ_EVENTS:

                pf["process_read_in"] += 1

            elif event in WRITE_EVENTS:

                pf["process_write_out"] += 1

            elif event in MODIFY_EVENTS:

                pf["process_modify"] += 1


            # elif event in EXECUTE_EVENTS:

            #     pf["process_excute"] += 1

            else:
                return
                # pf["process_other"] += 1
                # ff["file_other"] += 1

        ###################################################
        # Process -> Socket
        ###################################################

        elif src_type == "Subject" and dst_type == "NetFlowObject":

            pf = self.features[src]
            sf = self.features[dst]

            if event in SEND_EVENTS:

                pf["process_send_out"] += 1

            elif event in RECEIVE_EVENTS:

                pf["process_receive_in"] += 1

            else:
                return

        ###################################################
        # Process -> Process
        ###################################################
        elif src_type == "Subject" and dst_type == "Subject":

            sp = self.features[src]
            dp = self.features[dst]

            if event in CREATE_EVENTS:

             sp["process_spawn_out"] += 1
             dp["process_spawn_in"] += 1

            # elif event in EXECUTE_EVENTS:

            #     sp["process_execute"] += 1
            #     dp["process_executed"] += 1


            else:
                return


    #######################################################

    def finalize(self):

        rows = []

        for uuid, f in self.features.items():

            rows.append({

                "uuid": uuid,

                **f

            })

        return pd.DataFrame(rows).fillna(0)
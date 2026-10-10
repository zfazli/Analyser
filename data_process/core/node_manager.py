from pathlib import Path

import pandas as pd


class NodeManager:

    def __init__(self, node_dir):

        self.node_dir = Path(node_dir)

        self.nodes = {}
        self.node_type = {}


    ##########################################################

    def get_file_type(self , file):
        file = str(file)
        if "file" in file:
            return "FileObject"

        if "subject" in file:
            return "Subject"

        if "netflow" in file:
            return "NetFlowObject"

        if "principal" in file:
            return "Principal"
 
    def load(self):
        GT = set()

        print("Loading Nodes ...")

        files = sorted(self.node_dir.glob("*.parquet"))
        print(files)

        total = 0

        for file in files:


            df = pd.read_parquet(file)

            records = df.to_dict("records")
            file_type = self.get_file_type(file)

            for row in records:

                uuid = row["uuid"]
                self.nodes[uuid] = row
                self.node_type[uuid] = file_type

            total += len(records)

            print(f"{file.name:<30} {len(records):>10,}")

        print("------------------------------------------")

        print(f"Loaded Nodes : {total:,}")

    ##########################################################

    def get(self, uuid):

        return self.nodes.get(uuid)

    ##########################################################

    def exists(self, uuid):

        return uuid in self.nodes

    ##########################################################

    def get_type(self, uuid):

        if uuid in self.node_type:
            return self.node_type[uuid]
        else :
            return None
        
    def get_parent(self, uuid):

        if uuid in self.node_type:
            return self.nodes.get(uuid)['parent']
        else :
            return None


    ##########################################################

    def __len__(self):

        return len(self.nodes)
import os
import glob
import pandas as pd


class EdgeLoader:

    def __init__(self, edge_dir, max_files=None):

        self.files = sorted(
            glob.glob(
                os.path.join(edge_dir, "*.parquet")
            )
        )

        if max_files is not None:
            self.files = self.files[:max_files]

    #######################################################

    def __iter__(self):

        # dfs = [pd.read_parquet(f) for f in self.files]

        # df = pd.concat(dfs, ignore_index=True)
        # df = df.sort_values("time", kind="stable")   


        for file in self.files:

            print(file)

            df = pd.read_parquet(file)

            yield df.to_dict("records")
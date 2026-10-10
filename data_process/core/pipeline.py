import pandas as pd


class Pipeline:

    def __init__(

        self,

        loader,

        node_index,

        extractors

    ):

        self.loader = loader

        self.node_index = node_index

        self.extractors = extractors

    ######################################################

    def run(self):

        print("=" * 60)
        print("Start Feature Extraction")
        print("=" * 60)


        for edges in self.loader:

            for edge in edges:

                for extractor in self.extractors:

                    try:

                        extractor.update( edge, self.node_index)

                    except TypeError:

                        extractor.update(edge)

        ##################################################

        dfs = []

        for extractor in self.extractors:
            df = extractor.finalize()

            print(extractor.name)
            dfs.append(df)

        ##################################################

        result = dfs[0]



        for extractor, df in zip(self.extractors[1:], dfs[1:]):

            if df.empty:
                print(f"Skip {extractor.name} (empty)")
                continue

            if "uuid" not in df.columns:
                print(f"Skip {extractor.name} (no uuid)")
                continue

            result = result.merge(df,on="uuid",how="outer")

        for col in result.columns:

            if col == "uuid":
                continue

            if result[col].dtype == "object":

                result[col] = result[col].fillna("Unknown")

            else:

                result[col] = result[col].fillna(0)

        return result   
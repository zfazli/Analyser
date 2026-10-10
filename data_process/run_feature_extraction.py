from loaders.edge_loader import EdgeLoader
from core.node_manager import NodeManager
from core.pipeline import Pipeline

# Degree
from extractors.in_degree import InDegreeExtractor
from extractors.out_degree import OutDegreeExtractor

# Neighbor
from extractors.unique_neighbor import UniqueNeighborExtractor


# Interaction
from extractors.interaction import InteractionExtractor


# dataset = "theia-e5"
dataset = "trace-e5"

node_manager = NodeManager(
    f"./process_result/{dataset}/nodes"
)

node_manager.load()

loader = EdgeLoader(
    f"./process_result/{dataset}/edges",
    max_files= None
)

extractors = [

    InDegreeExtractor(),
    OutDegreeExtractor(),
    UniqueNeighborExtractor(),
    InteractionExtractor(),


]

pipeline = Pipeline(
    loader,
    node_manager,
    extractors
)

features = pipeline.run()

features["degree"] = (
    features["in_degree"] +
    features["out_degree"]
)

features["uuid"] = features["uuid"].astype(str)
features = features[features["uuid"] != "None"]
features = features[features["uuid"] != "0"]

features.to_parquet(
    f"./process_result/{dataset}/features.parquet"
)

print(features.head())
print(features.shape)
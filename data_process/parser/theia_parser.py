import json
from pathlib import Path

from tqdm import tqdm
import re

from storage.chunk_writer import ChunkWriter

from natsort import natsorted

UNKNOWN_UUID = "00000000-0000-0000-0000-000000000000"
class TheiaParser:

    def __init__(
            self,
            input_dir,
            output_dir,
            version="18",
            chunk_size=1_000_000,
            
    ):

        self.version = version

        self.input_dir = Path(input_dir)

        self.output_dir = Path(output_dir)

        self.seen_nodes = set()
        self.events= set()

        ########################################################

        self.subject_writer = ChunkWriter(
            self.output_dir / "nodes",
            "subject",
            chunk_size
        )

        self.file_writer = ChunkWriter(
            self.output_dir / "nodes",
            "file",
            chunk_size
        )

        self.netflow_writer = ChunkWriter(
            self.output_dir / "nodes",
            "netflow",
            chunk_size
        )



        self.edge_writer = ChunkWriter(
            self.output_dir / "edges",
            "edges",
            chunk_size
        )

    ###################################################################

    def parse_subject(self, obj):

        cmd = obj.get("cmdLine")
        if obj["uuid"] == UNKNOWN_UUID:
            return

        self.seen_nodes.add(obj["uuid"])

        self.subject_writer.write({

            "uuid": obj["uuid"],

            "host": obj.get("hostId"),

            "principal": obj.get("localPrincipal"),
            "cmdline": cmd["string"] if cmd else "",

            "start_time": obj.get("startTimestampNanos")
        })

    ###################################################################

    def parse_file(self, obj):

        prop = ((obj.get("baseObject") or {}).get("properties") or {}).get("map", {})
        self.seen_nodes.add(obj["uuid"])
        self.file_writer.write({

            "uuid": obj["uuid"],

            # "host": obj["baseObject"]["hostId"],

            "filename": prop.get("filename"),

            # "inode": prop.get("inode"),

            # "device": prop.get("dev")

        })

    ###################################################################

    def parse_netflow(self, obj):
        self.seen_nodes.add(obj["uuid"])
        self.netflow_writer.write({

            "uuid": obj["uuid"],

            # "host": obj["baseObject"]["hostId"],

            "local_ip": obj.get("localAddress"),

            "local_port": obj.get("localPort"),

            "remote_ip": obj.get("remoteAddress"),

            "remote_port": obj.get("remotePort")

        })

    ###################################################################


    def parse_event(self, obj):
    #   try:



        src = obj["subject"].get(
            f"com.bbn.tc.schema.avro.cdm{self.version}.UUID"
        )
        if src not in self.seen_nodes:
            return

       

        t1 = obj.get("predicateObject")

        if t1:

            dst = t1.get(
                f"com.bbn.tc.schema.avro.cdm{self.version}.UUID"
            )

            if dst:

                if dst not in self.seen_nodes:
                    return

                self.edge_writer.write({

                    "src": src,

                    "dst": dst,

                    "event": obj.get("type"),

                    "time": obj.get("timestampNanos"),

                    "thread": obj.get("threadId", {}).get("int"),

                    "sequence": obj.get("sequence", {}).get("long"),

                    "size": (obj.get("size") or {}).get("long")
                })
                self.events.add(obj.get("type"))

        t2 = obj.get("predicateObject2")

        if t2:

            dst = t2.get(
                f"com.bbn.tc.schema.avro.cdm{self.version}.UUID"
            )

            if dst:
                if dst not in self.seen_nodes:
                    return

                self.edge_writer.write({

                    "src": src,

                    "dst": dst,

                    "event": obj.get("type"),

                    "time": obj.get("timestampNanos"),

                    "thread": obj.get("threadId", {}).get("int"),

                    "sequence": obj.get("sequence", {}).get("long"),

                    "size": (obj.get("size") or {}).get("long")
                })
    #   except:
    #       print(obj)

    ###################################################################


    def sort_key(self , path):
        name = path.name

        m = re.search(r"\.bin(?:\.(\d+))?\.json(?:\.1)?$", name)

        if m:
            number = int(m.group(1) or 0)   # فایل بدون شماره => 0
            second = 1 if name.endswith(".json.1") else 0
            return (number, second)

        return (10**9, 0)
    def parse(self):

        key = f"com.bbn.tc.schema.avro.cdm{self.version}"

        files = natsorted( list(self.input_dir.rglob("*.json")) + list(self.input_dir.rglob("*.json.*")))
        for file in files:

            print(file.name)

            with open(file, encoding="utf-8") as f:

                for line in tqdm(f):
                    line = line.rstrip(",\n")
                    data = json.loads(line)


                    datum = data.get("datum", {})

                    if f"{key}.Subject" in datum:

                        self.parse_subject(
                            datum[f"{key}.Subject"]
                        )

                    elif f"{key}.FileObject" in datum:

                        self.parse_file(
                            datum[f"{key}.FileObject"]
                        )

                    elif f"{key}.NetFlowObject" in datum:

                        self.parse_netflow(
                            datum[f"{key}.NetFlowObject"]
                        )


                    elif f"{key}.Event" in datum:

                        self.parse_event(
                            datum[f"{key}.Event"]
                        )

        self.subject_writer.close()

        self.file_writer.close()

        self.netflow_writer.close()

        self.edge_writer.close()

        print()

        print("Parsing Finished")

        print("---------------------------")

        print("Subjects  :", self.subject_writer.num_rows)

        print("Files     :", self.file_writer.num_rows)

        print("Netflows  :", self.netflow_writer.num_rows)

        print("Edges     :", self.edge_writer.num_rows)

        for x in self.events :
            print(x)


        print("\nFinished.\n")


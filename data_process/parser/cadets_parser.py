import json
from pathlib import Path

from tqdm import tqdm
import re

from storage.chunk_writer import ChunkWriter

from config.config import parse_data_list

from natsort import natsorted

UNKNOWN_UUID = "00000000-0000-0000-0000-000000000000"
class CadetsParser:

    def __init__(
            self,
            dataset,
            version="18",
            chunk_size=1_000_000,
            
    ):

        self.version = version
        self.seen_nodes = set()
        self.events= set()

        self.output_dir = Path(f'./process_result/{dataset}')

        self.dataset = dataset

        self.subject ={}

        self.object = {}

        self.nets = {}

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


        self.train_edge_writer = ChunkWriter(
            self.output_dir / "edges" /"train",
            "edges",
            chunk_size
        )

        self.val_edge_writer = ChunkWriter(
            self.output_dir / "edges" /"val",
            "edges",
            chunk_size
        )

        self.test_edge_writer = ChunkWriter(
            self.output_dir / "edges"/"test",
            "edges",
            chunk_size
        )

    ###################################################################

    def parse_subject(self, obj):


        prop = obj.get("properties", {}).get("map", {})

        cmd = obj.get("cmdLine")
        if obj["uuid"] == UNKNOWN_UUID:
            return

        self.seen_nodes.add(obj["uuid"])

        self.subject[obj["uuid"]] = {

            "uuid": obj["uuid"],

            "host": obj.get("hostId"),

            "principal": obj.get("localPrincipal"),

            "parent":(obj.get("parentSubject") or {}).get(
                 f"com.bbn.tc.schema.avro.cdm{self.version}.UUID"),

            "cmdline": cmd["string"] if cmd else "",

            "start_time": obj.get("startTimestampNanos")
        }

    ###################################################################

    def parse_file(self, obj):

        prop = obj.get("baseObject", {}).get("properties", {}).get("map", {})
        self.seen_nodes.add(obj["uuid"])
        self.object[obj["uuid"]] = {

            "uuid": obj["uuid"],

            "filename": prop.get("filename"),


        }

    ###################################################################

    def parse_netflow(self, obj):
        self.seen_nodes.add(obj["uuid"])
        self.nets[obj["uuid"]] = {

            "uuid": obj["uuid"],

            # "host": obj["baseObject"]["hostId"],

            "local_ip": obj.get("localAddress"),

            "local_port": obj.get("localPort"),

            "remote_ip": obj.get("remoteAddress"),

            "remote_port": obj.get("remotePort")

        }

   ###################################################################

    def parse_event(self, obj , my_edge_writer):
    #   try:
        if obj["subject"] is None :
            return

        src = obj["subject"].get(
            f"com.bbn.tc.schema.avro.cdm{self.version}.UUID"
        )
        if src not in self.seen_nodes:
            return

        cmdline = obj["properties"]["map"].get("exec" , '')
        self.subject[src]["cmdline"] = cmdline

        t1 = obj.get("predicateObject")

        if t1:

            dst = t1.get(
                f"com.bbn.tc.schema.avro.cdm{self.version}.UUID"
            )

            if dst:

                if dst not in self.seen_nodes:
                    return
                tmp = obj["predicateObjectPath"]
                if tmp is not None:
                    path =  obj["predicateObjectPath"]["string"]
                else :
                    path = ''

                # if dst in self.subject.keys() and self.subject[dst]["cmdline"] == '':
                #     self.subject[dst]["cmdline"] = path
                # if dst in self.object.keys() and self.object[dst]["filename"] == '':
                #     self.object[dst]["filename"] = path
                my_edge_writer.write({

                    "src": src,

                    "dst": dst,

                    "event": obj.get("type"),

                    "time": obj.get("timestampNanos"),

                    "thread": obj.get("threadId", {}).get("int"),

                    "sequence": obj.get("sequence", {}).get("long"),

                    "size": (obj.get("size") or {}).get("long")
                })
                self.events.add(obj.get("type"))

    #   except:
    #       print(obj)

    ###################################################################

    def parse_files(self , files , type):
        key = f"com.bbn.tc.schema.avro.cdm{self.version}"

        for file in files:
        
            print(file)

            with open(file, encoding="utf-8") as f:

                for line in tqdm(f):

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

                        if type == 'train' :
                            self.parse_event(
                            datum[f"{key}.Event"] , self.train_edge_writer
                        )
                        elif type == 'val' :
                            self.parse_event(
                            datum[f"{key}.Event"] , self.val_edge_writer
                        )
                        elif type == 'test' :
                            self.parse_event(
                            datum[f"{key}.Event"] , self.test_edge_writer
                        )
                        
    def parse(self):


        train , val , test = parse_data_list(self.dataset)

        self.parse_files(train , "train")
        self.parse_files(val , "val")
        self.parse_files(test , "test")

        for _ , value in self.subject.items():
            self.subject_writer.write(value)

        self.subject_writer.close()

        for _ , value in self.object.items():
            self.file_writer.write(value)

        for _ , value in self.nets.items():
                self.netflow_writer.write(value)

        self.file_writer.close()

        self.netflow_writer.close()

        self.train_edge_writer.close()

        self.val_edge_writer.close()

        self.test_edge_writer.close()

        print()

        print("Parsing Finished")

        print("---------------------------")

        print("Subjects  :", self.subject_writer.num_rows)

        print("Files     :", self.file_writer.num_rows)

        print("Netflows  :", self.netflow_writer.num_rows)

        print("Train Edges     :", self.train_edge_writer.num_rows)

        print("Val Edges     :", self.val_edge_writer.num_rows)
        
        print("Test Edges     :", self.test_edge_writer.num_rows)

        for x in self.events :
            print(x)


        print("\nFinished.\n")


import json
from pathlib import Path

from tqdm import tqdm
from natsort import natsorted


def parse(input_dir):
    dic = {}

    input_dir = Path(input_dir)

    files = natsorted(
        list(input_dir.rglob("*.json")) +
        list(input_dir.rglob("*.json.*"))
    )

    for file in files:

        print(file.name)

        with open(file, encoding="utf-8") as f:

            for line in tqdm(f):
                line = line.rstrip(",\n")

                if not line:
                    continue

                data = json.loads(line)

                datum = data.get("datum", {})

                # پیدا کردن نوع object
                for key, value in datum.items():

                    if key.endswith(".Subject"):
                        uuid = value["uuid"]
                        dic[uuid] = str(file)
                        break

                    elif key.endswith(".FileObject"):
                        uuid = value["uuid"]
                        dic[uuid] = str(file)
                        break

                    elif key.endswith(".NetFlowObject"):
                        uuid = value["uuid"]
                        dic[uuid] = str(file)
                        break

    with open("uuid3.json", "w", encoding="utf-8") as f:
        json.dump(dic, f, ensure_ascii=False, indent=2)

    print(f"\nFinished. {len(dic):,} UUIDs found.\n")


parse("F:/dataset/trace_e5_45-47")
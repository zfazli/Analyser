import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import RobustScaler
import hdbscan
from core.node_manager import NodeManager



feature_groups = {
"Topology":[
    "in_degree",
    "out_degree",
    "process_neighbor",
    "file_neighbor",
    "socket_neighbor",

],

"Communication":[
    "process_read_in",
    "process_write_out",
    "process_modify",
    "process_send_out",
    "process_receive_in",
    "process_spawn_out",
    "process_spawn_in",
]
}


NEIGHBOR_DOMINANCE_THRESHOLD = 0.90
COM_THRESHOLD = 0.90
COVERAGE = 0.80


def prepare_df (dataset, top_ten = True):
    df = pd.read_parquet(f"process_result/{dataset}/features.parquet")

    # print(df.shape)

    node_manager = NodeManager(
        f"process_result/{dataset}/nodes"
    )
    node_manager.load()
    def get_cmd(uuid):
        cmd = node_manager.get(uuid)['cmdline'].split(' ')[0].split('/')[-1]

        if cmd == '-bash':
            cmd = 'bash'
        if cmd == 'sshd:':
            cmd = 'sshd'
        if cmd.startswith('xfce4'):
            cmd = cmd.replace('xfce4-','')

        return cmd
    df = df[df["degree"] > 1].copy()
    df["node_type"] = df["uuid"].map(node_manager.get_type)
    df_process = df[df["node_type"]=="Subject"].copy()
    df_process["cmdline"] = df_process["uuid"].apply(get_cmd)


    df_process["topology_label"] = df.apply(    assign_topology_label,axis=1,)

    df_process["communication_label"] = (df.apply(assign_communication_label, axis=1))

 
    # print(len(df_process))

    
    cmd_counts = ( df_process["cmdline"].value_counts().sort_values(ascending=False))
    if top_ten :
        keep_cmds = cmd_counts[:10].index
    else : 
        # فراوانی تجمعی
        cum_ratio = cmd_counts.cumsum() / cmd_counts.sum()

        # cmdlineهایی که تا 99% داده را پوشش می‌دهند
        keep_cmds = cum_ratio[cum_ratio <= COVERAGE].index
        if len(keep_cmds) < len(cmd_counts):
            keep_cmds = cmd_counts.iloc[:len(keep_cmds)+1].index
    df_process["cmdline_clean"] = df_process["cmdline"].where(
    df_process["cmdline"].isin(keep_cmds),
    "Rare")
    df_process = df_process[df_process["cmdline_clean"]!= ''].copy()
    df_process = df_process[df_process["cmdline_clean"] != "Rare"].copy()
    # print(len(df_process))

    df_process["role"] = (
    df_process["topology_label"].astype(str) + "_" +
    df_process["communication_label"].astype(str) )
    role_counts = (df_process.groupby(["cmdline_clean", "role"]).size().rename("count").reset_index())
    role_counts["total"] = ( role_counts.groupby("cmdline_clean")["count"].transform("sum"))
    role_counts["pct"] = role_counts["count"] / role_counts["total"]
    role_counts_filtered = role_counts[role_counts["pct"] >= 0.10].copy()

    # اگر خود df_process را می‌خواهی فیلتر کنی:
    valid_pairs = role_counts_filtered[["cmdline_clean", "role"]]

    df_process_filtered = df_process.merge(
    valid_pairs,
    on=["cmdline_clean", "role"],
    how="inner")


    return df_process_filtered


def assign_topology_label(row ):

    in_degree = row["in_degree"]
    out_degree = row["out_degree"]

    total_degree = in_degree + out_degree

    process_neighbor = row["process_neighbor"]
    file_neighbor = row["file_neighbor"]
    socket_neighbor = row["socket_neighbor"]



    # --------------------------------------------------------
    # 4. Neighbor composition
    # --------------------------------------------------------

    total_neighbors = (
        process_neighbor +
        file_neighbor +
        socket_neighbor
    )

    if total_neighbors > 0:

        process_ratio = process_neighbor / total_neighbors
        file_ratio = file_neighbor / total_neighbors
        socket_ratio = socket_neighbor / total_neighbors

        max_ratio = max(
            process_ratio,
            file_ratio,
            socket_ratio
        )

        if max_ratio >= NEIGHBOR_DOMINANCE_THRESHOLD:

            if process_ratio == max_ratio:
                return "process_centric"

            elif file_ratio == max_ratio:
                return "file_centric"

            else:
                return "socket_centric"


    # --------------------------------------------------------
    # 5. Default
    # --------------------------------------------------------

    return "balanced_connector"


def assign_communication_label(row):

    read_in = row["process_read_in"]
    write_out = row["process_write_out"]

    send_out = row["process_send_out"]
    receive_in = row["process_receive_in"]
    spawner = row['process_spawn_out']
    modify = row["process_modify"]
    # print(f' {read_in}  {write_out}  {send_out}  {receive_in} {spawner}')

    total_io = (
        read_in +
        write_out +
        send_out +
        receive_in
    )
    # --------------------------------------------------------
    # 4. Mixed communication
    # --------------------------------------------------------
    if spawner > total_io  :
        return "spawner"
    if modify > total_io:
        return "modifier"
  

    # --------------------------------------------------------
    # 2. Read / Write dominated
    # --------------------------------------------------------

    rw_total = read_in + write_out
    sr_total = send_out + receive_in


    if rw_total > 0:
        read_ratio = read_in / total_io
        write_ratio = write_out / total_io

        # Read dominant
        if read_ratio >= COM_THRESHOLD :
            return "read_dominant"

        # Write dominant
        if write_ratio >= COM_THRESHOLD :
            return "write_dominant"

        # Read + Write
        if rw_total/ total_io >= COM_THRESHOLD:
            return "read_write"



    # --------------------------------------------------------
    # 3. Network / IPC communication
    # --------------------------------------------------------

    if sr_total > 0  :

        send_ratio = send_out / total_io
        receive_ratio = receive_in / total_io

        

        # ----------------------------------------------------
        # Send dominant
        # ----------------------------------------------------

        if send_ratio > COM_THRESHOLD:
            return "send_dominant"
        if receive_ratio > COM_THRESHOLD:
            return "receive_dominant"
        
        if  sr_total/total_io >= COM_THRESHOLD :
            return "bidirectional"


    if spawner > rw_total and spawner > sr_total :
        return "spawner"


    return "mixed_communication"

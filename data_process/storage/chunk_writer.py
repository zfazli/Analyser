from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq


class ChunkWriter:
    """
    Generic Parquet Chunk Writer

    Example
    -------
    writer = ChunkWriter(
        output_dir="./process_result/theia-e3/edges",
        prefix="edges",
        chunk_size=1_000_000
    )

    writer.write(record)

    writer.close()
    """

    def __init__(
        self,
        output_dir,
        prefix,
        chunk_size=1_000_000
    ):

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.prefix = prefix
        self.chunk_size = chunk_size

        self.rows = []

        self.chunk_id = 0

        self.total_rows = 0

    ####################################################################

    def write(self, row: dict):

        self.rows.append(row)
        self.total_rows += 1

        if len(self.rows) >= self.chunk_size:
            self.flush()

    ####################################################################

    def flush(self):

        if len(self.rows) == 0:
            return

        table = pa.Table.from_pylist(self.rows)

        filename = self.output_dir / f"{self.prefix}_{self.chunk_id:05d}.parquet"

        pq.write_table(
            table,
            filename,
            compression="snappy"
        )

        self.rows.clear()

        self.chunk_id += 1

    ####################################################################

    def close(self):

        self.flush()

    ####################################################################

    @property
    def num_chunks(self):

        return self.chunk_id

    @property
    def num_rows(self):

        return self.total_rows
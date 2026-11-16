from mpi4py import MPI
import pandas as pd
import argparse
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def parse_where(expr):
    for op in [">=", "<=", "==", "!=", ">", "<"]:
        if op in expr:
            col, val = expr.split(op)
            col = col.strip()
            val = val.strip()
            
            try:
                val_num = float(val)
                is_number = True
            except ValueError:
                val_num = val.strip('"').strip("'")
                is_number = False

            if op in [">", "<", ">=", "<="] and not is_number:
                raise ValueError(f"'{op}' negali būti naudojamas su tekstu.")

            return {"col": col, "op": op, "value": val_num if is_number else val_num}
    raise ValueError("Neteisinga WHERE sąlyga")

def apply_where(df, cond):
    c, o, v = cond["col"], cond["op"], cond["value"]
    if o == ">": return df[df[c] > v]
    if o == "<": return df[df[c] < v]
    if o == "==": return df[df[c] == v]
    if o == "!=": return df[df[c] != v]
    if o == ">=": return df[df[c] >= v]
    if o == "<=": return df[df[c] <= v]

if rank == 0:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--where", required=True)
    parser.add_argument("--group-by", required=True)
    parser.add_argument("--agg", required=True)
    args = parser.parse_args()

    query = {
        "where": parse_where(args.where),
        "group_by": [args.group_by],
        "agg": {args.agg.split("=")[0]: args.agg.split("=")[1]},
        "filename": args.input
    }

    start = time.time()

    comm.bcast(query, root=0)

    df_iter = pd.read_csv(query["filename"], chunksize=10000)

    workers = list(range(1, size))
    active = set(workers)
    results = []

    for w in workers:
        try:
            comm.send(next(df_iter), dest=w)
        except StopIteration:
            comm.send(None, dest=w)

    while active:
        msg = comm.recv(source=MPI.ANY_SOURCE)
        src = msg["rank"]
        data = msg["data"]

        if data is not None and not data.empty:
            results.append(data)

        try:
            comm.send(next(df_iter), dest=src)
        except StopIteration:
            comm.send(None, dest=src)
            active.remove(src)

    final_df = pd.concat(results)
    final_df = (
        final_df
        .groupby(query["group_by"])
        .agg(query["agg"])
        .reset_index()
    )

    print("\nGALUTINIS REZULTATAS:")
    print(final_df)
    print(f"\nVykdymo laikas: {time.time() - start:.4f}s")


else:
    query = comm.bcast(None, root=0)

    while True:
        chunk = comm.recv(source=0)
        if chunk is None:
            break

        chunk = apply_where(chunk, query["where"])
        if chunk.empty:
            comm.send({"rank": rank, "data": None}, dest=0)
            continue

        local = (
            chunk
            .groupby(query["group_by"])
            .agg(query["agg"])
            .reset_index()
        )

        comm.send({"rank": rank, "data": local}, dest=0)

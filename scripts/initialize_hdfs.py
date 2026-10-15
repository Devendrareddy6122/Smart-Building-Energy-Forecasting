from __future__ import annotations

from storage.hdfs_client import HDFSClient


def initialize_hdfs():
    client = HDFSClient(url="hdfs://localhost:9000", fallback_root="./data")
    ok = client.connect()
    print(f"HDFS available: {ok}")
    if ok:
        print("HDFS is configured and ready for storage operations.")
    else:
        print("HDFS is unavailable. Local storage fallback will be used.")


if __name__ == "__main__":
    initialize_hdfs()

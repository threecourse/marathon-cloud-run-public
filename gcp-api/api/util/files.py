import os
import tarfile
from typing import Callable


def compress(target_dir: str, out_path: str, filter: Callable[[str], bool] = None):
    """対象フォルダ内を圧縮してtar.gzに保存する"""

    # フォルダの作成
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # ファイルの追加
    archive = tarfile.open(out_path, mode="w:gz")
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            path = os.path.join(root, file)
            arc_name = os.path.relpath(os.path.join(root, file), target_dir)
            if filter is None or filter(arc_name):
                archive.add(path, arcname=arc_name)

    archive.close()


def extract(target_path: str, out_dir: str):
    """tar.gzを解凍する"""
    tar = tarfile.open(target_path)
    tar.extractall(path=out_dir)
    tar.close()

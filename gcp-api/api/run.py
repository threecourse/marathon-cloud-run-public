import asyncio
import functools
import os
import shutil
import tempfile
import time
from typing import List

import requests

from .env import Env
from .util import files, gcp


def upload_code(run_name: str, local_target_dir: str, lang: str) -> None:
    """対象フォルダ内を圧縮してGCSにアップロードする

    inputフォルダおよび.cppのみをアップロードするようにしている
    """
    tmpdir = tempfile.mkdtemp()
    local_tar_path = os.path.join(tmpdir, "codes.tar.gz")

    def filter(arc_name: str) -> bool:
        rel_dir = os.path.dirname(arc_name)
        if lang == "cpp":
            if rel_dir.startswith("input"):
                return True
            if rel_dir.startswith("work"):
                return False
            if rel_dir.startswith("cmake-build-debug"):
                return False
            if arc_name.endswith(".cpp"):
                return True
            return False
        else:
            raise Exception

    files.compress(local_target_dir, local_tar_path, filter)
    gcp.upload_blob(Env.bucket_name, local_tar_path, Env.blob_name(run_name))
    shutil.rmtree(tmpdir)


async def local_submit(run_name: str, name: str, cases: List[str], params, lang: str) -> dict:
    """ローカルのdocker上のサーバにhttpリクエストを投げる（デバッグ用）"""
    payload = {
        "run_name": f"{run_name}",
        "name": name,
        "cases": cases,
        "params": params,
        "lang": lang,
    }
    response = requests.post("http://localhost:8080/run", json=payload)
    if response.status_code != 200:
        raise Exception(f"response is invalid: {response}")
    response_data = response.json()
    return response_data


async def submit(run_name: str, name: str, cases: List[str], params: dict, token: str, lang: str) -> dict:
    """Cloud RunにタスクをSubmitする"""

    # サービスアカウントのトークンを生成する（warningをフィルタする）
    url = Env.cloud_run_url
    payload = {
        "run_name": f"{run_name}",
        "name": name,
        "cases": cases,
        "params": params,
        "lang": lang,
    }
    headers = {"Authorization": f"Bearer {token}"}

    # 非同期処理にする
    loop = asyncio.get_running_loop()
    source = functools.partial(requests.post, url, json=payload, headers=headers)

    # タイムアウト処理を設定する（1秒を5回まで待つという設定）
    timeout_count = 0
    wait_seconds = [1, 1, 1, 1, 1]
    while True:
        response = await loop.run_in_executor(None, source)
        if response.status_code == 200:
            break
        elif response.status_code == 429 or response.status_code == 500:
            if timeout_count >= len(wait_seconds):
                raise Exception(f"timeout: {response}")
            wait = wait_seconds[timeout_count]
            await loop.run_in_executor(None, time.sleep, wait)
            timeout_count += 1
        else:
            raise Exception(f"response is invalid: {response}")

    response_data = response.json()
    return response_data

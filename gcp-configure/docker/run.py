import json
import logging
import os
import subprocess
import tarfile
import traceback
from pathlib import Path
from typing import List

import google.cloud.logging
from env import Env
from google.cloud import storage
from google.cloud.logging.handlers import CloudLoggingHandler

logger = logging.getLogger("server.run")
logger.setLevel(logging.INFO)


def download_blob(bucket_name: str, source_blob_name: str, destination_file_name: str, project_id: str):
    # フォルダの作成
    os.makedirs(os.path.dirname(destination_file_name), exist_ok=True)

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)


def extract(target_path: str, out_dir: str):
    """tar.gzを解凍する"""
    tar = tarfile.open(target_path)
    tar.extractall(path=out_dir)
    tar.close()
    os.remove(target_path)


class Runner:
    @classmethod
    def run(cls, req_payload: dict) -> List[dict]:
        """
        パラメータを元にランの実行を行う

        Env.blob_name, Env.blob_name_run_infoにソースコードとパラメータが保存されているとする
        :param run_name: ラン名
        :param case_id: ケース番号
        :return: ランにより出力されるjsonをパースしたdict
        """

        assert "run_name" in req_payload
        assert "cases" in req_payload
        assert "name" in req_payload
        assert "params" in req_payload
        assert "lang" in req_payload
        run_name = req_payload["run_name"]
        name = req_payload["name"]
        cases = req_payload["cases"]
        params = req_payload["params"]
        lang = req_payload["lang"]

        # Cloud Loggingのセットアップ
        if len(logger.handlers) == 0:
            client = google.cloud.logging.Client()
            cloud_handler = CloudLoggingHandler(client)
            stream_handler = logging.StreamHandler()
            logger.addHandler(cloud_handler)
            logger.addHandler(stream_handler)

        try:
            # パスの設定
            local_tar_path = f"../work/code-{run_name}.tar.gz"
            local_extract_path = f"../code-{run_name}"

            # ダウンロード
            download_blob(Env.bucket_name, Env.blob_name(run_name), local_tar_path, Env.project_id)
            extract(local_tar_path, local_extract_path)

            # ランの実行
            work_dir = local_extract_path
            os.chdir(work_dir)

            logger.info("run started")
            results = []
            for case in cases:
                result = cls.run_case(name, case, params, lang)
                results.append(result)
            logger.info("run finished")

            return results

        except Exception:
            logger.info(f"run failed {traceback.format_exc()}")
            raise

    @classmethod
    def run_case(cls, name: str, case: str, params: dict, lang: str) -> dict:
        """バイナリを実行し、結果を返す"""

        # パラメータ
        args = []
        args += [f"--name {name}"]
        args += [f"--case {case}"]
        for key, value in params.items():
            args += [f"--{key} {value}"]

        # ディレクトリの作成
        Path("bin").mkdir(parents=True, exist_ok=True)
        Path("result").mkdir(parents=True, exist_ok=True)

        # ランの実行
        if lang == "cpp":
            cpp_file = "main.cpp"
            output_bin = "./bin/a.out"
            build_cmd = f"g++ -std=gnu++1y -O2 {cpp_file} -o {output_bin}"
            run_cmd = f"{output_bin} {' '.join(args)} < input/{case}.txt"
            subprocess.check_call(
                build_cmd,
                shell=True,
            )
            subprocess.check_call(
                run_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=True,
            )
        else:
            raise Exception(f"lang {lang} is not supported")

        # 結果の取得
        if lang == "cpp":
            curr_dir = "."
            result_path = os.path.join(curr_dir, f"result/report-{name}-{case}.json")
        else:
            raise Exception(f"lang {lang} is not supported")

        with open(result_path, "r") as f:
            result_data = json.load(f)

        return result_data

import logging
import subprocess
import warnings
from typing import List

import google.cloud.logging

from . import run
from .env import Env


class API:
    @classmethod
    def generate_run_name(cls):
        return Env.generate_run_name()

    @classmethod
    def initialize(cls):
        warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

        # Cloud Loggingのセットアップ
        client = google.cloud.logging.Client()
        client.setup_logging()

    @classmethod
    def upload_code(cls, run_name: str, local_target_dir: str, lang: str):
        logging.info(f"[{run_name}] UPLOAD CODE")
        run.upload_code(run_name, local_target_dir, lang)

    @classmethod
    async def local_submit(cls, run_name: str, name: str, cases: List[str], params: dict, lang: str) -> dict:
        # （デバッグ用）ローカルのサーバにランをsubmitする
        # 計算はlocalのdockerに行わせるが、GCSは使用する
        logging.info(f"[{run_name}] LOCAL SUBMIT - {name}, {cases}")
        response_data = await run.local_submit(run_name, name, cases, params, lang)
        return response_data

    @classmethod
    async def submit(cls, run_name: str, name: str, cases: List[str], params: dict, token: str, lang: str) -> dict:
        # Cloud Runにsubmitする
        logging.info(f"[{run_name}] SUBMIT - {name}, {cases}")
        response_data = await run.submit(run_name, name, cases, params, token, lang)
        return response_data

    @classmethod
    def get_token(cls) -> str:
        token = (
            subprocess.run(
                f"gcloud auth print-identity-token --impersonate-service-account={Env.cloud_run_invoker_email}"
                + " --verbosity=error",
                shell=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode("utf-8")
            .rstrip()
        )
        return token

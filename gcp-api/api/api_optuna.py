import asyncio
import re
import time
from multiprocessing import Pool
from typing import Callable, List, Tuple

import optuna
import pandas as pd

from .api import API


class OptunaRunner:
    RunServer = 1
    RunLocalServer = 2

    def __init__(
        self,
        cases: List[str],
        source_param: Callable[[optuna.Trial], dict],
        source_loss: Callable[[List[dict], optuna.Trial], float],
        run_resource=RunServer,
        lang: str = "cpp",
        trials: int = 100,
        concurrency: int = 10,
        batch_size=2,
        bin_dir=".",
        storage="sqlite:///work/example.db",
    ):

        self.cases = cases
        self.source_param = source_param
        self.source_loss = source_loss
        self.run_resource = run_resource
        self.trials = trials
        self.concurrency = concurrency
        self.batch_size = batch_size
        self.bin_dir = bin_dir
        self.storage = storage
        self.run_name = ""
        self.token = ""
        self.lang = lang

    def run(self) -> Tuple[pd.DataFrame, dict, pd.DataFrame]:
        """パラメータの最適化を行う"""

        start_time = time.time()
        # run_nameの作成
        if self.run_resource == self.RunServer or self.run_resource == self.RunLocalServer:
            API.initialize()
            self.run_name = API.generate_run_name()
            API.upload_code(self.run_name, self.bin_dir, self.lang)
        else:
            self.run_name = "local"

        # studyの作成
        try:
            optuna.delete_study(study_name=self.run_name, storage=self.storage)
        except Exception as ex:
            print(ex)
        study = optuna.create_study(study_name=self.run_name, storage=self.storage)

        # トークンのセット（有効期間は60分）
        self.token = API.get_token()

        # マルチスレッドでの実行
        with Pool(self.concurrency) as p:
            p.map(self._optimize, range(self.concurrency))

        # 集計
        df = study.trials_dataframe(attrs=("number", "value", "params", "state", "user_attrs", "duration"))
        df = df.rename(columns=lambda x: re.sub("user_attrs_", "", x))

        # user_attrs_cases_data_listへの対応
        df_data_list = df[["cases_data_list"]].copy()
        df = df.drop(columns=["cases_data_list"])

        end_time = time.time()
        print(f"elapsed: {end_time - start_time:.3f} sec")

        return df, study.best_params, df_data_list

    def _optimize(self, i_thread: int):
        """パラメータの最適化を行う（各スレッド）"""

        # 行うTrialの数を定める
        def calc_n_trials():
            # 切り上げ
            n = (self.trials + (self.concurrency - 1)) // self.concurrency
            # 端数調整
            if i_thread == self.concurrency - 1:
                n = self.trials - n * (self.concurrency - 1)
            return n

        n_trials = calc_n_trials()
        if n_trials == 0:
            return
        study = optuna.load_study(study_name=self.run_name, storage=self.storage)
        study.optimize(self._objective, n_trials=n_trials, n_jobs=1)

    def _objective(self, trial: optuna.Trial):
        # (name, case)がユニークとなるように設計された名前
        name = f"{self.run_name}_seq{trial.number}"

        # パラメータを作成する
        params = self.source_param(trial)

        # ランの実行
        data_list = self._run_cases(name, params)

        # データの集約
        loss = self.source_loss(data_list, trial)

        return loss

    def _run_cases(self, name: str, params: dict) -> List[dict]:

        # バッチに分ける
        def to_batch(cases: List[str]):
            batches = []
            batch = []
            for i, case in enumerate(cases):
                batch.append(case)
                if len(batch) >= self.batch_size or i == len(cases) - 1:
                    batches.append(batch)
                    batch = []
            return batches

        # 各ケースの実行を非同期で行う
        loop = asyncio.get_event_loop()
        coroutine_list = []

        batches = to_batch(self.cases)
        for batch in batches:
            cor = self._run_batch_cases_server(name, batch, params)
            coroutine_list.append(cor)
        data_list_stacked = loop.run_until_complete(asyncio.gather(*coroutine_list))
        data_list = []
        for data_list_stack in data_list_stacked:
            data_list += data_list_stack
        return data_list

    async def _run_batch_cases_server(self, name: str, batch: List[str], params: dict) -> List[dict]:
        """パラメータを指定し複数のケースの実行を行い、スコアのリストを返す

        複数のケースを実行するジョブをサーバに投げる
        """
        print(f"---run {name} {batch}")

        if self.run_resource == self.RunServer:
            response_data = await API.submit(self.run_name, name, batch, params, self.token, self.lang)
        elif self.run_resource == self.RunLocalServer:
            response_data = await API.local_submit(self.run_name, name, batch, params, self.lang)
        else:
            raise Exception("should not be here")

        if response_data["status"] != "OK":
            raise Exception(f"response is invalid: {response_data['exception']}")
        else:
            data_list = response_data["results"]
        return data_list

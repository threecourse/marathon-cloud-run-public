import argparse
import os
import sys
from pathlib import Path
from typing import List

import numpy as np
import optuna

api_directory = "../../gcp-api"
sys.path.append(api_directory)
from api.api_optuna import OptunaRunner  # noqa

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--local-debug", action="store_true")
    parser.add_argument("-t", "--trials", type=int, default=None)
    parser.add_argument("--concurrency", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--case-start", type=int, default=None)
    parser.add_argument("-c", "--case-count", type=int, default=None)
    args = parser.parse_args()

    # set parameters
    lang = "cpp"
    local_debug = args.local_debug
    case_start = args.case_start
    case_count = args.case_count
    concurrency = args.concurrency
    batch_size = args.batch_size
    trials = args.trials
    if trials is None:
        trials = 10  # 100
    if concurrency is None:
        concurrency = 2  # 10
    if batch_size is None:
        batch_size = 1
    if case_start is None:
        case_start = 0
    if case_count is None:
        case_count = 5

    if local_debug:
        run_resource = OptunaRunner.RunLocalServer
    else:
        run_resource = OptunaRunner.RunServer

    def gen_params(trial: optuna.Trial) -> dict:
        if trials == 1:
            return {}

        # パラメータの作成
        p = trial.suggest_uniform("p", 0.0, 10.0)
        params = {"p": p}
        return params

    def calc_loss(data_list: List[dict], trial: optuna.Trial) -> float:
        # データの集約
        scores = []
        counters = []
        for data in data_list:
            score = data["score"]
            counter = data["counter"]
            scores.append(score)
            counters.append(counter)

        # データの添加
        score_mean = np.mean(scores)
        counters_mean = np.mean(counters)
        counters_min = int(np.min(counters))
        cases_data_list = data_list

        trial.set_user_attr("score", score_mean)
        trial.set_user_attr("counter", counters_mean)
        trial.set_user_attr("counter_min", counters_min)

        # jsonに出力した情報をかき集める
        trial.set_user_attr("cases_data_list", cases_data_list)

        # ロスの計算
        loss = score_mean * (-1)
        return loss

    Path("work").mkdir(parents=True, exist_ok=True)
    cases = [f"case{c:04}" for c in range(case_start, case_start + case_count)]
    runner = OptunaRunner(
        cases,
        gen_params,
        calc_loss,
        trials=trials,
        run_resource=run_resource,
        concurrency=concurrency,
        batch_size=batch_size,
        lang=lang,
    )
    df, best_params, df_data_list = runner.run()

    print(df.sort_values("value"))
    print(best_params)

    df_path = os.path.join(runner.bin_dir, "df.txt")
    df_data_list_path = os.path.join(runner.bin_dir, "df_data_list.txt")
    df.to_csv(df_path, sep="\t", index=False)
    df_data_list.to_csv(df_data_list_path, sep="\t", index=False)

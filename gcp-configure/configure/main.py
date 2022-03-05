import argparse
import warnings

import configure
import google.cloud.logging

if __name__ == "__main__":

    # このフォルダのコードはローカルで実行するので、ユーザーアカウント権限で構わない
    warnings.filterwarnings("ignore", "Your application has authenticated using end user credentials")

    # Cloud Loggingのセットアップ
    client = google.cloud.logging.Client()
    client.setup_logging()

    # 引数の扱い
    parser = argparse.ArgumentParser()

    # configure
    parser.add_argument("--build-base", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--push", action="store_true")
    parser.add_argument("--deploy", action="store_true")
    parser.add_argument("--local-deploy", action="store_true")

    args, unknown_args = parser.parse_known_args()

    # configure ------------------------------
    if args.build_base:
        # ベースとなるdocker imageのビルド
        configure.docker_build_base()
    if args.build:
        # docker imageのビルド
        configure.docker_build()
    if args.push:
        # docker imageのGCRへのpush
        configure.docker_push()
    if args.deploy:
        # Cloud Runへのデプロイ
        configure.deploy()
    if args.local_deploy:
        # （デバッグ用）ローカルでCloud Runと同じようにサーバを立ち上げる
        configure.docker_run_server()

# マラソンマッチ用パラメータチューニングツール

## ディレクトリ構成

* `gcp-api` - Optunaによるパラメータチューニングを実行するためのAPI
* `gcp-configure` - dockerfileおよびdockerイメージに含めるファイル  
* `gcp-configure/configure` - GCPプロジェクトの構成用のコード
* `problems/sample` - サンプル問題

## requirements

* python 3.7
* poetry
* docker  
  see https://docs.docker.com/engine/install/
* Google Cloud SDK  
  see https://cloud.google.com/sdk/install?hl=ja
* g++ 7.5

## GCPプロジェクトの構成

* 試行錯誤して作成したため、以下のとおりで動かない可能性もあるので、適宜ご対応下さい
* 途中でAPIの許可などが必要になることがあるため、1行ごとに実行するほうが良いです
* GCPプロジェクトの構成を管理するには、Terraformを利用する方法もあります

### GCPプロジェクトの構成

以下のコマンドを実行することで、GCPプロジェクトが構成されます。
```
# pythonライブラリのインストール
poetry install

# 環境変数に情報を設定（.flaskenvはバージョン管理上に含める環境変数を設定するファイル）
source .flaskenv

# GCPプロジェクトの作成
gcloud projects create ${PROJECT_ID} 
gcloud config set project ${PROJECT_ID} 

# gcloudの権限設定
gcloud auth application-default login 

# GCPの請求先アカウントの設定
# (gcpコンソールから実行 - 「お支払い」からプロジェクトに請求先アカウントを設定）

# GCPのAPIの権限設定
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable iamcredentials.googleapis.com

# Cloud Storageの設定
gsutil mb -p ${PROJECT_ID} gs://${PROJECT_ID}/

# dockerイメージのビルド
inv gcp --build-base --build

# dockerイメージのプッシュ
inv gcp --push 

# Cloud Runへのデプロイ
inv gcp --deploy

# サービスアカウントからCloud Runを実行できるようにする
gcloud iam service-accounts create invoker-service-account --display-name "Invoker Service Account"
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
       --member=serviceAccount:invoker-service-account@${PROJECT_ID}.iam.gserviceaccount.com \
       --role=roles/run.invoker --platform=managed --region us-central1

# 自身のアカウントからサービス アカウントのトークンを作成できるようにする
# (GCPコンソールから実行 - 自身のアカウントのロールに「サービス アカウント トークン作成者」を追加)

# Cloud RunのURLの設定
# (ローカル - .flaskenvにCLOUD_RUN_ROOT_URLを記述する）

```

### ログの出力による課金の抑制について

* ログの出力による課金を抑制するため、いずれかを行う必要があります。
  * Dockerイメージ内からプログラムを起動するときに、標準出力・エラーを抑制する（このプロジェクトではこの方法で対応）
  * ログの取り込みで、resource.type="cloud_run_revision" severity=DEFAULT の除外設定を適用する

## Optunaによるパラメータチューニングの実行

以下のコマンドで、Cloud Run/Optunaでのパラメータチューニングを行います。
```
inv test-run-optimize
```

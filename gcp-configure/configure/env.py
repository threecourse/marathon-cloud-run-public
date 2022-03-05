from pathlib import Path

from dotenv import dotenv_values

flaskenv_path = Path(__file__).parent.parent.parent / ".flaskenv"
config = dotenv_values(flaskenv_path)


class Env:
    # 特に指定しない場合、パスは相対パスであることに注意
    project_id = config["PROJECT_ID"]
    docker_file_base = "docker/dockerfile-base"
    docker_file = "docker/dockerfile"
    image_base_name = "marathon-cloud-run-sample-docker-base"
    image_name = project_id
    gcr_path = f"gcr.io/{project_id}/{image_name}"
    zone = "us-central1-c"
    region = "us-central1"
    service_name = "marathon-judge"

import random
import string
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import dotenv_values

flaskenv_path = Path(__file__).parent.parent.parent / ".flaskenv"
config = dotenv_values(flaskenv_path)


class Env:
    project_id = config["PROJECT_ID"]
    bucket_name = project_id
    cloud_run_root_url = config["CLOUD_RUN_ROOT_URL"]
    cloud_run_url = f"{cloud_run_root_url}/run"
    cloud_run_invoker_email = f"invoker-service-account@{project_id}.iam.gserviceaccount.com"

    @classmethod
    def generate_run_name(cls):
        jst = timezone(timedelta(hours=+9), "jst")
        jst_datetime = datetime.now(jst)
        format_str = "%Y%m%d%H%M%S"
        date_str = jst_datetime.strftime(format_str)

        rand_chars = [random.choice(string.ascii_lowercase) for i in range(3)]
        rand_str = "".join(rand_chars)

        return f"gcp-{date_str}-{rand_str}"

    @classmethod
    def blob_name(cls, run_name):
        return f"code/{run_name}.tar.gz"

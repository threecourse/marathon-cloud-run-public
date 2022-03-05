import os


class Env:
    project_id = os.environ["PROJECT_ID"]
    bucket_name = project_id

    @classmethod
    def blob_name(cls, run_name):
        return f"code/{run_name}.tar.gz"

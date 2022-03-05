import subprocess
from pathlib import Path

from invoke import task

root_dir = Path(__file__).parent.absolute()
gcp_dir = root_dir / "gcp-configure"


@task(aliases=["pc"])
def pre_commit(c, target="tasks.py"):
    with c.cd(str(root_dir)):
        c.run(f"black {target}")
        c.run(f"isort {target}")
        c.run(f"flake8 {target}")
        # c.run(f"mypy {target}")


@task(aliases=["pc-all"])
def pre_commit_all(c):
    pre_commit(c, "tasks.py")
    pre_commit(c, "gcp-api")
    pre_commit(c, "gcp-configure")
    pre_commit(c, "problems")


# region configure-gcp


@task(aliases=["gcp"])
def gcp_configure(c, build_base=False, build=False, push=False, deploy=False, local_deploy=False):
    args = ""
    if build_base:
        args += " --build-base"
    if build:
        args += " --build"
    if push:
        args += " --push"
    if deploy:
        args += " --deploy"
    if local_deploy:
        args += " --local-deploy"
    cmd = f"python ./configure/main.py{args}"
    # print(cmd)
    subprocess.check_call(cmd, shell=True, cwd=gcp_dir)


@task(aliases=["gcp-bpd"])
def gcp_configure_build_push_deploy(c):
    gcp_configure(c, build=True, push=True, deploy=True)


@task(aliases=["gcp-bl"])
def gcp_configure_build_local_deploy(c):
    gcp_configure(c, build=True, local_deploy=True)


# endregion

# region test


@task()
def test_run(c):
    dir = root_dir / "problems/sample"
    subprocess.check_call("python run.py", cwd=dir, shell=True)


@task()
def test_run_optimize(c):
    dir = root_dir / "problems/sample"
    subprocess.check_call("python run_optimize.py", cwd=dir, shell=True)


# endregion

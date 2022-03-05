import subprocess
from pathlib import Path

if __name__ == "__main__":
    cpp_file = "main.cpp"
    output_bin = "bin/a.out"
    result_dir = "result"
    Path(output_bin).parent.mkdir(parents=True, exist_ok=True)
    Path(result_dir).mkdir(parents=True, exist_ok=True)
    build_cmd = f"g++ -std=gnu++1y -O2 {cpp_file} -o {output_bin}"
    name = "temp"
    case = "case0000"
    p = 2.0
    run_cmd = cmd = f"./{output_bin} --name {name} --p {p} --case {case} < ./input/case0000.txt"
    subprocess.check_call(build_cmd, shell=True)
    subprocess.check_call(run_cmd, shell=True)

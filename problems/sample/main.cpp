#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <map>
#include <vector>

using namespace std;

// declaration -------------------------

void parse_args(int argc, char *argv[]);

void solve();

void print_json(std::string filename, std::string name, std::string _case,
                double score, double timer, int counter);

class Timer {

public:
    std::chrono::system_clock::time_point start_time;

    void start() {
        start_time = std::chrono::system_clock::now();
    }

    double elapsed() {
        std::chrono::system_clock::time_point now = std::chrono::system_clock::now();
        double elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
        return elapsed;
    }

};

// program -------------------------

Timer timer;
std::map<std::string, std::string> arg_dict;
double score;
double _time;
int counter;
int answer;

double p;
double x;

int main(int argc, char *argv[]) {
    timer.start();

    // parse
    parse_args(argc, argv);
    string name = arg_dict["--name"];
    string _case = arg_dict["--case"];
    p = stod(arg_dict["--p"]);

    // input
    cin >> x;

    // solve
    solve();

    // report
    string report_file_name = "report-" + name + "-" + _case + ".json";
    print_json(report_file_name, name, _case, score, _time, counter);
    return 0;
}

void solve() {
    // 解の評価を行う関数を模したもの
    score = (x - p) * (x - p);

    // 時間計測の確認用
    int z = 13;
    int N = 1000000000;
    for (int i = 0; i < N; ++i) {
        z *= 17;
    }
    _time = timer.elapsed();
    counter = 0;
    answer = z;
    cerr << answer << endl;
}

void parse_args(int argc, char *argv[]) {
    vector<string> args(argv, argv + argc);
    for (int arg_index = 1; arg_index < args.size(); arg_index += 2) {
        arg_dict[args[arg_index]] = args[arg_index + 1];
    }
}

void print_json(std::string filename, std::string name, std::string _case,
                double score, double _time, int counter) {
    auto path = "result/" + filename;
    std::ofstream ofs(path);
    ofs << "{" << endl;
    ofs << "\"name\": \"" << name << "\"," << endl;
    ofs << "\"case\": \"" << _case << "\"," << endl;
    ofs << "\"score\": " << score << "," << endl;
    ofs << "\"timer\": " << _time << "," << endl;
    ofs << "\"counter\": " << counter << endl;
    ofs << "}" << endl;
}


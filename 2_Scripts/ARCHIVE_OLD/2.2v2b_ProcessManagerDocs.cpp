/*
==============================================================================
STEP 2.2v2b: Process Speaker Documents (C++)
==============================================================================
Filters speaker turns by dataset type and aggregates text per document.
Inputs:
    - temp_unified_info.jsonl (file_name -> company_name, start_date)
    - temp_speaker_YYYY.jsonl (speaker turns)
Outputs:
    - temp_output_YYYY_DATASET.jsonl (aggregated documents)
Usage:
    2.2v2b_ProcessManagerDocs.exe YEAR DATASET_TYPE
    DATASET_TYPE: manager_qa | manager_pres | analyst_qa | entire_call
==============================================================================
*/

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>

using namespace std;

// Global dataset type
string DATASET_TYPE = "";

// Simple JSON string extraction
string get_json_value(const string& json, const string& key) {
    // Look for "key":
    string search = "\"" + key + "\":";
    size_t pos = json.find(search);
    if (pos == string::npos) return "";

    pos += search.length();

    // Skip whitespace
    while (pos < json.length() && (json[pos] == ' ' || json[pos] == '\t')) pos++;

    // Check if value starts with quote
    if (pos >= json.length() || json[pos] != '"') return "";

    pos++; // Skip opening quote

    // Find closing quote
    size_t end = pos;
    while (end < json.length() && json[end] != '"') {
        if (json[end] == '\\') end++; // Skip escaped char
        end++;
    }

    if (end >= json.length()) return "";

    return json.substr(pos, end - pos);
}

// Simple JSON int extraction
int get_json_int(const string& json, const string& key) {
    string search = "\"" + key + "\":";
    size_t start = json.find(search);
    if (start == string::npos) return 0;

    start += search.length();
    string num;
    while (start < json.length() && (isdigit(json[start]) || json[start] == '-')) {
        num += json[start++];
    }

    return num.empty() ? 0 : stoi(num);
}

// Check if role contains keyword (case-insensitive)
bool has_keyword(string text, string keyword) {
    transform(text.begin(), text.end(), text.begin(), ::tolower);
    transform(keyword.begin(), keyword.end(), keyword.begin(), ::tolower);
    return text.find(keyword) != string::npos;
}

// Check if speaker is managerial
bool is_managerial(const string& role, const string& employer, const string& company) {
    // Exclusions
    if (has_keyword(role, "analyst") || has_keyword(role, "operator")) return false;

    // Employer match
    if (!employer.empty() && !company.empty()) {
        string emp_lower = employer, comp_lower = company;
        transform(emp_lower.begin(), emp_lower.end(), emp_lower.begin(), ::tolower);
        transform(comp_lower.begin(), comp_lower.end(), comp_lower.begin(), ::tolower);
        if (emp_lower == comp_lower) return true;
    }

    // Role keywords
    vector<string> keywords = {"president", "vp", "director", "ceo", "cfo", "coo", "officer",
                               "chief", "executive", "head", "chairman", "manager"};
    for (const auto& kw : keywords) {
        if (has_keyword(role, kw)) return true;
    }

    return false;
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cerr << "Usage: " << argv[0] << " YEAR DATASET_TYPE" << endl;
        return 1;
    }

    int year = stoi(argv[1]);
    DATASET_TYPE = argv[2];

    cout << "======================================" << endl;
    cout << "Processing: " << DATASET_TYPE << " (year " << year << ")" << endl;
    cout << "======================================" << endl;

    // Load unified info
    unordered_map<string, pair<string, string>> unified; // file_name -> (company_name, start_date)
    ifstream unified_file("temp_unified_info.jsonl");
    if (!unified_file.is_open()) {
        cerr << "ERROR: Could not open temp_unified_info.jsonl" << endl;
        return 1;
    }

    string line;
    while (getline(unified_file, line)) {
        if (line.empty()) continue;
        string fname = get_json_value(line, "file_name");
        string company = get_json_value(line, "company_name");
        string start_date = get_json_value(line, "start_date");
        if (!fname.empty()) {
            unified[fname] = make_pair(company, start_date);
        }
    }
    unified_file.close();
    cout << "Loaded " << unified.size() << " file_name -> company_name mappings" << endl;

    // Process speaker data
    string input_file = "temp_speaker_" + to_string(year) + ".jsonl";
    string output_file = "temp_output_" + to_string(year) + "_" + DATASET_TYPE + ".jsonl";

    ifstream infile(input_file);
    if (!infile.is_open()) {
        cerr << "ERROR: Could not open " << input_file << endl;
        return 1;
    }

    cout << "Processing speaker data..." << endl;

    // Aggregate text by file_name
    unordered_map<string, vector<pair<int, string>>> documents; // file_name -> [(speaker_num, text)]

    long total_turns = 0;
    long context_turns = 0;
    long filtered_turns = 0;
    long missing_unified = 0;

    while (getline(infile, line)) {
        if (line.empty()) continue;
        total_turns++;

        string fname = get_json_value(line, "file_name");
        string context = get_json_value(line, "context");
        string role = get_json_value(line, "role");
        string employer = get_json_value(line, "employer");
        string text = get_json_value(line, "speaker_text");
        int speaker_num = get_json_int(line, "speaker_number");

        // Check unified info
        if (unified.find(fname) == unified.end()) {
            missing_unified++;
            continue;
        }

        string company = unified[fname].first;

        // Filter by context
        if (DATASET_TYPE != "entire_call") {
            string required_context = (DATASET_TYPE == "manager_pres") ? "pres" : "qa";
            if (context != required_context) continue;
            context_turns++;
        }

        // Filter by role
        bool passes = false;
        if (DATASET_TYPE == "manager_qa" || DATASET_TYPE == "manager_pres") {
            passes = is_managerial(role, employer, company);
        } else if (DATASET_TYPE == "analyst_qa") {
            passes = has_keyword(role, "analyst");
        } else if (DATASET_TYPE == "entire_call") {
            passes = true;
        }

        if (!passes) continue;

        filtered_turns++;
        documents[fname].push_back(make_pair(speaker_num, text));
    }
    infile.close();

    // Print statistics
    cout << "Statistics:" << endl;
    cout << "  Total turns: " << total_turns << endl;
    if (DATASET_TYPE != "entire_call") {
        string ctx = (DATASET_TYPE == "manager_pres") ? "pres" : "qa";
        cout << "  " << ctx << " turns: " << context_turns << endl;
        cout << "  Filtered turns (" << DATASET_TYPE << "): " << filtered_turns << endl;
    } else {
        cout << "  Filtered turns (all speakers, all contexts): " << filtered_turns << endl;
    }
    cout << "  Missing unified info: " << missing_unified << endl;
    cout << "  Final documents: " << documents.size() << endl;

    // Write output
    cout << "Writing output..." << endl;
    ofstream outfile(output_file);
    if (!outfile.is_open()) {
        cerr << "ERROR: Could not open " << output_file << endl;
        return 1;
    }

    // Sort file names for determinism
    vector<string> fnames;
    for (const auto& pair : documents) {
        fnames.push_back(pair.first);
    }
    sort(fnames.begin(), fnames.end());

    for (const auto& fname : fnames) {
        auto& texts = documents[fname];

        // Sort by speaker number
        sort(texts.begin(), texts.end());

        // Aggregate text
        string aggregated;
        for (const auto& pair : texts) {
            if (!aggregated.empty()) aggregated += " ";
            aggregated += pair.second;
        }

        // Get metadata
        string start_date = unified[fname].second;
        int doc_year = year;
        int quarter = 1;
        if (start_date.length() >= 7) {
            doc_year = stoi(start_date.substr(0, 4));
            int month = stoi(start_date.substr(5, 2));
            quarter = ((month - 1) / 3) + 1;
        }

        // Escape text for JSON (backslashes first, then quotes, then newlines)
        string escaped_text;
        for (char c : aggregated) {
            if (c == '\\') escaped_text += "\\\\";
            else if (c == '"') escaped_text += "\\\"";
            else if (c == '\n') escaped_text += "\\n";
            else if (c == '\r') escaped_text += "\\r";
            else if (c == '\t') escaped_text += "\\t";
            else escaped_text += c;
        }

        // Escape filename
        string escaped_fname;
        for (char c : fname) {
            if (c == '\\') escaped_fname += "\\\\";
            else if (c == '"') escaped_fname += "\\\"";
            else escaped_fname += c;
        }

        // Write JSON
        outfile << "{\"file_name\":\"" << escaped_fname << "\""
                << ",\"doc_text\":\"" << escaped_text << "\""
                << ",\"approx_char_len\":" << aggregated.length()
                << ",\"start_date\":\"" << start_date << "\""
                << ",\"year\":" << doc_year
                << ",\"quarter\":" << quarter << "}" << endl;
    }

    outfile.close();
    cout << "Output written successfully" << endl;
    cout << "======================================" << endl;
    cout << "Processing complete" << endl;
    cout << "======================================" << endl;

    return 0;
}

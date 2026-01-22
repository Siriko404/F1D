/*
==============================================================================
STEP 2.3b: Tokenize Text and Count Dictionary Matches (C++)
==============================================================================
ID: 2.3b_TokenizeText
Description: Tokenizes text and counts matches against 2 LM dictionaries
             (Uncertainty and Negative). Pure C++ stdlib implementation.
Inputs:
    - temp_unc_dictionary.jsonl (Uncertainty dictionary tokens)
    - temp_neg_dictionary.jsonl (Negative dictionary tokens)
    - temp_docs_YYYY_QX.jsonl (documents for year-quarter)
Outputs:
    - temp_output_YYYY_QX.jsonl (token counts and metrics per document)
Output Schema: file_name, start_date, total_word_tokens, Uncertainty_hits,
               Negative_hits, unc_pct, neg_pct, top5_uncertainty,
               top5_negative, process_version
Usage:
    2.3b_TokenizeText.exe YEAR QUARTER
Deterministic: true
==============================================================================
*/

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_set>
#include <map>
#include <algorithm>
#include <cctype>

using namespace std;

// ==============================================================================
// Simple JSON parsing utilities
// ==============================================================================

string trim(const string& str) {
    size_t start = str.find_first_not_of(" \t\r\n");
    if (start == string::npos) return "";
    size_t end = str.find_last_not_of(" \t\r\n");
    return str.substr(start, end - start + 1);
}

// Extract JSON string value
string extract_json_string(const string& json, const string& key) {
    string search = "\"" + key + "\":";
    size_t pos = json.find(search);
    if (pos == string::npos) return "";

    pos += search.length();
    while (pos < json.length() && isspace(json[pos])) pos++;

    if (json.substr(pos, 4) == "null") return "";
    if (json[pos] != '"') return "";
    pos++; // Skip opening quote

    string result;
    while (pos < json.length()) {
        if (json[pos] == '\\' && pos + 1 < json.length()) {
            pos++;
            if (json[pos] == 'n') result += '\n';
            else if (json[pos] == 't') result += '\t';
            else if (json[pos] == 'r') result += '\r';
            else if (json[pos] == '"') result += '"';
            else if (json[pos] == '\\') result += '\\';
            else result += json[pos];
            pos++;
        } else if (json[pos] == '"') {
            break;
        } else {
            result += json[pos];
            pos++;
        }
    }

    return result;
}

// ==============================================================================
// Text normalization and tokenization
// ==============================================================================

string normalize_text(const string& text) {
    string result;
    result.reserve(text.length());

    // Convert to uppercase and replace non-letters with spaces
    for (char c : text) {
        if (isalpha(c)) {
            result += toupper(c);
        } else {
            result += ' ';
        }
    }

    // Collapse multiple spaces
    string collapsed;
    collapsed.reserve(result.length());
    bool last_was_space = true;  // Skip leading spaces

    for (char c : result) {
        if (c == ' ') {
            if (!last_was_space) {
                collapsed += ' ';
                last_was_space = true;
            }
        } else {
            collapsed += c;
            last_was_space = false;
        }
    }

    // Remove trailing space if any
    if (!collapsed.empty() && collapsed.back() == ' ') {
        collapsed.pop_back();
    }

    return collapsed;
}

vector<string> tokenize(const string& normalized_text) {
    vector<string> tokens;
    string current_token;

    for (char c : normalized_text) {
        if (c == ' ') {
            if (!current_token.empty()) {
                tokens.push_back(current_token);
                current_token.clear();
            }
        } else {
            current_token += c;
        }
    }

    // Don't forget last token
    if (!current_token.empty()) {
        tokens.push_back(current_token);
    }

    return tokens;
}

// ==============================================================================
// Top N tracking
// ==============================================================================

struct TokenCount {
    string token;
    int count;

    bool operator<(const TokenCount& other) const {
        // Sort by count desc, then alphabetically asc
        if (count != other.count) {
            return count > other.count;  // Descending by count
        }
        return token < other.token;  // Ascending alphabetically
    }
};

vector<TokenCount> get_top_n(const map<string, int>& match_counts, int n) {
    vector<TokenCount> all_tokens;
    for (const auto& pair : match_counts) {
        all_tokens.push_back({pair.first, pair.second});
    }

    sort(all_tokens.begin(), all_tokens.end());

    // Return top N
    vector<TokenCount> result;
    for (size_t i = 0; i < min((size_t)n, all_tokens.size()); i++) {
        result.push_back(all_tokens[i]);
    }

    return result;
}

// ==============================================================================
// Dictionary loading
// ==============================================================================

unordered_set<string> load_dictionary(const string& path) {
    unordered_set<string> dict;
    ifstream file(path);

    if (!file.is_open()) {
        cerr << "ERROR: Could not open " << path << endl;
        return dict;
    }

    string line;
    int count = 0;
    while (getline(file, line)) {
        line = trim(line);
        if (line.empty()) continue;

        string token = extract_json_string(line, "token");
        if (!token.empty()) {
            dict.insert(token);
            count++;
        }
    }

    cout << "Loaded " << count << " dictionary tokens" << endl;
    return dict;
}

// ==============================================================================
// Document processing
// ==============================================================================

struct Document {
    string file_name;
    string doc_text;
    string start_date;
};

struct DocumentMetrics {
    string file_name;
    string start_date;
    int total_word_tokens;
    int uncertainty_hits;
    int negative_hits;
    double unc_pct;
    double neg_pct;
    vector<TokenCount> top5_uncertainty;
    vector<TokenCount> top5_negative;
};

DocumentMetrics process_document(const Document& doc,
                                const unordered_set<string>& unc_dict,
                                const unordered_set<string>& neg_dict) {
    // Normalize and tokenize
    string normalized = normalize_text(doc.doc_text);
    vector<string> tokens = tokenize(normalized);

    // Count total and matches for BOTH dictionaries
    int total_tokens = tokens.size();
    int unc_hits = 0;
    int neg_hits = 0;
    map<string, int> unc_match_counts;  // map for deterministic iteration
    map<string, int> neg_match_counts;

    for (const string& token : tokens) {
        if (unc_dict.count(token)) {
            unc_hits++;
            unc_match_counts[token]++;
        }
        if (neg_dict.count(token)) {
            neg_hits++;
            neg_match_counts[token]++;
        }
    }

    // Calculate percentages
    double unc_pct = (total_tokens > 0) ? (double)unc_hits / total_tokens * 100.0 : 0.0;
    double neg_pct = (total_tokens > 0) ? (double)neg_hits / total_tokens * 100.0 : 0.0;

    // Get top 5 for each dictionary
    vector<TokenCount> top5_unc = get_top_n(unc_match_counts, 5);
    vector<TokenCount> top5_neg = get_top_n(neg_match_counts, 5);

    return {doc.file_name, doc.start_date, total_tokens, unc_hits, neg_hits,
            unc_pct, neg_pct, top5_unc, top5_neg};
}

void process_documents(
    const string& input_path,
    const string& output_path,
    const unordered_set<string>& unc_dict,
    const unordered_set<string>& neg_dict,
    const string& process_version,
    int year,
    int quarter
) {
    ifstream infile(input_path);
    if (!infile.is_open()) {
        cerr << "ERROR: Could not open " << input_path << endl;
        return;
    }

    cout << "Processing documents..." << endl;

    // Parse documents
    vector<Document> documents;
    string line;
    while (getline(infile, line)) {
        line = trim(line);
        if (line.empty()) continue;

        Document doc;
        doc.file_name = extract_json_string(line, "file_name");
        doc.doc_text = extract_json_string(line, "doc_text");
        doc.start_date = extract_json_string(line, "start_date");

        if (!doc.file_name.empty() && !doc.doc_text.empty()) {
            documents.push_back(doc);
        }
    }
    infile.close();

    cout << "  Loaded " << documents.size() << " documents" << endl;

    // Process all documents with BOTH dictionaries
    vector<DocumentMetrics> results;
    for (const auto& doc : documents) {
        results.push_back(process_document(doc, unc_dict, neg_dict));
    }

    // Write output
    cout << "Writing output..." << endl;
    ofstream outfile(output_path);
    if (!outfile.is_open()) {
        cerr << "ERROR: Could not open " << output_path << endl;
        return;
    }

    // Sort by file_name for determinism
    sort(results.begin(), results.end(), [](const DocumentMetrics& a, const DocumentMetrics& b) {
        return a.file_name < b.file_name;
    });

    for (const auto& metrics : results) {
        // Escape strings for JSON
        string escaped_file_name;
        for (char c : metrics.file_name) {
            if (c == '"') escaped_file_name += "\\\"";
            else if (c == '\\') escaped_file_name += "\\\\";
            else escaped_file_name += c;
        }

        string escaped_start_date;
        for (char c : metrics.start_date) {
            if (c == '"') escaped_start_date += "\\\"";
            else if (c == '\\') escaped_start_date += "\\\\";
            else escaped_start_date += c;
        }

        string escaped_process_version;
        for (char c : process_version) {
            if (c == '"') escaped_process_version += "\\\"";
            else if (c == '\\') escaped_process_version += "\\\\";
            else escaped_process_version += c;
        }

        // Build top5_uncertainty JSON array
        string top5_unc_json = "[";
        for (size_t i = 0; i < metrics.top5_uncertainty.size(); i++) {
            if (i > 0) top5_unc_json += ",";

            string escaped_token;
            for (char c : metrics.top5_uncertainty[i].token) {
                if (c == '"') escaped_token += "\\\"";
                else if (c == '\\') escaped_token += "\\\\";
                else escaped_token += c;
            }

            top5_unc_json += "{\\\"token\\\":\\\"" + escaped_token + "\\\",\\\"count\\\":" +
                        to_string(metrics.top5_uncertainty[i].count) + "}";
        }
        top5_unc_json += "]";

        // Build top5_negative JSON array
        string top5_neg_json = "[";
        for (size_t i = 0; i < metrics.top5_negative.size(); i++) {
            if (i > 0) top5_neg_json += ",";

            string escaped_token;
            for (char c : metrics.top5_negative[i].token) {
                if (c == '"') escaped_token += "\\\"";
                else if (c == '\\') escaped_token += "\\\\";
                else escaped_token += c;
            }

            top5_neg_json += "{\\\"token\\\":\\\"" + escaped_token + "\\\",\\\"count\\\":" +
                        to_string(metrics.top5_negative[i].count) + "}";
        }
        top5_neg_json += "]";

        // Write JSON line with BOTH metrics
        outfile << "{\"file_name\":\"" << escaped_file_name << "\""
                << ",\"start_date\":\"" << escaped_start_date << "\""
                << ",\"total_word_tokens\":" << metrics.total_word_tokens
                << ",\"Uncertainty_hits\":" << metrics.uncertainty_hits
                << ",\"Negative_hits\":" << metrics.negative_hits
                << ",\"unc_pct\":" << metrics.unc_pct
                << ",\"neg_pct\":" << metrics.neg_pct
                << ",\"top5_uncertainty\":\"" << top5_unc_json << "\""
                << ",\"top5_negative\":\"" << top5_neg_json << "\""
                << ",\"process_version\":\"" << escaped_process_version << "\"}" << endl;
    }

    outfile.close();
    cout << "Output written successfully: " << results.size() << " documents" << endl;

    // Statistics for BOTH dictionaries
    long total_tokens = 0;
    long total_unc_hits = 0;
    long total_neg_hits = 0;
    for (const auto& m : results) {
        total_tokens += m.total_word_tokens;
        total_unc_hits += m.uncertainty_hits;
        total_neg_hits += m.negative_hits;
    }
    double avg_unc = (total_tokens > 0) ? (double)total_unc_hits / total_tokens * 100.0 : 0.0;
    double avg_neg = (total_tokens > 0) ? (double)total_neg_hits / total_tokens * 100.0 : 0.0;

    cout << "Statistics:" << endl;
    cout << "  Total word tokens: " << total_tokens << endl;
    cout << "  Uncertainty hits: " << total_unc_hits << " (" << avg_unc << "%)" << endl;
    cout << "  Negative hits: " << total_neg_hits << " (" << avg_neg << "%)" << endl;
}

// ==============================================================================
// Main
// ==============================================================================

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cerr << "Usage: " << argv[0] << " YEAR QUARTER" << endl;
        return 1;
    }

    int year = stoi(argv[1]);
    int quarter = stoi(argv[2]);

    cout << "======================================" << endl;
    cout << "Processing " << year << " Q" << quarter << endl;
    cout << "======================================" << endl;

    // Load BOTH dictionaries
    cout << "Loading Uncertainty dictionary..." << endl;
    string unc_dict_path = "temp_unc_dictionary.jsonl";
    auto unc_dictionary = load_dictionary(unc_dict_path);

    if (unc_dictionary.empty()) {
        cerr << "ERROR: No Uncertainty dictionary tokens loaded" << endl;
        return 1;
    }

    cout << "Loading Negative dictionary..." << endl;
    string neg_dict_path = "temp_neg_dictionary.jsonl";
    auto neg_dictionary = load_dictionary(neg_dict_path);

    if (neg_dictionary.empty()) {
        cerr << "ERROR: No Negative dictionary tokens loaded" << endl;
        return 1;
    }

    // Process documents with BOTH dictionaries
    string input_path = "temp_docs_" + to_string(year) + "_Q" + to_string(quarter) + ".jsonl";
    string output_path = "temp_output_" + to_string(year) + "_Q" + to_string(quarter) + ".jsonl";
    string process_version = "F1D.1.0";

    process_documents(input_path, output_path, unc_dictionary, neg_dictionary,
                     process_version, year, quarter);

    cout << "======================================" << endl;
    cout << "Processing complete" << endl;
    cout << "======================================" << endl;

    return 0;
}

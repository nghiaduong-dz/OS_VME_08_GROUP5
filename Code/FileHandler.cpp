#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <exception>
#include <stdexcept>
#include "Models.cpp"

using namespace std;

class FileHandler {
public:
// 1. Read input csv (Extreme safe reader with try-catch logic to avoid App Crash)
    static InputModel ReadInputCSV(const string& filepath) {
        InputModel model;
        ifstream file(filepath);
        
        if (!file.is_open()) {
            throw runtime_error("File not found or cannot be opened: " + filepath);
        }

        string line;
        // Read frame size (Row 1)
        if (!getline(file, line)) {
            throw runtime_error("Error: The file is completely empty.");
        }
        
        try {
            // Trim whitespace
            line.erase(line.find_last_not_of(" \n\r\t") + 1);
            if (line.empty()) throw runtime_error("Error: The first row (Frame Size) is missing.");
            
            model.frameSize = stoi(line);
            
            // Check for negative frame size 
            if (model.frameSize <= 0) {
                throw runtime_error("Error: Frame Size must be greater than 0. Received: " + line);
            }
        } 
        catch (const invalid_argument&) {
            // Catch if user puts letters where numbers should be
            throw runtime_error("Error: Frame Size must be an integer, but received characters. Received: " + line);
        } 
        catch (const out_of_range&) {
            throw runtime_error("Error: Frame Size number is too large to handle.");
        }

        // Read reference string (Row 2)
        if (!getline(file, line)) {
            throw runtime_error("Error: Missing the Reference String on the second row.");
        }

        stringstream ss(line);
        string token;
        while (getline(ss, token, ',')) {
            // Clean spaces around numbers
            size_t start = token.find_first_not_of(" \n\r\t");
            size_t end = token.find_last_not_of(" \n\r\t");
            
            if (start != string::npos && end != string::npos) {
                string trimmedToken = token.substr(start, end - start + 1);
                try {
                    int page = stoi(trimmedToken);
                    if (page < 0) {
                        throw runtime_error("Error: Page request cannot be negative. Found: " + trimmedToken);
                    }
                    model.referenceString.push_back(page);
                } 
                catch (const invalid_argument&) {
                    throw runtime_error("Error: Reference String contains invalid characters. Found: " + trimmedToken);
                } 
                catch (const out_of_range&) {
                    throw runtime_error("Error: Page number is too large. Found: " + trimmedToken);
                }
            }
        }

        if (model.referenceString.empty()) {
            throw runtime_error("Error: The Reference String is empty.");
        }

        file.close();
        return model;
    }

    // 2. Export output csv (Optimized for both small data and 10 Million rows Stress tests)
    static void ExportOutputCSV(const string& filepath, 
                                const InputModel& input,
                                const vector<StepResultModel>& results, // Empty for stress test (optimization)
                                const SummaryModel& summary) {
        
        // Fast I/O: This trick speeds up buffered writing massively for C++ output streams
        ios_base::sync_with_stdio(false);
        
        ofstream outFile(filepath);
        if (!outFile.is_open()) {
            throw runtime_error("Error: Cannot create or open the output file: " + filepath);
        }

        bool isStressTest = (input.referenceString.size() > 500000);

        outFile << "Algorithm, " << summary.algorithmName << "\n";
        outFile << "Frame Size, " << input.frameSize << "\n";
        
        if (!isStressTest) {
            outFile << "Reference String, \"";
            for (size_t i = 0; i < input.referenceString.size(); ++i) {
                outFile << input.referenceString[i];
                if (i < input.referenceString.size() - 1) outFile << ", ";
            }
            outFile << "\"\n";
        } else {
            // Memory optimization for Stress test output: Avoid writing 10M numbers 
            outFile << "Reference String, \"[STRESS TEST - OMITTED FOR PERFORMANCE]\"\n";
        }
        
        outFile << "\n";

        // Write detailed steps
        if (!isStressTest) {
            outFile << "--- Detailed Steps ---\n";
            outFile << "Step, Page";
            for (int i = 1; i <= input.frameSize; ++i) {
                outFile << ", Frame " << i;
            }
            outFile << ", Page Fault, Total_Faults\n";

            for (const auto& stepResult : results) {
                outFile << stepResult.step << ", " << stepResult.pageRequest;
                
                for (int frameData : stepResult.frames) {
                    if (frameData == -1) {
                        outFile << ", -";
                    } else {
                        outFile << ", " << frameData;
                    }
                }
                
                outFile << ", " << (stepResult.isPageFault ? "YES" : "NO") 
                        << ", " << stepResult.currentTotalFaults << "\n";
            }
            outFile << "\n";
        } else {
            outFile << "--- Detailed Steps Omitted for Stress Test (Data length > 500000) ---\n\n";
        }

        // Write sumaray
        int totalRequests = summary.totalPageHits + summary.totalPageFaults;
        double throughput = (summary.executionTimeMs > 0) ? (totalRequests / summary.executionTimeMs) : 0;

        outFile << "--- Summary ---\n";
        outFile << "Total Page Requests, " << totalRequests << "\n";
        outFile << "Page Hit, " << summary.totalPageHits << "\n";
        outFile << "Total Page Fault, " << summary.totalPageFaults << "\n";
        outFile << "Hit Ratio, " << summary.hitRatio << "%\n";
        outFile << "Fault Ratio, " << summary.faultRatio << "%\n";
        outFile << "Execution Time (ms), " << summary.executionTimeMs << "\n";
        outFile << "Throughput (Requests/ms), " << throughput << "\n";

        outFile.close();
    }
};


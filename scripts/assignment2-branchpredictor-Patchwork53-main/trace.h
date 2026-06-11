#ifndef __TRACE_H_
#define __TRACE_H_

#include <iostream>
#include <fstream>
#include <vector>
#include <set>
using namespace std;

class TraceFile{
    private:
        string fileName;
        ifstream inputStream;

    public:
        TraceFile(string fileName);
        bool getNextBranch(string &, bool &);
};

#endif

#ifndef __BRANCH_H_
#define __BRANCH_H_

#include <iostream>
#include <vector>
using namespace std;

class Predictor{
    private:

        unsigned int addrBits; //number of bits of address used to index  
        unsigned int historyBits; //number of bits used for global history
        unsigned int globalHistory; //record of global histroy
        unsigned int counterBits; //number of bits per counter
        vector<unsigned int> pht; //n-bit saturating counters
        vector<unsigned char> phtUsed; //tracks which entries are accessed
        size_t usedEntries;
        int correct;
        int total;
        bool debug;
	unsigned int hexToInt(string);
        unsigned int truncateAddress (unsigned int);
        void updateGlobalHistory(bool); //update the history
    void updateCounter(unsigned int, bool);

    public:
        Predictor(unsigned int, unsigned int, unsigned int, bool);
        bool makePrediction(string, bool);
        void printStats();
};

#endif

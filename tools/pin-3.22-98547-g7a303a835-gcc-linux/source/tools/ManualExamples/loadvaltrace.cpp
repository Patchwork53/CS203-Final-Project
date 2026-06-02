#include "pin.H"

#include <cstdio>

FILE* trace = nullptr;

KNOB<std::string> KnobOutputFile(
    KNOB_MODE_WRITEONCE,
    "pintool",
    "o",
    "pinatrace.out",
    "specify output trace file name"
);

VOID RecordMemRead(VOID* ip, VOID* addr)
{
    ADDRINT value = 0;
    PIN_SafeCopy(&value, addr, sizeof(ADDRINT));
    std::fprintf(trace, "%p: R %p, 0x%016lx\n", ip, addr, static_cast<unsigned long>(value));
}

VOID Instruction(INS ins, VOID* v)
{
    (void)v;
    UINT32 memOperands = INS_MemoryOperandCount(ins);

    for (UINT32 memOp = 0; memOp < memOperands; memOp++) {
        if (INS_MemoryOperandIsRead(ins, memOp)) {
            INS_InsertPredicatedCall(
                ins,
                IPOINT_BEFORE,
                AFUNPTR(RecordMemRead),
                IARG_INST_PTR,
                IARG_MEMORYOP_EA,
                memOp,
                IARG_END
            );
        }
    }
}

VOID Fini(INT32 code, VOID* v)
{
    (void)code;
    (void)v;
    std::fclose(trace);
}

INT32 Usage()
{
    PIN_ERROR("Load value trace pintool\n"
              + KNOB_BASE::StringKnobSummary()
              + "\n");
    return -1;
}

int main(int argc, char* argv[])
{
    if (PIN_Init(argc, argv)) {
        return Usage();
    }

    trace = std::fopen(KnobOutputFile.Value().c_str(), "w");
    if (trace == nullptr) {
        PIN_ERROR("Unable to open output trace file\n");
    }

    INS_AddInstrumentFunction(Instruction, nullptr);
    PIN_AddFiniFunction(Fini, nullptr);

    PIN_StartProgram();
    return 0;
}

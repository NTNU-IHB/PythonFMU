
#include "cppfmu/cppfmu_common.hpp"

extern "C" {

/* Log a message from Python to the FMU logger */
void pylog(void* logPtr, int status, const char* category, const char* msg, bool debug)
{
    auto logger = ((cppfmu::Logger*) logPtr);
    if (!debug) {
        logger->Log((fmi2Status) status, category, msg);
    } else {
        logger->DebugLog((fmi2Status) status, category, msg);
    }
}

}

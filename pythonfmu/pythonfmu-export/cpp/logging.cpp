
#include "cppfmu/cppfmu_common.hpp"

extern "C" {

void log_info(void* logPtr, int status, const char* msg)
{
    cppfmu::Logger* logger = ((cppfmu::Logger*)logPtr);
    logger->Log((fmi2Status) status, "", msg);
}

void log_debug(void* logPtr, int status, const char* msg)
{
    cppfmu::Logger* logger = ((cppfmu::Logger*)logPtr);
    logger->DebugLog((fmi2Status) status, "", msg);
}
}

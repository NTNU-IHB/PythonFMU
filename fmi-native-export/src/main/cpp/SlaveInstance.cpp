
#include <pythonfmu/SlaveInstance.hpp>

#include <cppfmu/cppfmu_cs.hpp>

#include <fstream>

namespace pythonfmu
{

SlaveInstance::SlaveInstance(
    const cppfmu::Memory& memory,
    const PyObjectWrapper& instance,
    const std::string& resources)
    : instance_(instance)
{
    instance_.initialize();
}

void SlaveInstance::SetupExperiment(cppfmu::FMIBoolean, cppfmu::FMIReal, cppfmu::FMIReal tStart, cppfmu::FMIBoolean, cppfmu::FMIReal)
{
    instance_.setupExperiment(tStart);
}

void SlaveInstance::EnterInitializationMode()
{
    instance_.enterInitializationMode();
}

void SlaveInstance::ExitInitializationMode()
{
    instance_.exitInitializationMode();
}

bool SlaveInstance::DoStep(cppfmu::FMIReal currentCommunicationPoint, cppfmu::FMIReal communicationStepSize, cppfmu::FMIBoolean, cppfmu::FMIReal& endOfStep)
{
    return instance_.doStep(currentCommunicationPoint, communicationStepSize);
}

void SlaveInstance::Reset()
{
}


void SlaveInstance::Terminate()
{
    instance_.terminate();
}

void SlaveInstance::SetReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIReal* value)
{
}

void SlaveInstance::SetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIInteger* value)
{
}

void SlaveInstance::SetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, const cppfmu::FMIBoolean* value)
{
}

void SlaveInstance::SetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString const* value)
{
}

void SlaveInstance::GetReal(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIReal* value) const
{
}


void SlaveInstance::GetInteger(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIInteger* value) const
{
}

void SlaveInstance::GetBoolean(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIBoolean* value) const
{
}

void SlaveInstance::GetString(const cppfmu::FMIValueReference* vr, std::size_t nvr, cppfmu::FMIString* value) const
{
}

SlaveInstance::~SlaveInstance() = default;


} // namespace pythonfmu

bool pyInit = false;

cppfmu::UniquePtr<cppfmu::SlaveInstance> CppfmuInstantiateSlave(
    cppfmu::FMIString,
    cppfmu::FMIString,
    cppfmu::FMIString fmuResourceLocation,
    cppfmu::FMIString,
    cppfmu::FMIReal,
    cppfmu::FMIBoolean,
    cppfmu::FMIBoolean,
    cppfmu::Memory memory,
    cppfmu::Logger)
{

    if (!pyInit) {
        Py_Initialize();
        pyInit = true;
    }

    std::string resources = std::string(fmuResourceLocation);
    auto find = resources.find("file:///");
    if (find != std::string::npos) {
        resources.replace(find, 8, "");
    }

    PyObject* pModule = PyImport_ImportModule("model");
    PyObject* pClass = PyObject_GetAttrString(pModule, "Model");
    PyObject* pInstance = PyObject_CallFunctionObjArgs(pClass, nullptr);

    return cppfmu::AllocateUnique<pythonfmu::SlaveInstance>(
        memory, memory, pythonfmu::PyObjectWrapper(pModule, pClass, pInstance), resources);
}

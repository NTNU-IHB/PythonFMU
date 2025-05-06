
#ifndef PYTHONFMU_SLAVEINSTANCE_HPP
#define PYTHONFMU_SLAVEINSTANCE_HPP

#include "IPyState.hpp"
#include "Logger.hpp"

#include <memory>
#include <optional>

namespace pythonfmu
{

struct fmu_data
{
    PyLogger* fmiLogger{nullptr};
    bool visible{false};
    std::string instanceName;
    std::string resourceLocation;
    std::shared_ptr<IPyState> pyState;
};

class SlaveInstance
{
public:

    virtual void SetupExperiment(double start, std::optional<double> stop, std::optional<double> tolerance) = 0;

    virtual void EnterInitializationMode() = 0;

    virtual void ExitInitializationMode() = 0;

    virtual void Terminate() = 0;

    virtual void Reset() = 0;

    virtual void SetReal(
        const unsigned int vr[],
        std::size_t nvr,
        const fmi2Real value[]) = 0;
    virtual void SetInteger(
        const unsigned int vr[],
        std::size_t nvr,
        const int value[]) = 0;
    virtual void SetBoolean(
        const unsigned int vr[],
        std::size_t nvr,
        const int value[]) = 0;
    virtual void SetString(
        const unsigned int vr[],
        std::size_t nvr,
        const char* const value[]) = 0;

    virtual void GetReal(
        const unsigned int vr[],
        std::size_t nvr,
        fmi2Real value[]) const = 0;
    virtual void GetInteger(
        const unsigned int vr[],
        std::size_t nvr,
        int value[]) const = 0;
    virtual void GetBoolean(
        const unsigned int vr[],
        std::size_t nvr,
        int value[]) const = 0;
    virtual void GetString(
        const unsigned int vr[],
        std::size_t nvr,
        const char* value[]) const = 0;

    bool DoStep(
        double currentCommunicationPoint,
        double communicationStepSize)
    {
        return Step(currentCommunicationPoint, communicationStepSize);
    }

    virtual bool Step(double currentTime, double dt) = 0;

    virtual void GetFMUstate(fmi2FMUstate& state) = 0;
    virtual void SetFMUstate(const fmi2FMUstate& state) = 0;
    virtual void FreeFMUstate(fmi2FMUstate& state) = 0;

    virtual size_t SerializedFMUstateSize(const fmi2FMUstate& state) = 0;
    virtual void SerializeFMUstate(const fmi2FMUstate& state, fmi2Byte bytes[], size_t size) = 0;
    virtual void DeSerializeFMUstate(const fmi2Byte bytes[], size_t size, fmi2FMUstate& state) = 0;

    virtual ~SlaveInstance() = default;
    ;
};

std::unique_ptr<SlaveInstance> createInstance(fmu_data data);

} // namespace pythonfmu

#endif // PYTHONFMU_SLAVEINSTANCE_HPP


#ifndef PYTHONFMU_SLAVEINSTANCE_HPP
#define PYTHONFMU_SLAVEINSTANCE_HPP

#include <fmi/fmi2Functions.h>
#include <optional>

namespace pythonfmu
{

class SlaveInstance
{
public:
    void EnterInitializationMode(double start, std::optional<double> stop, std::optional<double> tolerance)
    {
        EnterInitializationMode();
    }

    virtual void EnterInitializationMode();

    virtual void ExitInitializationMode();

    virtual void Terminate();

    virtual void Reset();

    virtual void SetReal(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        const fmi2Real value[]);
    virtual void SetInteger(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        const fmi2Integer value[]);
    virtual void SetBoolean(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        const fmi2Boolean value[]);
    virtual void SetString(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        const fmi2String value[]);

    /* Called from fmi2GetXxx()/fmiGetXxx().
     * Throws std::logic_error by default.
     */
    virtual void GetReal(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        fmi2Real value[]) const;
    virtual void GetInteger(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        fmi2Integer value[]) const;
    virtual void GetBoolean(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        fmi2Boolean value[]) const;
    virtual void GetString(
        const fmi2ValueReference vr[],
        std::size_t nvr,
        fmi2String value[]) const;

    // Called from fmi2DoStep()/fmiDoStep(). Must be implemented in model code.
    virtual bool DoStep(
        fmi2Real currentCommunicationPoint,
        fmi2Real communicationStepSize,
        fmi2Boolean newStep,
        fmi2Real& endOfStep) = 0;

    virtual void GetFMUstate(fmi2FMUstate& state) = 0;
    virtual void SetFMUstate(const fmi2FMUstate& state) = 0;
    virtual void FreeFMUstate(fmi2FMUstate& state) = 0;

    virtual size_t SerializedFMUstateSize(const fmi2FMUstate& state) = 0;
    virtual void SerializeFMUstate(const fmi2FMUstate& state, fmi2Byte bytes[], size_t size) = 0;
    virtual void DeSerializeFMUstate(const fmi2Byte bytes[], size_t size, fmi2FMUstate& state) = 0;

    // The instance is destroyed in fmi2FreeInstance()/fmiFreeSlaveInstance().
    virtual ~SlaveInstance();
};

} // namespace pythonfmu

#endif // PYTHONFMU_SLAVEINSTANCE_HPP

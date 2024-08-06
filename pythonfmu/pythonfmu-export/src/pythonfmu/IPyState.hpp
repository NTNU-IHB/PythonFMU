#ifndef PYTHONFMU_IPYTHONSTATE_HPP
#define PYTHONFMU_IPYTHONSTATE_HPP

namespace pythonfmu
{
    class IPyState
    {
    public:
        IPyState() = default;
        IPyState(IPyState const& other) = delete;
        IPyState(IPyState&& other) = delete;
        IPyState& operator=(IPyState const& other) = delete;
        IPyState& operator=(IPyState&& other) = delete;
        virtual ~IPyState() = default;
    };
}

#endif //PYTHONFMU_IPYTHONSTATE_HPP
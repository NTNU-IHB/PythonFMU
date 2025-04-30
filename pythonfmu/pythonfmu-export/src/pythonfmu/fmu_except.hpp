
#ifndef PYTHONFMU_FMU_EXCEPT_HPP
#define PYTHONFMU_FMU_EXCEPT_HPP

#include <stdexcept>
#include <string>

namespace pythonfmu {

    class fatal_error final : public std::runtime_error {
    public:
        explicit fatal_error(const std::string &msg) : std::runtime_error(msg) {}
    };


}// namespace pythonfmu

#endif//PYTHONFMU_FMU_EXCEPT_HPP

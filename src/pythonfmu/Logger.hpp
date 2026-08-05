
#ifndef PYTHONFMU_LOGGER_HPP
#define PYTHONFMU_LOGGER_HPP

#include "fmi/fmi2Functions.h"
#include "LogCategories.hpp"

#include <algorithm>
#include <string>
#include <vector>

namespace pythonfmu
{

class PyLogger
{

public:
    explicit PyLogger(std::string instanceName)
        : instanceName_(std::move(instanceName))
    { }

    void setDebugLogging(bool flag, const std::vector<std::string>& categories = {})
    {
        debugLogging_ = flag;
        categories_ = categories;
    }

    // Logs a message, deriving its category from the status (mirrors Fmi2Slave.log in Python).
    void log(fmi2Status s, const std::string& message)
    {
        log(s, defaultCategoryForStatus(s), message);
    }

    void log(fmi2Status s, const std::string& category, const std::string& message)
    {
        if (debugLogging_) {
            if (categories_.empty() || std::find(categories_.begin(), categories_.end(), category) != categories_.end()) {
                debugLog(s, category, message);
            }
        }
    }

    virtual ~PyLogger() = default;

private:
    bool debugLogging_{false};

    // Mirrors the category derivation in Fmi2Slave.log (Python), generated from the
    // shared status->category table in LogCategories.hpp so both sides stay in sync.
    static std::string defaultCategoryForStatus(fmi2Status s)
    {
        switch (s) {
#define PYTHONFMU_LOG_CATEGORY(status, name, description) \
    case status: \
        return name;
            PYTHONFMU_LOG_CATEGORIES
#undef PYTHONFMU_LOG_CATEGORY
        default:
            return PYTHONFMU_LOG_ALL_CATEGORY;
        }
    }

protected:
    std::string instanceName_;
    std::vector<std::string> categories_;

    virtual void debugLog(fmi2Status s, const std::string& category, const std::string& message) = 0;
};

} // namespace pythonfmu

#endif // PYTHONFMU_LOGGER_HPP

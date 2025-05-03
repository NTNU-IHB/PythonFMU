
#ifndef PYTHONFMU_LOGGER_HPP
#define PYTHONFMU_LOGGER_HPP

#include "fmi/fmi2Functions.h"

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

    // Logs a message.
    void log(fmi2Status s, const std::string& message)
    {
        log(s, "", message);
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

protected:
    std::string instanceName_;
    std::vector<std::string> categories_;

    virtual void debugLog(fmi2Status s, const std::string& category, const std::string& message) = 0;
};

} // namespace pythonfmu

#endif // PYTHONFMU_LOGGER_HPP

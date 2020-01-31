
#include <pythonfmu/thread_worker.hpp>

#include <utility>

namespace pythonfmu
{

thread_worker::thread_worker()
{
    worker_ = std::thread(&thread_worker::listen, this);
}

void thread_worker::work(std::function<void()> f)
{
    f_ = std::move(f);
    {
        std::lock_guard<std::mutex> lk(m_);
        ready_ = true;
        processed_ = false;
    }

    cv_.notify_one();

    {
        std::unique_lock<std::mutex> lk(m_);
        cv_.wait(lk, [this] {
            return processed_;
        });
    }
}

void thread_worker::listen()
{
    while (!stop_) {

        std::unique_lock<std::mutex> lk(m_);
        cv_.wait(lk, [this] {
            return ready_;
        });

        if (stop_) break;

        f_();

        ready_ = false;
        processed_ = true;

        lk.unlock();
        cv_.notify_one();
    }
}


thread_worker::~thread_worker()
{
    stop_ = true;
    {
        std::lock_guard<std::mutex> lk(m_);
        ready_ = true;
    }

    cv_.notify_one();
    worker_.join();
}

} // namespace pythonfmu

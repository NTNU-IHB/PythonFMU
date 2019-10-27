
#include <pythonfmu/PyException.hpp>

#include <Python.h>
#include <iostream>
#include <jni.h>
#include <sstream>

namespace
{
inline const char* get_class_name(PyObject* pModule)
{
    auto f = PyObject_GetAttrString(pModule, "slave_class");
    if (f != nullptr) {
        return PyUnicode_AsUTF8(f);
    }
    return nullptr;
}
} // namespace

extern "C" {

JNIEXPORT jstring JNICALL Java_no_ntnu_ihb_pythonfmu_util_ModelDescriptionFetcher_getModelDescription(
    JNIEnv* env,
    jobject,
    jstring jScriptPath,
    jstring jModuleName)
{

    Py_Initialize();

    auto scriptPath = env->GetStringUTFChars(jScriptPath, nullptr);
    std::ostringstream oss;
    oss << "import sys\n";
    oss << "sys.path.append(r'" << scriptPath << "')\n";
    PyRun_SimpleString(oss.str().c_str());
    env->ReleaseStringUTFChars(jScriptPath, scriptPath);

    auto moduleName = env->GetStringUTFChars(jModuleName, nullptr);
    auto pModule = PyImport_ImportModule(moduleName);
    env->ReleaseStringUTFChars(jModuleName, moduleName);
    if (pModule == nullptr) {
        pythonfmu::handle_py_exception();
    }
    auto className = get_class_name(pModule);
    if (className == nullptr) {
        Py_Finalize();
        pythonfmu::handle_py_exception();
    }

    auto slaveClass = PyObject_GetAttrString(pModule, className);
    if (slaveClass == nullptr) {
        pythonfmu::handle_py_exception();
    }

    auto slaveInstance = PyObject_CallFunctionObjArgs(slaveClass, nullptr);
    if (slaveInstance == nullptr) {
        pythonfmu::handle_py_exception();
    }

    auto f = PyObject_CallMethod(slaveInstance, "define", nullptr);
    if (f == nullptr) {
        Py_Finalize();
        return nullptr;
    } else {
        const char* xml = PyUnicode_AsUTF8(f);
        Py_XDECREF(f);
        Py_Finalize();
        return env->NewStringUTF(xml);
    }
}

}


#include <Python.h>
#include <iostream>
#include <jni.h>
#include <sstream>

extern "C" {

JNIEXPORT jstring JNICALL Java_no_ntnu_ihb_pythonfmu_util_ModelDescriptionFetcher_getModelDescription(
    JNIEnv* env,
    jobject,
    jstring jScriptPath,
    jstring jModuleName,
    jstring jClassName)
{

    Py_Initialize();

    const char* scriptPath = env->GetStringUTFChars(jScriptPath, nullptr);
    std::ostringstream oss;
    oss << "import sys\n";
    oss << "sys.path.append(r'" << scriptPath << "')\n";
    PyRun_SimpleString(oss.str().c_str());
    env->ReleaseStringUTFChars(jScriptPath, scriptPath);

    const char* moduleName = env->GetStringUTFChars(jModuleName, nullptr);
    PyObject* pModule = PyImport_ImportModule(moduleName);
    env->ReleaseStringUTFChars(jModuleName, moduleName);

    const char* className = env->GetStringUTFChars(jClassName, nullptr);
    PyObject* modelClass = PyObject_GetAttrString(pModule, className);
    env->ReleaseStringUTFChars(jClassName, className);

    PyObject* modelInstance = PyObject_CallFunctionObjArgs(modelClass, nullptr);
    auto f = PyObject_CallMethod(modelInstance, "define", nullptr);
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


#include <Python.h>
#include <iostream>
#include <jni.h>
#include <sstream>

extern "C" {

JNIEXPORT jstring JNICALL Java_no_ntnu_ihb_pythonfmu_util_ModelDescriptionFetcher_getModelDescription(JNIEnv* env, jobject obj, jstring jScriptPath, jstring jModuleName)
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
    PyObject* modelClass = PyObject_GetAttrString(pModule, "Model");
    PyObject* modelInstance = PyObject_CallFunctionObjArgs(modelClass, nullptr);

    Py_XDECREF(PyObject_CallMethod(modelInstance, "define", nullptr));

    PyObject* pyXml = PyObject_GetAttrString(modelInstance, "xml");
    const char* xml = PyUnicode_AsUTF8(pyXml);

    Py_XDECREF(pyXml);

    Py_FinalizeEx();

    return env->NewStringUTF(xml);
}
}

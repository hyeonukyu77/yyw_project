#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <time.h>

#define MAX_CLASSES 8

typedef struct {
    int period;
    const char *start_time;
    const char *subject;
} ClassInfo;

typedef struct {
    const char *weekday_name;
    ClassInfo classes[MAX_CLASSES];
    int class_count;
} DailyTimetable;

static const DailyTimetable TIMETABLE[7] = {
    {
        "월요일",
        {
            {1, "08:20", "B_화ⅡB"},
            {2, "09:20", "영독"},
            {3, "10:20", "화학"},
            {4, "11:20", "A_화ⅡA"},
            {5, "13:10", "인수"},
            {6, "14:10", "학통"},
        },
        6,
    },
    {
        "화요일",
        {
            {1, "08:20", "영독"},
            {2, "09:20", "B_화ⅡB"},
            {3, "10:20", "화실"},
            {4, "11:20", "화학"},
            {5, "13:10", "미적"},
            {6, "14:10", "논술"},
            {7, "15:10", "학통"},
        },
        7,
    },
    {
        "수요일",
        {
            {1, "08:20", "일Ⅱ"},
            {2, "09:20", "일Ⅱ"},
            {3, "10:20", "미적"},
            {4, "11:20", "화ⅡA"},
            {5, "13:10", "인수"},
            {6, "14:10", "화실"},
            {7, "15:10", "화실"},
        },
        7,
    },
    {
        "목요일",
        {
            {1, "08:20", "A_화ⅡA"},
            {2, "09:20", "화작"},
            {3, "10:20", "B_화ⅡB"},
            {4, "11:20", "영독"},
            {5, "13:10", "스생"},
            {7, "15:10", "인수"},
        },
        6,
    },
    {
        "금요일",
        {
            {1, "08:20", "영독"},
            {2, "09:20", "체육"},
            {3, "10:20", "진로"},
            {4, "11:20", "미적"},
            {5, "13:10", "동아리"},
            {6, "14:10", "창체"},
        },
        6,
    },
    {"토요일", {{0, NULL, NULL}}, 0},
    {"일요일", {{0, NULL, NULL}}, 0},
};

static int get_local_weekday(void)
{
    time_t current_time = time(NULL);
    struct tm local_time;

    if (current_time == (time_t)-1 || localtime_s(&local_time, &current_time) != 0) {
        PyErr_SetString(PyExc_RuntimeError, "현재 날짜를 확인할 수 없습니다.");
        return -1;
    }

    /* tm_wday: 일요일=0, 월요일=1, ... 토요일=6 */
    return (local_time.tm_wday + 6) % 7;
}

static int get_weekday_from_object(PyObject *now)
{
    PyObject *weekday_result;
    long weekday;

    if (now == NULL || now == Py_None) {
        return get_local_weekday();
    }

    weekday_result = PyObject_CallMethod(now, "weekday", NULL);
    if (weekday_result == NULL) {
        return -1;
    }

    weekday = PyLong_AsLong(weekday_result);
    Py_DECREF(weekday_result);

    if (weekday == -1 && PyErr_Occurred()) {
        return -1;
    }
    if (weekday < 0 || weekday > 6) {
        PyErr_SetString(PyExc_ValueError, "weekday 값은 0부터 6 사이여야 합니다.");
        return -1;
    }

    return (int)weekday;
}

static PyObject *build_class_dict(const ClassInfo *class_info)
{
    PyObject *item = PyDict_New();
    PyObject *period;
    PyObject *start_time;
    PyObject *subject;

    if (item == NULL) {
        return NULL;
    }

    period = PyLong_FromLong(class_info->period);
    start_time = PyUnicode_FromString(class_info->start_time);
    subject = PyUnicode_FromString(class_info->subject);

    if (period == NULL || start_time == NULL || subject == NULL) {
        Py_XDECREF(period);
        Py_XDECREF(start_time);
        Py_XDECREF(subject);
        Py_DECREF(item);
        return NULL;
    }

    if (PyDict_SetItemString(item, "period", period) < 0 ||
        PyDict_SetItemString(item, "time", start_time) < 0 ||
        PyDict_SetItemString(item, "subject", subject) < 0) {
        Py_DECREF(period);
        Py_DECREF(start_time);
        Py_DECREF(subject);
        Py_DECREF(item);
        return NULL;
    }

    Py_DECREF(period);
    Py_DECREF(start_time);
    Py_DECREF(subject);
    return item;
}

static PyObject *get_today_timetable(PyObject *self, PyObject *args, PyObject *kwargs)
{
    static char *keyword_names[] = {"now", NULL};
    PyObject *now = Py_None;
    PyObject *classes;
    PyObject *result;
    PyObject *weekday_name;
    const DailyTimetable *day;
    int weekday;
    int index;

    (void)self;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O:get_today_timetable",
                                     keyword_names, &now)) {
        return NULL;
    }

    weekday = get_weekday_from_object(now);
    if (weekday < 0) {
        return NULL;
    }

    day = &TIMETABLE[weekday];
    classes = PyList_New(day->class_count);
    if (classes == NULL) {
        return NULL;
    }

    for (index = 0; index < day->class_count; index++) {
        PyObject *item = build_class_dict(&day->classes[index]);
        if (item == NULL) {
            Py_DECREF(classes);
            return NULL;
        }
        PyList_SET_ITEM(classes, index, item);
    }

    weekday_name = PyUnicode_FromString(day->weekday_name);
    if (weekday_name == NULL) {
        Py_DECREF(classes);
        return NULL;
    }

    result = PyTuple_Pack(2, weekday_name, classes);
    Py_DECREF(weekday_name);
    Py_DECREF(classes);
    return result;
}

static PyMethodDef timetable_methods[] = {
    {
        "get_today_timetable",
        (PyCFunction)(void(*)(void))get_today_timetable,
        METH_VARARGS | METH_KEYWORDS,
        "현재 요일의 이름과 시간표 목록을 반환합니다.",
    },
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef timetable_module = {
    PyModuleDef_HEAD_INIT,
    "timetable_module",
    "ANAVI 시간표 C 확장 모듈",
    -1,
    timetable_methods,
};

PyMODINIT_FUNC PyInit_timetable_module(void)
{
    return PyModule_Create(&timetable_module);
}

/*
 * 시간표 모듈
 *
 * [프로그램의 역할]
 * 1. 요일별 시간표를 C 언어의 배열에 저장한다.
 * 2. 컴퓨터의 현재 요일을 구한다.
 * 3. 오늘의 시간표를 Python이 읽을 수 있는 형태로 바꾼다.
 * 4. app.py에서 get_today_timetable() 함수로 사용할 수 있게 한다.
 *
 * 이 파일은 일반 C 프로그램이 아니라 Python과 연결되는 'C 확장 모듈'이다.
 * 따라서 실행 파일(.exe)이 아닌 Python 확장 파일(.pyd)로 빌드한다.
 */

/* Python과 C를 연결하는 기능을 사용할 수 있게 해 주는 헤더 파일 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* 현재 날짜와 요일을 알아내기 위한 C 표준 라이브러리 */
#include <time.h>

/* 하루에 저장할 수 있는 최대 수업 수 */
#define MAX_CLASSES 8

/*
 * 구조체(struct)는 서로 관련된 여러 자료를 하나로 묶는 기능이다.
 * ClassInfo 하나에는 수업 한 교시의 정보가 들어간다.
 */
typedef struct {
    int period;             /* 교시 번호 */
    const char *start_time; /* 수업 시작 시각 */
    const char *subject;    /* 과목명 */
} ClassInfo;

/* DailyTimetable 하나에는 하루 전체의 시간표가 들어간다. */
typedef struct {
    const char *weekday_name;          /* 요일 이름 */
    ClassInfo classes[MAX_CLASSES];    /* 그날의 수업 배열 */
    int class_count;                   /* 실제로 저장된 수업 개수 */
} DailyTimetable;

/*
 * 월요일부터 일요일까지 총 7일의 시간표 데이터이다.
 * 배열 번호는 0=월요일, 1=화요일, ..., 6=일요일 순서이다.
 * static const를 사용해 이 파일 안에서만 읽을 수 있고 수정은 할 수 없게 했다.
 */
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
    /*
     * time(NULL)은 현재 시각을 초 단위 숫자로 가져온다.
     * localtime_s는 그 숫자를 연, 월, 일, 요일처럼 사용하기 쉬운 형태로 바꾼다.
     */
    time_t current_time = time(NULL);
    struct tm local_time;

    /* 날짜 정보를 가져오지 못하면 Python에 오류 내용을 전달한다. */
    if (current_time == (time_t)-1 || localtime_s(&local_time, &current_time) != 0) {
        PyErr_SetString(PyExc_RuntimeError, "현재 날짜를 확인할 수 없습니다.");
        return -1;
    }

    /*
     * C의 tm_wday: 일=0, 월=1, ..., 토=6
     * 시간표 배열:     월=0, 화=1, ..., 일=6
     * 따라서 6을 더한 뒤 7로 나눈 나머지를 구해 순서를 맞춘다.
     * 예: 일요일 0 -> (0+6)%7 = 6
     */
    return (local_time.tm_wday + 6) % 7;
}

/*
 * 평소에는 컴퓨터의 오늘 요일을 사용한다.
 * 테스트할 때 날짜를 전달하면 그 날짜의 weekday() 결과를 대신 사용한다.
 */
static int get_weekday_from_object(PyObject *now)
{
    PyObject *weekday_result;
    long weekday;

    if (now == NULL || now == Py_None) {
        return get_local_weekday();
    }

    /* C에서 Python 날짜 객체의 weekday() 메서드를 호출하는 부분 */
    weekday_result = PyObject_CallMethod(now, "weekday", NULL);
    if (weekday_result == NULL) {
        return -1;
    }

    weekday = PyLong_AsLong(weekday_result);
    /*
     * Python 객체는 사용 횟수를 세어 메모리를 관리한다.
     * Py_DECREF는 이 객체를 더 이상 사용하지 않는다고 알려 주는 명령이다.
     */
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
    /*
     * C 구조체 한 개를 아래와 같은 Python 딕셔너리로 바꾼다.
     * {"period": 1, "time": "08:20", "subject": "영어"}
     */
    PyObject *item = PyDict_New();
    PyObject *period;
    PyObject *start_time;
    PyObject *subject;

    if (item == NULL) {
        return NULL;
    }

    /* C의 int와 문자열을 Python의 숫자와 문자열 객체로 변환한다. */
    period = PyLong_FromLong(class_info->period);
    start_time = PyUnicode_FromString(class_info->start_time);
    subject = PyUnicode_FromString(class_info->subject);

    /* 변환 도중 하나라도 실패하면 이미 만든 객체를 정리하고 종료한다. */
    if (period == NULL || start_time == NULL || subject == NULL) {
        Py_XDECREF(period);
        Py_XDECREF(start_time);
        Py_XDECREF(subject);
        Py_DECREF(item);
        return NULL;
    }

    /* 만든 값을 period, time, subject라는 이름으로 딕셔너리에 저장한다. */
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
    /*
     * app.py가 실제로 호출하는 핵심 함수이다.
     * 반환 형태:
     * ("금요일", [{"period": 1, "time": "08:20", "subject": "영독"}, ...])
     */
    static char *keyword_names[] = {"now", NULL};
    PyObject *now = Py_None;
    PyObject *classes;
    PyObject *result;
    PyObject *weekday_name;
    const DailyTimetable *day;
    int weekday;
    int index;

    (void)self;

    /*
     * Python에서 전달된 선택 인자 now를 읽는다.
     * |O는 객체(Object) 하나를 선택적으로 받을 수 있다는 뜻이다.
     */
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O:get_today_timetable",
                                     keyword_names, &now)) {
        return NULL;
    }

    weekday = get_weekday_from_object(now);
    if (weekday < 0) {
        return NULL;
    }

    /* 오늘 요일 번호를 이용해 배열에서 오늘 시간표를 선택한다. */
    day = &TIMETABLE[weekday];

    /* Python에 전달할 빈 리스트를 수업 개수만큼 만든다. */
    classes = PyList_New(day->class_count);
    if (classes == NULL) {
        return NULL;
    }

    /* 각 수업을 Python 딕셔너리로 바꿔 리스트에 차례대로 넣는다. */
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

    /* 요일 이름과 수업 목록을 하나의 튜플로 묶어서 app.py에 돌려준다. */
    result = PyTuple_Pack(2, weekday_name, classes);
    Py_DECREF(weekday_name);
    Py_DECREF(classes);
    return result;
}

static PyMethodDef timetable_methods[] = {
    /*
     * C 함수와 Python에서 사용할 함수 이름을 연결하는 표이다.
     * 이 설정 덕분에 Python에서 timetable_module.get_today_timetable()로 호출한다.
     */
    {
        "get_today_timetable",
        (PyCFunction)(void(*)(void))get_today_timetable,
        METH_VARARGS | METH_KEYWORDS,
        "현재 요일의 이름과 시간표 목록을 반환합니다.",
    },
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef timetable_module = {
    /* Python에 모듈의 이름, 설명, 함수 목록을 알려 주는 설정이다. */
    PyModuleDef_HEAD_INIT,
    "timetable_module",
    "ANAVI 시간표 C 확장 모듈",
    -1,
    timetable_methods,
};

PyMODINIT_FUNC PyInit_timetable_module(void)
{
    /*
     * Python이 import timetable_module을 실행할 때 가장 먼저 호출하는 함수이다.
     * 설정 내용을 바탕으로 실제 Python 모듈 객체를 만들어 반환한다.
     */
    return PyModule_Create(&timetable_module);
}

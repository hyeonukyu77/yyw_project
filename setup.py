from setuptools import Extension, setup
###
# timetable_module.c를 Python이 import할 수 있는 .pyd 파일로 빌드한다.
setup(
    name="anavi-timetable",
    version="1.0.0",
    ext_modules=[
        Extension(
            name="timetable_module",
            sources=["timetable_module.c"],
            # C 파일에 들어 있는 한글을 Windows 컴파일러가 UTF-8로 읽게 한다.
            extra_compile_args=["/utf-8"],
        )
    ],
)

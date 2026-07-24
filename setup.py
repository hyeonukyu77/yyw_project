from setuptools import Extension, setup


setup(
    name="anavi-timetable",
    version="1.0.0",
    ext_modules=[
        Extension(
            name="timetable_module",
            sources=["timetable_module.c"],
            extra_compile_args=["/utf-8"],
        )
    ],
)

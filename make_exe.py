"""Модуль для изготовления скомпилированных .exe файлов"""
import subprocess
import shutil
import os


for file in (
    'musicrebuilder.py',
    'musicsaver.py',
):
    subprocess.run(f'pyinstaller --onefile {file}', shell=True, check=True)

    FILE_EXE = file.replace('.py', '.exe')
    FILE_SPEC = file.replace('.py', '.spec')
    shutil.move(f'./dist/{FILE_EXE}', f'./{FILE_EXE}')
    os.remove(FILE_SPEC)

shutil.rmtree('build')
shutil.rmtree('dist')

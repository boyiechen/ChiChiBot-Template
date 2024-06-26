"""remove all files in ./app/static/tmp/ directory"""

import os
import shutil

def clean_up_tmp():
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'tmp')
    for file in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def clean_up_uploads():
    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'uploads')
    for file in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    clean_up_tmp()
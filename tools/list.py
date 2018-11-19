import os

IMG_DIR = "/home/lihui/Projects/ai/captcha_crack/jiyan/images"
def run():
    files = os.listdir(IMG_DIR)
    for f in files:
        if f.endswith("jpeg"):
            path = os.path.join(IMG_DIR, f)
            print(path)
            

if __name__ == '__main__':
    run()
import os.path
import stat
import time

dic_list = {"label1": [1189, 547, 1849], "label2": [597, 662, 1002], "label3": [189, 1692, 1474],
            "label4": [688, 441, 1112], "label0": [873, 924, 470]}

base_path = "/underdog/video"


def run():
    for k, v in dic_list.items():
        cnt_k = k
        for i in v:
            print(cnt_k + "_" + str(i + 685))
        #     """dir_path = os.path.join(base_path, cnt_k + "_" + str(i))
        #     is_exist = os.path.exists(dir_path)
        #     if is_exist is False:
        #         os.mkdir(dir_path, 777)"""
        #     esminiCmd = "esmini --window 60 60 800 400 --osc /home/Rupeng119_com/esmini/resources/xosc/{}.xosc --fixed_timestep 0.033 --capture_screen".format(
        #         i)
        #     os.system(esminiCmd)
        #     time.sleep(80)
        #     mp4Cmd = "ffmpeg -f image2 -framerate 30 -i screen_shot_%5d.tga -c:v libx264 -qp 0 {}.mp4".format(i)
        #     os.system(mp4Cmd)
        # break


if __name__ == '__main__':
    run()

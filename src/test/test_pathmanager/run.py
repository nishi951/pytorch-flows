from flow_utils.path_utils import ExpPathManager

if __name__ == '__main__':
    pathmanager = ExpPathManager(__file__)
    print(pathmanager)
    print(pathmanager.exp_path)
    print(pathmanager.log_dir)

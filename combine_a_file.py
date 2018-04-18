import os
import random
import string
import shutil
# for filename in os.listdir(r'/Users/wudi/Desktop/TextApi/TextApi'):
#     print filename

def run_cmd(cmd):
    try:
        import subprocess
    except ImportError:
        _, result_f, error_f = os.popen3(cmd)
    else:
        process = subprocess.Popen(cmd, shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result_f, error_f = process.stdout, process.stderr

    errors = error_f.read()
    if errors:  pass
    result_str = result_f.read().strip()
    if result_f:   result_f.close()
    if error_f:    error_f.close()

    return result_str

class file_command :
    base_directory_path = ''
    arch_directory = 'arch'
    result_directory = 'result'
    info_arr = []

    def start(self):
        arr = self.get_all_file(self.base_directory_path)
        for archive in arr:
            if '.a' in archive:
                self.get_archive_info(archive)
        for archive in self.info_arr:
            self.create_o_file(archive)
            self.generat_a_file(archive)
            shutil.rmtree(self.base_directory_path + '/' + archive)
        self.create_final_file()


    def get_all_file(self,path):
        return os.listdir(r"{}".format(path))

    def get_archive_info(self,file_name):
        file = "{}/{}".format(self.base_directory_path,file_name)

        command_result = run_cmd("lipo -info {}".format(file))
        arr = []
        if "architecture: " in command_result:
            arr = command_result.split("architecture: ")
        else:
            arr = command_result.split("are: ")

        result = arr[1]
        arr = result.split(" ")

        if len(arr) == 1:
            out_file = self.creat_file(arr[0],file_name)
            os.system("scp {} {}".format(file,out_file))
            return
        for archive in arr:
            out_file = self.creat_file(archive,file_name)
            os.system("lipo {} -thin {} -output {}".format(file,archive,out_file))

    def create_o_file(self,dir_name):
        base_path = self.base_directory_path + '/' + dir_name
        arr = self.get_all_file(base_path)
        string = "cd {}\n".format(base_path)
        for name in arr:
            if '.a' in name:
                last_name = name.rstrip('.a')
                os.system('mkdir ' + base_path + '/' + last_name)
                string = string + 'cd ' + last_name + '\n'
                string = string + "ar -x {}/{}\n".format(base_path,name)
                string = string + 'rm -f ' + base_path + '/' + name + '\n'
                string = string + 'cd ..\n'
        self.generate_shell(string)

    def generat_a_file(self,dir_name):
        base_path = self.base_directory_path + '/' + dir_name
        string = "cd {}\n".format(base_path)
        string = string + "ar rc {}/{}/lib-{}.a ".format(self.base_directory_path,self.arch_directory,dir_name)

        arr = self.get_all_file(base_path)

        for name in arr:
            path = base_path + '/' + name
            if os.path.isdir(path):
                arr1 = self.get_all_file(path)
                for name1 in arr1:
                    if '.o' in name1:
                        string = string + name + '/' + name1 + ' '

        # string = string + "libtool -static -o {}/{}/lib-{}.a *.o".format(self.base_directory_path,self.arch_directory,dir_name)

        if not self.check_file_exist(self.base_directory_path + '/' + self.arch_directory):
            os.system("mkdir {}".format(self.base_directory_path + '/' + self.arch_directory))

        self.generate_shell(string)

    def create_final_file(self):
        base_path = self.base_directory_path + '/' + self.arch_directory
        string = "cd " + base_path +'\n'

        if not self.check_file_exist(self.base_directory_path + '/' + self.result_directory):
            os.system("mkdir {}".format(self.base_directory_path + '/' + self.result_directory))

        string = string + "lipo -create *.a -output " + self.base_directory_path + '/' +self.result_directory + '/lib-all.a\n'
        self.generate_shell(string)

    def generate_shell(self,string):
        print string
        file_name = self.generate_random() + '.sh'
        with open(file_name, 'w+') as f:
            f.write(string)
        os.system("chmod +x {}".format(file_name))
        print "run shell script"
        os.system("./{}".format(file_name))
        os.system("rm -f {}".format(file_name))

    def check_file_exist(self,file):
        return os.path.exists(self.base_directory_path + '/' + file)

    def creat_file(self,archive,file_name):
        if not self.check_file_exist(archive):
            os.system("mkdir {}/{}".format(self.base_directory_path, archive))
        if archive not in self.info_arr:
            self.info_arr.append(archive)
        return "{}/{}/{}".format(self.base_directory_path, archive, file_name)

    def generate_random(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
if __name__ == '__main__':
    file = file_command()
    file.base_directory_path = "/Users/flh/Desktop/lib"

    file.start()
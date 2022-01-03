from time import sleep

import docker

client = docker.from_env()


def check_image_exist(image_tag):
    try:
        updated_tag = image_tag + ":latest"
        image_list = client.images.list()
        if len(image_list) != 0:
            for image in image_list:
                exist_tag = image.tags[0]
                if updated_tag == exist_tag:
                    return True
        return False
    except Exception as err:
        raise err


def build_image(dockerfile_path, dockerfile_name, image_tag):
    try:
        print("build executed")
        client.images.build(path=dockerfile_path, dockerfile=dockerfile_name, tag=image_tag, forcerm=True)
        return True
    except Exception as err:
        print(err)
        return False


def force_installation_dockers(image_tag_list):
    for image_dict in image_tag_list:
        if check_image_exist(image_dict["image_tag"]) is False:
            print(image_dict["image_tag"])
            while True:
                if build_image(image_dict["path"], image_dict["dockerfile"], image_dict["image_tag"]):
                    print("build successfully on {0}".format(image_dict["image_tag"]))
                    break
                else:
                    print("on_sleep")
                    sleep(45)
        else:
            print("image exist installation skipped")
            return True
    return True


def shuffledns_exec(local_client, domain_name, image_tag):
    try:
        resp = local_client.containers.run(image_tag,
                                           ["-d", domain_name,
                                            "-w", "/dev/shm/{0}".format("wordlist.txt"),
                                            "-r",
                                            "/dev/shm/resolvers.txt"],
                                           volumes={
                                               '/tmp/shuffledns_scan': {
                                                   'bind': '/dev/shm', 'mode': 'rw'}},
                                           auto_remove=True)
        print(resp)
        with open("shuffledns_"+domain_name+"_output.txt", "w") as f:
            f.write(resp.decode("utf-8"))
        return resp

    except Exception as err:
        raise err


if __name__ == '__main__':

    with open("domain_to_scan.txt", "r") as f:
        domain_list = f.readlines()

    image_tag_list = [
        {'path': '.',
         "dockerfile": "Dockerfile.shuffledns",
         'image_tag': 'shuffledns'}]

    result = force_installation_dockers(image_tag_list)
    if result:
        for domain_name in domain_list:
            shuffledns_exec(client, domain_name.strip(), "shuffledns")
            sleep(1)

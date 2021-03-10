import docker

IP = '0.0.0.0'
PORT = '5000'
img_tag = 'test-img'
container_name = 'test-container'
client = docker.from_env(timeout=86400)


def build():
    client.images.build(path="../", tag=img_tag)
    print('Container is built.')


def run():
    client.containers.run(img_tag,
                          ports={'5000/tcp': 5000, '8983/tcp': 8983},
                          name=container_name,
                          detach=True,
                          volumes={'/home/jueri/STELLA_DEV/data/': {'bind': '/data/', 'mode': 'rw'},
                                   '/home/jueri/STELLA_DEV/index/':{'bind': '/index/', 'mode': 'rw'}}
                          )
    print('Container is running.')


if __name__ == '__main__':
    build()
    run()

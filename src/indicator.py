#!/usr/bin/env python

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
import docker
import os
import signal


APPINDICATOR_ID = 'docker_indicator'
IMAGE_DIR = 'img'
IMAGE_PATH = os.path.join(
                 os.path.dirname(os.path.realpath(__file__)),
                 os.pardir,
                 IMAGE_DIR
             )


def build_menu(client):
    menu = gtk.Menu()
    for c in containers_list(client):
        menu.append(c)
    item_quit = gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def containers_list(client):
    return list(
            map(
                lambda c: render_container(c),
                client.containers.list(all=True)
                )
            )


def render_container(container):
    if container.status == 'running':
        icon_path = os.path.join(IMAGE_PATH, 'running.svg')
    else:
        icon_path = os.path.join(IMAGE_PATH, 'stopped.svg')
    img = gtk.Image()
    img.set_from_file(icon_path)
    menu_entry = gtk.ImageMenuItem(container.name)
    menu_entry.set_always_show_image(True)
    menu_entry.set_image(img)
    return menu_entry


def quit(source):
    gtk.main_quit()


def main():
    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    indicator = appindicator.Indicator.new(
            APPINDICATOR_ID,
            os.path.join(IMAGE_PATH, 'docker-gray.svg'),
            appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu(client))
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    gtk.main()


if __name__ == "__main__":
    main()

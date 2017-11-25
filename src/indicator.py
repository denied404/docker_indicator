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


class DockerIndicator:
    def __init__(self):
        self.client = docker.DockerClient(
                base_url='unix://var/run/docker.sock')
        self.indicator = appindicator.Indicator.new(
                APPINDICATOR_ID,
                os.path.join(IMAGE_PATH, 'docker-gray.svg'),
                appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu(self.client))
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        gtk.main()

    def build_menu(self, client):
        self.menu = gtk.Menu()
        for c in client.containers.list(all=True):
            self.menu.append(self.render_container(c))
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', quit)
        self.menu.append(item_quit)
        self.menu.show_all()
        return self.menu

    def container_menu(self, container):
        menu = gtk.Menu()
        item_start = gtk.MenuItem('Start')
        item_start.connect('activate', self.container_action,
                           container, 'start')
        item_stop = gtk.MenuItem('Stop')
        item_stop.connect('activate', self.container_action,
                          container, 'stop')
        menu.append(item_start)
        menu.append(item_stop)
        menu.show_all()
        return menu

    def container_action(self, _, container, action):
        if action == 'start':
            container.start()
        elif action == 'stop':
            container.stop()

    def render_container(self, container):
        if container.status == 'running':
            icon_path = os.path.join(IMAGE_PATH, 'running.svg')
        else:
            icon_path = os.path.join(IMAGE_PATH, 'stopped.svg')
        img = gtk.Image()
        img.set_from_file(icon_path)
        menu_entry = gtk.ImageMenuItem(container.name)
        menu_entry.set_always_show_image(True)
        menu_entry.set_image(img)
        menu_entry.set_submenu(self.container_menu(container))
        return menu_entry

    def quit(self, _):
        gtk.main_quit()


if __name__ == "__main__":
    docker_indicator = DockerIndicator()

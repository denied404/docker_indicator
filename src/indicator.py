#!/usr/bin/python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk as gtk, GLib as glib
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3 as appindicator
import docker
import os
import signal


APPINDICATOR_ID = 'docker_indicator'
IMAGE_DIR = 'img'
IMAGE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          os.pardir,
                          IMAGE_DIR)
DOCKER_ON_IMG = os.path.join(IMAGE_PATH, 'docker-gray.svg')
DOCKER_OFF_IMG = os.path.join(IMAGE_PATH, 'docker-gray-reverted.svg')


class DockerIndicator:
    def __init__(self):
        self.client = docker.DockerClient(
            base_url='unix://var/run/docker.sock')
        self.indicator = appindicator.Indicator.new(
            APPINDICATOR_ID,
            '',
            appindicator.IndicatorCategory.SYSTEM_SERVICES
        )
        self.refresh_indicator_icon()
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.build_menu()
        glib.timeout_add(1000, self.refresh)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        gtk.main()

    @property
    def docker_online(self):
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def containers_list(self):
        if self.docker_online:
            try:
                return self.client.containers.list(all=True)
            except Exception:
                return []
        else:
            return []

    def build_menu(self):
        self.menu = gtk.Menu()
        for c in self.containers_list():
            self.menu.append(self.render_container(c))
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', quit)
        self.menu.append(item_quit)
        self.reorder_menu_items()
        self.menu.show_all()
        self.indicator.set_menu(self.menu)

    def reorder_menu_items(self):
        container_items = [i for i in self.menu
                           if i.get_label() != 'Quit']
        quit_item = [i for i in self.menu
                     if i.get_label() == 'Quit'][0]
        for k, v in enumerate(
                sorted(container_items,
                       key=lambda c: c.get_label())):
            self.menu.reorder_child(v, k)
        self.menu.reorder_child(quit_item, len(container_items))
        self.indicator.set_menu(self.menu)

    def refresh_menu(self):
        containers = self.containers_list()

        new_containers = False
        for c in containers:
            if c.name not in [i.get_label() for i in self.menu
                              if i.get_label() != 'Quit']:
                self.menu.append(self.render_container(c))
                new_containers = True

        # As long as GtkMenu.reorder_child doesn't work on
        # rendered menu, we need to redraw it each time we
        # have a new entries to keep them in a right
        # alphabetical order
        if new_containers == 1:
            self.build_menu()

        for item in [i for i in self.menu
                     if i.get_label() != 'Quit']:
            if item.get_label() not in [c.name for c in containers]:
                self.menu.remove(item)
            else:
                item.set_image(
                    self.container_status_img(
                        self.client.containers.get(item.get_label())
                    )
                )

    def refresh_indicator_icon(self):
        if self.docker_online:
            self.indicator.set_icon(DOCKER_ON_IMG)
        else:
            self.indicator.set_icon(DOCKER_OFF_IMG)

    def refresh(self):
        self.refresh_indicator_icon()
        self.refresh_menu()
        return True

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

    def container_status_img(self, container):
        if container.status == 'running':
            icon_path = os.path.join(IMAGE_PATH, 'running.svg')
        else:
            icon_path = os.path.join(IMAGE_PATH, 'stopped.svg')
        img = gtk.Image()
        img.set_from_file(icon_path)
        return img

    def container_action(self, _, container, action):
        if action == 'start':
            container.start()
        elif action == 'stop':
            container.stop()

    def render_container(self, container):
        menu_entry = gtk.ImageMenuItem(container.name)
        menu_entry.set_always_show_image(True)
        menu_entry.set_image(self.container_status_img(container))
        menu_entry.set_submenu(self.container_menu(container))
        menu_entry.show()
        return menu_entry

    def quit(self, _):
        gtk.main_quit()


if __name__ == "__main__":
    docker_indicator = DockerIndicator()

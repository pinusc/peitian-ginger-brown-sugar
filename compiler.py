from jinja2 import Environment
import os
import shutil
import glob
import toml
from jinja2 import BaseLoader, TemplateNotFound
from os.path import join, exists, getmtime


class Loader(BaseLoader):
    def __init__(self, path):
        self.path = path

    def get_source(self, environment, template):
        path = join(self.path, template)
        if not exists(path):
            raise TemplateNotFound(template)
        mtime = getmtime(path)
        with open(path, 'r') as f:
            source = f.read()
        return source, path, lambda: mtime == getmtime(path)


class SourceBundle(object):
    def __init__(self, static_dir='static', src_dir='src', templates=None, dist_dir='dist'):
        if templates is None:
            self.templates = ['index.html']
        else:
            self.templates = templates

        self.static_dir = static_dir
        self.src_dir = src_dir
        self.dist_dir = dist_dir

    def _root(self):
        return os.path.dirname(os.path.abspath(__file__))

    def clean(self):
        if os.path.exists(self.dist_dir):
            shutil.rmtree(self.dist_dir)

    def build(self, output=None, tr_dict=None, **kwargs):
        if not os.path.exists(os.path.join(self._root(), self.dist_dir)):
            os.mkdir(os.path.join(self._root(), self.dist_dir))

        print("    --- Copying the files... ---    ")
        if self.static_dir is not None:
            static_list = glob.glob(os.path.join(self._root(), self.src_dir, self.static_dir) + "/*")
            static_list = [os.path.basename(p) for p in static_list]
            for st in static_list:
                dest = os.path.join(self._root(), self.dist_dir, st)
                src = os.path.join(self._root(), self.src_dir, self.static_dir, st)
                if os.path.exists(dest):
                    if os.path.isfile(dest):
                        os.remove(dest)
                    elif os.path.isdir(dest):
                        shutil.rmtree(dest)
                if os.path.isfile(src):
                    shutil.copy2(src, dest)
                elif os.path.isdir(src):
                    shutil.copytree(src, dest)
                # print("cp " +
                #      os.path.join(self._root(), self.dist_dir, self.static_dir, st) + "   " +
                #      os.path.join(self._root(), self.dist_dir))



        print("    --- Loading the template... ---    ")
        env = Environment(loader=Loader(os.path.join(self._root(), self.src_dir)))
        for template in self.templates:
            if output is None:
                output = template
            with open(os.path.join(self._root(), self.dist_dir, output), 'w') as f2:
                slug = env.get_template(template)
                print("    --- Rendering the template... ---    ")
                slug = slug.render(**tr_dict)
                print("    --- Writing the template... ---    ")
                f2.write(slug)
                print("    --- Template rendered! ---    ")

        return True


if __name__ == '__main__':
    print("======= Compiler log =======")
    sb = SourceBundle(templates=[
        'index.html'
    ])
    with open("general.toml", 'r') as strings_file:
        strings_toml_string = strings_file.read()
        strings_dict = toml.loads(strings_toml_string)
    print("  ===== General config read! =====  ")
    for translation in glob.glob("i18n/*"):
        print("  ===== " + translation + " read! =====  ")
        with open(translation, 'r') as tr_file:
            tr_toml_string = tr_file.read()
            tr_dict = toml.loads(tr_toml_string)
        tr_name = os.path.splitext(os.path.basename(translation))[0]
        strings_dict.update(tr_dict)
        print("  ===== Compiling " + translation + " template... =====  ")
        sb.build(output=tr_name + ".html", tr_dict=strings_dict)
        print("  ===== Compiled! =====  ")
        print("  ===== Have a nice day! =====  ")

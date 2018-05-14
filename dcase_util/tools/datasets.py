# !/usr/bin/env python
# -*- coding: utf-8 -*-
from dcase_util.ui import FancyLogger
from dcase_util.files import Package
from dcase_util.utils import get_byte_string, Path
import os
import codecs
import logging


class DatasetPacker(object):
    def __init__(self,
                 package_size_limit=None,
                 convert_md_to_html=True,
                 md_to_html_template=None,
                 package_extension='zip',
                 filename_template='{dataset_name}.{data_name}.{extension}'
                 ):
        """Constructor

        Parameters
        ----------
        package_size_limit : int
            Package size limit in bytes (uncompressed), bigger packages will be split into multiple packages.
            Default value None

        convert_md_to_html : bool
            Convert Markdown document to HTML. Original Markdown document is kept.
            Default value True

        md_to_html_template : str
            Template override for HTML document. If None given, default one is used.
            Default value None

        package_extension : str
            Package extension
            Default value 'zip'

        filename_template : str
            Template for dataset package filenames.
            Default value '{dataset_name}.{data_name}.{extension}'

        """

        self.package_size_limit = package_size_limit
        self.filename_template = filename_template

        self.convert_md_to_html = convert_md_to_html
        self.package_extension = package_extension

        if md_to_html_template is None:
            self.md_to_html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css" integrity="sha384-9gVQ4dYFwwWSjIDZnLEWnxCjeSWFphJiwGPXr1jddIhOegiu1FwO5qRGvFXOdJZ4" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js" integrity="sha384-cs/chFZiN24E4KMATLdqdvsezGxaGsi4hLGOzlXwp5UZB1LY//20VyM2taTB4QvJ" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js" integrity="sha384-uefMccjFJAIv6A+rW+L4AHf99KvxDjWSu1z9VI8SKNVmz4sk7buKt/6v9KI65qnm" crossorigin="anonymous"></script>

    <link rel="stylesheet" href="https://cdn.rawgit.com/afeld/bootstrap-toc/v1.0.0/dist/bootstrap-toc.min.css"> 
    <script src="https://cdn.rawgit.com/afeld/bootstrap-toc/v1.0.0/dist/bootstrap-toc.min.js"></script>

    <style>        
        p {
            text-align: justify;
        }
        nav[data-toggle='toc'] {
            top: 42px;
        }
        @media (max-width: 768px) {
          nav[data-toggle='toc'] {
            margin-bottom: 42px;
            position: static;
          }
          nav[data-toggle='toc'] .nav .nav {
            display: block;
          }
        }
        pre {
            padding: 1.5rem;
            background-color: #f8f9fa;
        }
    </style>
</head>
<body data-spy="scroll" data-target="#toc">
    <div class="container">
        <div class="row">                            
            <div class="col-sm-3">
                <nav id="toc" data-toggle="toc" class="sticky-top"></nav>
            </div>
            <div class="col-sm-9">
                {{content}}
            </div>
        </div>
    </div>
</body>
</html>
                """
        else:
            self.md_to_html_template = md_to_html_template

    @property
    def logger(self):
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            from dcase_util.utils import setup_logging
            setup_logging()

        return logger

    def pack(self,
             dataset_name='dcase-dataset',
             content=None,
             output_path=None,
             base_path=None,
             overwrite=False,
             verbose=True):
        """Pack dataset.

        Parameters
        ----------
        dataset_name : str
            Dataset name
            Default value 'dcase-dataset'

        content : list of dict
            List of packages to be packed. Package item dict should have format {'data_name': 'doc', 'file_list': [{'source': 'file1.txt'}]}.
            Default value None

        output_path : str
            Path to which packages are saved.
            Default value None

        base_path : str
            Base path of the data. If per item package paths are not given ('target' field), this parameter is used
            to create one from source path.
            Default value None

        overwrite : bool
            Overwrite existing packages.
            Default value False

        verbose : bool
            Show information during the packing.
            Default value True

        Returns
        -------
        nothing

        """

        if verbose:
            log = FancyLogger()
            log.section_header('Packing dataset [{dataset_name}]'.format(dataset_name=dataset_name))

        if base_path is not None and not base_path.endswith(os.path.sep):
            base_path += os.path.sep

        for group in content:
            if verbose:
                log.line('[{data_name}]'.format(data_name=group['data_name']))

            package_filename = os.path.join(output_path, self.filename_template.format(
                dataset_name=dataset_name,
                data_name=group['data_name'],
                extension=self.package_extension
            ))

            newest_source = 0
            for item in group['file_list']:
                if not os.path.exists(item['source']):
                    message = '{name}: File not found [{source_file}].'.format(
                        name=self.__class__.__name__,
                        source_file=item['source']
                    )

                    self.logger.exception(message)
                    raise IOError(message)

                if 'target' not in item:
                    item['target'] = item['source'].replace(base_path, '')

                timestamp = os.path.getmtime(item['source'])
                if newest_source < timestamp:
                    newest_source = timestamp

            # Get newest package, take care of split packages
            all_packages = Path().file_list(path=os.path.split(package_filename)[0], extensions=os.path.splitext(package_filename)[1][1:])
            newest_package = 0
            for package in all_packages:
                base_name = os.path.splitext(package)[0]
                if base_name[-1].isdigit():
                    base_name = os.path.splitext(base_name)[0]

                if base_name == os.path.splitext(package_filename)[0]:
                    timestamp = os.path.getmtime(package)
                    if newest_package < timestamp:
                        newest_package = timestamp

            if newest_package < newest_source or overwrite:
                if self.convert_md_to_html:
                    # Check for markdown content
                    new_files = []
                    for item in group['file_list']:
                        if os.path.splitext(item['source'])[-1] == '.md':
                            if not os.path.exists(os.path.splitext(item['source'])[0] + '.html') or (os.path.exists(os.path.splitext(item['source'])[0] + '.html') and os.path.getmtime(item['source']) > os.path.getmtime(os.path.splitext(item['source'])[0] + '.html')) or overwrite:

                                # Convert
                                self.convert_markdown(
                                    source_filename=item['source'],
                                    target_filename=os.path.splitext(item['source'])[0] + '.html'
                                )

                                new_files.append(
                                    {
                                        'source': os.path.splitext(item['source'])[0] + '.html',
                                        'target': os.path.splitext(item['target'])[0] + '.html'
                                    }
                                )

                    # Add new html files to the file_list
                    group['file_list'] += new_files

                # Create packages
                package = Package(
                    filename=package_filename
                )
                package_filenames = package.compress(
                    file_list=group['file_list'],
                    size_limit=self.package_size_limit
                )

                if verbose:
                    log.line('Saved', indent=2)

                    for i in package_filenames:
                        log.line(
                            '[{file}] [{size}]'.format(
                                file=i.replace(base_path, ''),
                                size=get_byte_string(os.path.getsize(i), show_bytes=False)),
                            indent=4
                        )

        if verbose:
            log.foot()

    def convert_markdown(self, source_filename, target_filename):
        """Convert markdown document to HTML document.

        Parameters
        ----------
        source_filename : str
            Markdown document filename

        target_filename : str
            HTML document filename

        Returns
        -------
        nothing

        """

        try:
            import markdown
        except ImportError:
            message = '{name}: Unable to import markdown module. You can install it with `pip install markdown`.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ImportError(message)

        try:
            import jinja2
        except ImportError:
            message = '{name}: Unable to import jinja2 module. You can install it with `pip install jinja2`.'.format(
                name=self.__class__.__name__
            )

            self.logger.exception(message)
            raise ImportError(message)

        f = codecs.open(source_filename, mode='r', encoding='utf-8')
        md_data = f.read()
        f.close()

        md = markdown.Markdown(
            extensions=[
                'extra',
                'markdown.extensions.meta'
            ],
        )

        html = md.convert(md_data)
        html = html.replace('<table>', '<table class="table table-striped table-hover table-sm">')

        if hasattr(md, 'Meta'):
            title = md.Meta['title'][0]

        else:
            title = None

        doc = jinja2.Template(self.md_to_html_template).render(
            content=html,
            title=title
        )

        f = codecs.open(target_filename, mode='w', encoding='utf-8')
        f.write(doc)
        f.close()


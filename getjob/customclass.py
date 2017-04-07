# -*- coding:utf-8 -*-


from __future__ import unicode_literals
import datetime, re,sys

from django.forms.widgets import Widget,FileInput,ClearableFileInput,Select
from django.forms.utils import flatatt
from django.forms import FileField,ImageField

from django.core.exceptions import ValidationError
from io import BytesIO

from django.utils import datetime_safe, formats, six
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy


#自定义城市列表选择部件
class SelectCityWidget(Widget):
    """
    A Widget that splits date input into two <select> boxes.
    """
    def __init__(self,attrs=None):
        super(SelectCityWidget,self).__init__()

        # provinice and city values supported by Ajax ,

        # Optional string, list, or tuple to use as empty_label
        #self.province_attrs = {'id':'province','name':'province'}
        #self.city_attrs = {'id':'city','name':'city'}
    #def __deepcopy__(self,*args):
    #   pass

    #def id_for_label(self,id_):

    def render(self,name,values,attrs=None):
        #attrs = {}
        label_for = format_html('<label for="id_city">城市:</label>')
        select_province = format_html('<select {}><option>------</option></select>',flatatt({'id':'province','name':'province'}))
        select_city = format_html('<select {}></select>',flatatt({'id':'city','name':'city'}))
        html = ''.join((label_for,select_province,select_city))
       # html.append()
        #html[1] = format_html('<select {}>---</select>',flatatt(self.city_attrs))
        #output = []
        #for field in self._parse_date_fmt():
        #    output.append(html[field])
        return html

class ImageFileInput(ClearableFileInput):
    # change text
    #initial_text = ugettext_lazy('')
    #input_text = ugettext_lazy(u'更改')

    # add <img> element
    template_with_initial = (
        '<a href="%(initial_url)s"><img src="%(initial_url)s"></img></a>'
        '%(clear_template)s<br />%(input)s'
    )


class CustomImageField(ImageField):
    def to_python(self, data):
        """
        Checks that the file-upload field data contains a valid image (GIF, JPG,
        PNG, possibly others -- whatever the Python Imaging Library supports).
        """
        f = super(CustomImageField, self).to_python(data)
        if f is None:
            return None

        from PIL import Image

        # We need to get a file object for Pillow. We might have a path or we might
        # have to read the data into memory.
        if hasattr(data, 'temporary_file_path'):
            file = data.temporary_file_path()
        else:
            if hasattr(data, 'read'):
                file = BytesIO(data.read())
            else:
                file = BytesIO(data['content'])

        try:
            # load() could spot a truncated JPEG, but it loads the entire
            # image in memory, which is a DoS vector. See #3848 and #18520.
            image = Image.open(file)
            #image.
            image.thumbnail((200,160),Image.ANTIALIAS)# 生成缩略图不起作用

            # verify() must be called immediately after the constructor.
            image.verify()
            # create thumbnail

            # Annotating so subclasses can reuse it for their own validation

            f.image = image
            # Pillow doesn't detect the MIME type of all formats. In those
            # cases, content_type will be None.
            f.content_type = Image.MIME.get(image.format)
        except Exception:
            # Pillow doesn't recognize it as an image.
            six.reraise(ValidationError, ValidationError(
                self.error_messages['invalid_image'],
                code='invalid_image',
            ), sys.exc_info()[2])
        if hasattr(f, 'seek') and callable(f.seek):
            f.seek(0)
        return f





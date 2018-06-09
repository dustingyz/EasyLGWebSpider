import time
import chardet
import json
from PIL import Image
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator

with open('./dat', 'rb') as f:
    read = f.read()
    encoding_ = chardet.detect(read)['encoding']
    loads = json.loads(read, encoding=encoding_)
    d = dict(zip([i[0] for i in loads], [i[1] for i in loads]))

image_open = Image.open('./miki.png')
coloring = np.array(image_open)
cloud = WordCloud(background_color='white',
                  font_path='C:\\Windows\\Fonts\\ARIALUNI.TTF',
                  mask=coloring)
color_func = ImageColorGenerator(coloring)
# cloud.generate_from_text(','.join(words))
cloud.generate_from_frequencies(d)
cloud.recolor(color_func=color_func)
cloud.to_file('./' + str(round(time.time())) + '.png')
# cloud.generate_from_frequencies()

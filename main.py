import discord, asyncio, os
from discord.ext import commands

import string
import random
import urllib.request
from urllib.request import urlopen
import PIL
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps
import xmltodict
import io

import requests
from io import BytesIO

class Wolfram(object):
    def __init__(self,question):

        self.appid="WYV3QY-HKX3X23R4R"
        self.query=question
        self.url=f"http://api.wolframalpha.com/v2/query?appid={self.appid}&input="
        self.image_url_array=[]
        self.img_array=[]
        self.pod_title=[]

    def download_image(self,url):
        imag=urlopen(url)
        raw = io.BytesIO(imag.read())
        im=PIL.Image.open(raw)
        im.load()
        size=im.size

        inv=im.convert('RGB')
        inv=PIL.ImageOps.invert(inv)
        imageBox=inv.getbbox()
        cropped = im.crop(imageBox)
        return cropped.convert('RGBA')
        #cropped.show()

    def url_encode(self,query):
        encoded_query=''
        for word in query:
            if word==' ':
                encoded_query=encoded_query+"%20"
            elif word=='/':
                encoded_query=encoded_query+"%2F"
            elif word=='+':
                encoded_query=encoded_query+"%2B"
            elif word=='&':
                encoded_query=encoded_query+"%26"
            elif word=='=':
                encoded_query=encoded_query+"%3D"
            else :
                encoded_query=encoded_query+word
        return encoded_query


    def text_to_img(self,text):
        try:
            fnt = ImageFont.truetype('arial.ttf', 15)
        except:
            fnt = ImageFont.load_default()
        background_color=(255,255,255)
        image = Image.new(mode = "RGB", size = (7*len(text)+4,20), color = background_color)
        draw = ImageDraw.Draw(image)
        draw.text((1,1), text, font=fnt, fill=(0,70,170))
        return image

    def response_handling(self,xml):
        doc = xmltodict.parse(xml)
        if doc["queryresult"]["@success"]=="false" or doc["queryresult"]["@error"]=="true" or doc["queryresult"]["@numpods"]=="1":
            return False
        for i in range(0,len(doc["queryresult"]["pod"])):
            n = int(doc["queryresult"]["pod"][i]["@numsubpods"])
            if (n > 1):
                #self.pod_title.append(doc["queryresult"]["pod"][i]["@title"])
                #self.image_url_array.append(doc["queryresult"]["pod"][i]["subpod"][0]["img"]["@src"])
                title = doc["queryresult"]["pod"][i]["@title"]
                self.img_array.append(self.text_to_img(title))
                for j in range(0, n) :
                    img = doc["queryresult"]["pod"][i]["subpod"][j]["img"]["@src"]
                    self.img_array.append(self.download_image(img))
            else:
                #self.pod_title.append(doc["queryresult"]["pod"][i]["@title"])
                #self.image_url_array.append(doc["queryresult"]["pod"][i]["subpod"]["img"]["@src"])
                title = doc["queryresult"]["pod"][i]["@title"]
                img = doc["queryresult"]["pod"][i]["subpod"]["img"]["@src"]
                self.img_array.append(self.text_to_img(title))
                self.img_array.append(self.download_image(img))

        return True

    def image_array_setup(self):
        #for i in range(0,len(self.pod_title)):
        #    self.img_array.append(self.text_to_img(self.pod_title[i]))
        #    self.img_array.append(self.download_image(self.image_url_array[i]))
        return self.image_processing()

    def merge_image(self,images):
        widths, heights = zip(*(i.size for i in images))
        new_width = max(widths)+20
        new_height = sum(heights)+15*len(images)
        new_im = Image.new('RGB', (new_width, new_height), color=(255,255,255))

        offset =20
        for im in images:
            x = 10
            new_im.paste(im, (x, offset))
            offset += im.size[1]+10
        return new_im

    def image_processing(self):
        max_height=100
        temp=[]
        re=[]
        current_height=0

        for i in self.img_array:
            current_height=current_height+i.size[1]
            temp.append(i)
        try:
            re.append(self.merge_image(temp))
        except ValueError:
            pass
        return re

    def output(self):
        query=self.url_encode(self.query)
        xml=urlopen(self.url+query).read()
        #print ("processing...")
        result_check=self.response_handling(xml)

        if(result_check):
            #a=self.image_array_setup()
            a = self.image_processing()
            return (True,a)
        else :
            return(False,"a")

game = discord.Game("Wolframalpha")
bot = commands.Bot(command_prefix='!', status=discord.Status.online, activity=game)
token = 'OTgyNTc4NTIwOTY0MzQxNzkx.GWtY8l.z7BFGscF6MJgRUn1PTRbdp85SRJWJZyDqjQ7-w'

@bot.command(aliases=['wolf'])
async def hello(ctx, *, txt):
    a='';
    if __name__=="__main__":
        a=Wolfram(txt)
        await ctx.send('processing...')
        a=a.output()[1]

    if not isinstance(a, str):
        a=a[0]
        with BytesIO() as image_binary:
            a.save(image_binary, "png")
            image_binary.seek(0)
            # make random string <name>
            name = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(8))
            name = name + '.png'
            out = discord.File(fp=image_binary, filename=name)
            await ctx.send(file=out)
    else : await ctx.send('No result found')
# Close the bot
bot.run(token)

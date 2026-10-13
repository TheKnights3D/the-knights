import sys,subprocess,math
from PIL import Image,ImageDraw,ImageFont,ImageFilter
W,H,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
F="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f=lambda s:ImageFont.truetype(F,s)
NAVY=(11,18,40);CY=(34,211,238);FPS=30
top,bot=(250,400) if H>W else (80,80)
mid=(top+H-bot)//2
names=[("dragon","Articulated dragons"),("planter","Custom planters"),("phone-stand","Phone stands"),("miniature","Tabletop minis"),("gear","Replacement parts"),("helmet","Cosplay helmets")]
imgs=[]
for n,c in names:
    im=Image.open(f"/workspace/3d-print-site/images/{n}.jpg").convert("RGB")
    s=max(W/im.width,H/im.height)*1.15
    imgs.append((im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS),c))
def text(d,y,t,sz,col=(255,255,255),maxw=None):
    maxw=maxw or W-120
    while d.textlength(t,font=f(sz))>maxw: sz-=2
    d.text((W//2,y),t,font=f(sz),fill=col,anchor="mm",stroke_width=max(2,sz//18),stroke_fill=(0,0,0))
def bg(): return Image.new("RGB",(W,H),NAVY)
def ease(t): return min(1,t*4)
segs=[("hook",2.0)]+[("s%d"%i,1.4) for i in range(6)]+[("price",1.9),("pickup",1.5),("end",2.2)]
import os,json
if os.environ.get("SEGS"): segs=[tuple(x) for x in json.load(open(os.environ["SEGS"]))]
total=sum(d for _,d in segs)
p=subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-movflags","+faststart",out],stdin=subprocess.PIPE)
for fr in range(int(total*FPS)):
    t=fr/FPS;acc=0
    for name,dur in segs:
        if t<acc+dur: lt=(t-acc)/dur;break
        acc+=dur
    a=ease(lt)
    if name.startswith("s"):
        im,cap=imgs[int(name[1])]
        z=1+0.12*lt; cw,ch=im.width/z,im.height/z
        cx=(im.width-cw)/2*(0.6+0.8*lt*(1 if int(name[1])%2 else -1)*0.5+0.0)
        cy=(im.height-ch)/2
        cx=max(0,min(im.width-cw,cx))
        frm=im.crop((int(cx),int(cy),int(cx+cw),int(cy+ch))).resize((W,H))
        ov=Image.new("RGBA",(W,H),(0,0,0,0));od=ImageDraw.Draw(ov)
        od.rectangle((0,H-bot-260,W,H-bot+20),fill=(0,0,0,140))
        frm=Image.alpha_composite(frm.convert("RGBA"),ov).convert("RGB")
        d=ImageDraw.Draw(frm)
        text(d,H-bot-120,cap,84 if H>W else 72)
        d.text((W-40,top+20),"Example prints",font=f(30),fill=(255,255,255),anchor="ra",stroke_width=2,stroke_fill=(0,0,0))
    else:
        frm=bg();d=ImageDraw.Draw(frm)
        dy=int((1-a)*60)
        if name=="hook":
            text(d,mid-80+dy,"Need something",110);text(d,mid+60+dy,"3D printed?",120,CY)
        elif name=="price":
            d.rounded_rectangle((70,mid-260,W-70,mid+260),40,fill=(20,32,66),outline=CY,width=6)
            text(d,mid-150+dy,"$10/hour",130,CY);text(d,mid+10+dy,"$3 minimum",90);text(d,mid+140+dy,"PLA included",80)
        elif name=="pickup":
            text(d,mid-70+dy,"Free pickup",120);text(d,mid+70+dy,"in Murray, UT",100,CY)
        else:
            sz=140;tw=d.textlength("The ",font=f(sz))+d.textlength("Knights",font=f(sz))
            x=(W-tw)/2;y=mid-90+dy
            d.text((x,y),"The ",font=f(sz),fill=(255,255,255),anchor="lm")
            d.text((x+d.textlength("The ",font=f(sz)),y),"Knights",font=f(sz),fill=CY,anchor="lm")
            text(d,mid+50+dy,"3D Printing · Murray, UT",54)
            text(d,mid+170,"theknights3d.github.io/the-knights",56,maxw=W-100)
            text(d,mid+270,"Follow @theknights3d",60,CY);text(d,mid+345,"on TikTok & Instagram",50)
    p.stdin.write(frm.tobytes())
p.stdin.close();p.wait()

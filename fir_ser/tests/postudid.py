
import requests
import random
short=["bgql","wjbu","vnfg","bgql"]

udid_lists=[
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08922",
    "f55df38afe5c1242b8bc478d0182bbd0d7d01129",
    "f55df38afe5c1242b8bc478d0182bbd0d723929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d118929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "f55df38afe5c1242b8bc478d0182bbd0daed08929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "f55df38afe5c1242b8bc478d0182bbdfsdfe7d08929",
    "f55df38afe5c1242b8bc478d0182bbdfsdfe7d08929",
    "f55df38afe5c1242b8bc478d0182bbdfsdfe7d08929",
    "f55df38afe5c1242b8bc478d0182dsfsdd7d08929",
    "f55df38afe5c1242b8bc478d0182dsfsdd7d08929",
    "f55df38afe5c1242b8bc478d0182dsfsdd7d08929",
    "f55df38afe5c1242b8bc478d0182bbdsdfsadf8929",
    "f55df38afe5c1242b8bc478d01sdsdfsdd0d7d08929",
    "f55df38afe5c1242b8bc478sdfsdffsdafd7d08929",
    "f55df38afe5c1242b8bc478sdfsdffsdafd7d08929",
    "f55df38afe5c1242b8bc478sdfsdffsdafd7d08929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "f55df38afe5c1242b8bc478dsdfeasdfbbd0d7d08929",
    "f55df38afe5c1242b8bc478dfsdfseasbd0d7d08929",
    "f55df38afe5c1242b8bc478d0sdfseafsdbbd0d7d08929",
    "f55df38afe5c1242b8asdfae8ds2bbd0d7d118929",
    "f55df38afe5c1242b8bc47sfsdf2bbd0d7dd18929",
    "f55df38afe5c1242b8bc478d0182bbd0d7d0ae8929",
    "f55df38afe5c1242b8bc478d0182bbd0d7dsfe08929",
]




for udid in udid_lists:
    data='<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n\t<key>PRODUCT</key>\n\t<string>iPhone9,1</string>\n\t<key>SERIAL</key>\n\t<string>F71YD58GHG74</string>\n\t<key>UDID</key>\n\t<string>%s</string>\n\t<key>VERSION</key>\n\t<string>17E262</string>\n</dict>\n</plist>\n' %(udid)
    uri = "https://fly.harmonygames.cn/udid/%s" % (random.choice(short))
    # uri = "https://fly.harmonygames.cn/udid/%s" % ("bgql")
    req=requests.post(uri,data=data )
    print(req.status_code)
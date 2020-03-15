from django.test import TestCase

# # Create your tests here.
# import base64
# request_token='ZWZhN2MwNGMwMzg2MWVmMzA5YjUxNDlkMGU0ZWIwNDRiNTlmZWJjYzpuaW5ldmVuQHFxLmNvbQ%3D%3D=='
# print(base64.b64decode(request_token))


# import xml.etree.ElementTree as ET
# tree = ET.parse("xmlfir.xml")
# root = tree.getroot()
# print(root)
# print(root.tag)     #data
# for child in root:
#     print('========>',child.tag,child)  #
#     #========> country {'name': 'Liechtenstein'} Liechtenstein
#     for i in child:
#         print(i.tag,i.attrib,i.text)


import xml.etree.ElementTree as ET

ios_plist = ET.Element("plist", attrib={"version": "1.0"})
dict1 = ET.SubElement(ios_plist, "dict")
key1 = ET.SubElement(dict1, "key")
key1.text = 'items'
array1 = ET.SubElement(dict1, "array")
dict2 = ET.SubElement(array1, "dict")





et = ET.ElementTree(ios_plist)  # 生成文档对象
# et.write("test.xml", encoding="utf-8", xml_declaration=True)

ET.dump(ios_plist)  # 打印生成的格式

import json

import xmltodict

xjson = json.dumps(xmltodict.parse("""

<plist version="1.0"><dict>
  <key>items</key>
  <array>
    <dict>
      <key>assets</key>
      <array>
        <dict>
          <key>kind</key>
          <string>software-package</string>
          <key>url</key>
          <string><![CDATA[https://ali-fir-pro-binary.jappstore.com/52e972d2749a404028e2ab7edb04d7a7f365184d?auth_key=1583720494-0-0-3dc9d1bf4f093c53f1193614ee5f6d3e]]></string>
        </dict>
        <dict>
          <key>kind</key>
          <string>display-image</string>
          <key>needs-shine</key>
          <integer>0</integer>
          <key>url</key>
          <string><![CDATA[https://ali-fir-pro-icon.fir.im/6be40db9e2bb729db1ce0db93b8ebdba50ea8b4d?auth_key=1583720494-0-0-0212635dc7c21a3c02cd2422d0213e99]]></string>
        </dict>
        <dict>
          <key>kind</key>
          <string>full-size-image</string>
          <key>needs-shine</key>
          <true/>
          <key>url</key>
          <string><![CDATA[https://ali-fir-pro-icon.fir.im/6be40db9e2bb729db1ce0db93b8ebdba50ea8b4d?auth_key=1583720494-0-0-0212635dc7c21a3c02cd2422d0213e99]]></string>
        </dict>
      </array>
      <key>metadata</key>
      <dict>
        <key>bundle-identifier</key>
        <string>com.fengxin.im.test</string>
        <key>bundle-version</key>
        <string><![CDATA[1.1.7]]></string>
        <key>kind</key>
        <string>software</string>
        <key>title</key>
        <string><![CDATA[亲友圈发发]]></string>
      </dict>
    </dict>
  </array>
</dict>
</plist>
"""), indent=4)

# print(xjson)
# print(xjson["plist"]["dict"]["array"]["dict"])
# Fdata = xjson["plist"]["dict"]["array"]["dict"]
# odata = Fdata["array"]["dict"]






bin_url="bin_url"
img_url="img_url"
bundle_id="bundle_id"
bundle_version="bundle_version"
name="name"

ios_plist_tem="""
{
    "plist": {
        "@version": "1.0",
        "dict": {
            "key": "items",
            "array": {
                "dict": {
                    "key": [
                        "assets",
                        "metadata"
                    ],
                    "array": {
                        "dict": [
                            {
                                "key": [
                                    "kind",
                                    "url"
                                ],
                                "string": [
                                    "software-package",
                                    "%s"
                                ]
                            },
                            {
                                "key": [
                                    "kind",
                                    "needs-shine",
                                    "url"
                                ],
                                "string": [
                                    "display-image",
                                    "%s"
                                ],
                                "integer": "0"
                            },
                            {
                                "key": [
                                    "kind",
                                    "needs-shine",
                                    "url"
                                ],
                                "string": [
                                    "full-size-image",
                                    "%s"
                                ],
                                "true": null
                            }
                        ]
                    },
                    "dict": {
                        "key": [
                            "bundle-identifier",
                            "bundle-version",
                            "kind",
                            "title"
                        ],
                        "string": [
                            "%s",
                            "%s",
                            "software",
                            "%s"
                        ]
                    }
                }
            }
        }
    }
}
""" %(bin_url,img_url,img_url,bundle_id,bundle_version,name)


# print(xmltodict.unparse(json.loads(ios_plist_tem), indent=4))


tokenlist=[
    {'a':{
        'data':['1','fsdf'],
        'time':65225
    }}
]

for token in tokenlist:
    print(token)
    for k,v in token.items():
        print(k,v)
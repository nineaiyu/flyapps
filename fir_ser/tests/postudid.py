import random

import requests

udid_lists = [
    "75f14e4aee3dad37568a1a374f6c8b661b32d05e", "00008030-000C185C1143802E", "cadb0511abdb545d7eb7e828fd641a93e3164d02",
    "efa8e5eb2a58fe65e303d1d9fad99d8b8670b6bb", "2525def0a63af76b8a09ea0dce0574d720925800",
    "fdefbf544b7729db27c5294cd652e0dbb462cd22", "00008030-00122CD21A82402E", "e9f4cdc73fe24b1e20a4c33ae842d0d9ce6f8e34",
    "cd84e936355f492ee68b7182f12ce3a7d0205557", "00008101-000B05E4368B001E", "f81a3a4170cf8e6c71d525464e175049134a6dbc",
    "6bae15671c8fe7096a40752071d87c6a837dd132", "7dd77d8cf13789e3f547f28ceb3e0c67b8694e37",
    "53e663905fcd81887abffc0d92e5c116ea2bfe5c", "00008101-001325EE1188001E", "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "00008020-000951C40C12002E", "760862a7367dea986542dae17ee31cd139e454ad", "079d0e46eab5369184830d37cbed345f664e835a",
    "00008030-000E6CC122D2402E", "00008101-0012758822A2001E", "00008020-00192CDE3A41002E",
    "e2bcc2bdf73bf815bfde88becdeee05abdebf4d1", "000f0a85cf2d0b65b7a1fa21f143516500e040e0",
    "6dd86c12ab5506a1f7e45b0f58b6b1448f5cdf54", "49d8ca930a5610ba00190565ef756e24af97e63c",
    "ad4016d3749277b58f6294a9496ad97fa7c88110", "6a245252fb9cca583fc84413a092e73f7afc3182",
    "28f756d951c07d9073d5c62e66b2f9623bfcc1b4", "54d5c3d340912606f3502bd57196700daa23e8a0",
    "7b12d1a745468afe0e2ba63fa8962e99a0b75b7c", "8d7fed0e9adc3c9ea269a447a4b171b1ea38e205", "00008101-001A115C0110001E",
    "4d83d479308de7cb50f91679edf11e4f0017ac40", "00008020-001A75480E46002E", "d0746191f9a8e3f8ccbdbbf421fe4af43f2bd431",
    "00008030-001949CC34DA402E", "00008030-000509D41A08802E", "00008020-0002344A0279002E",
    "0f88c091dba1f606290cd4e2c2385a03ed6433f3", "00008030-00187410112A802E", "2a3b78c5559e956dc499c78fe7bb2730789085d4",
    "1e574d63210a2c4ca50c403525c5b47ad446ade0", "00008101-001259E93A81001E", "00008020-00046DD03A69002E",
    "17db32cab3c04e699189c49867833a7ab98bd7f1", "00008020-001E21C60A51002E", "00008030-00162D010A33802E",
    "00008101-001661290169001E", "00008020-001B78E93461002E", "a84919cf236558b0f83496302237fd7f62a212a7",
    "00008101-0008093E3611001E", "00008110-00162C9A3C82801E", "638525bfd0ef1f029ed4c216f1430688093e5ac5",
    "00008030-000A51AE0EFA402E", "00008110-0016082C1E32801E", "00008030-001828411163802E",
    "20737b4d60c2e0ff34e32edde224e64d042f72c1", "41d1b77e3a831f82a0ca306beaceeb955280b57a"
]

udid_lists2 = [
    "00008020-000909C00CE8402E",
    "e7058122cffa6a1705ea7144f208159e793a0f99",
    "00008020-00192CDE3A41002E",
    "00008101-001614893A42001E",
    "00008101-001449580100001E",
    "00008101-0012758822A2001E",
    "019e2418ebf7bebbe82b42e4255b06f60f43fdda",
    "d3c7d88e66bb84b5b1b03fc70a12b568118464da",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929"
]

short_list = [
    "wgvn",
    "ynei",
    "mecg",
    "plzd",
    "ibhp",
    "zpus",
    "ucwk"
]


def postudid(short=short_list[0], udid=udid_lists[0]):
    data = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n\t<key>PRODUCT</key>\n\t<string>iPhone9,1</string>\n\t<key>SERIAL</key>\n\t<string>F71YD58GHG74</string>\n\t<key>UDID</key>\n\t<string>%s</string>\n\t<key>VERSION</key>\n\t<string>17E262</string>\n</dict>\n</plist>\n' % (
        udid)
    uri = "https://app.hehelucky.cn/udid/%s" % (short)
    req = requests.post(uri, data=data)
    print(req.status_code, req.text)


from concurrent.futures import ThreadPoolExecutor

# postudid(udid="f55df38afe5c1242b8bc478d0182bbd0d7d08929")
# exit()

if __name__ == '__main__':
    for udid in udid_lists:
        with ThreadPoolExecutor(max_workers=10) as executor:
            future = executor.submit(postudid, random.choice(short_list), udid)

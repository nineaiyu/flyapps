import random
import time

import requests

udid_lists = [
    "75f14e4aee3dad37568a1a374f6c8b661b32d05e", "00008030-000C185C1143802E",
    "efa8e5eb2a58fe65e303d1d9fad99d8b8670b6bb", "e9f4cdc73fe24b1e20a4c33ae842d0d9ce6f8e34",
    "cd84e936355f492ee68b7182f12ce3a7d0205557", "00008101-000B05E4368B001E", "f81a3a4170cf8e6c71d525464e175049134a6dbc",
    "6bae15671c8fe7096a40752071d87c6a837dd132", "7dd77d8cf13789e3f547f28ceb3e0c67b8694e37",
    "53e663905fcd81887abffc0d92e5c116ea2bfe5c", "00008101-001325EE1188001E", "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "00008020-000951C40C12002E", "760862a7367dea986542dae17ee31cd139e454ad", "079d0e46eab5369184830d37cbed345f664e835a",
    "00008030-000E6CC122D2402E", "00008020-00192CDE3A41002E",
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

]

udid_lists2 = [
    "00008020-000909C00CE8402E",
    "e7058122cffa6a1705ea7144f208159e793a0f99",
    "00008020-00192CDE3A41002E",
    "00008101-001614893A42001E",
    "00008101-001449580100001E",
    "019e2418ebf7bebbe82b42e4255b06f60f43fdda",
    "d3c7d88e66bb84b5b1b03fc70a12b568118464da",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929"
]

short_list = [
    "tiok",
    "semi",
    "lify",
    "nyvr",
    "uwdy",
    "ceuj",
    "bqpi"
]


def postudid(short=short_list[0], udid=udid_lists[0]):
    data = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n<plist version="1.0">\n<dict>\n\t<key>PRODUCT</key>\n\t<string>iPhone9,1</string>\n\t<key>SERIAL</key>\n\t<string>F71YD58GHG74</string>\n\t<key>UDID</key>\n\t<string>%s</string>\n\t<key>VERSION</key>\n\t<string>17E262</string>\n</dict>\n</plist>\n' % (
        udid)
    uri = f"https://app.hehelucky.cn/api/v1/fir/xsign/udid/{short}"
    req = requests.post(uri, data=data)
    print(req.status_code, req.text)


from concurrent.futures import ThreadPoolExecutor

# postudid(udid="f55df38afe5c1242b8bc478d0182bbd0d7d08929")
# exit()
# import oss2

# tokens = {
#     "access_key_id": "STS.NUrQfSoT1hxZt953jpkzpAxrD",
#     "access_key_secret": "3DYz3ZVLCYaCF7mU7BT5DPdRDmCqpW1sFUwr2T6obt3X",
#     "bucket": "fly001-storage",
#     "endpoint": "oss-cn-beijing.aliyuncs.com",
#     "expiration": 1636451222,
#     "request_id": "E792C7D3-051E-5D77-8439-5F596F525827",
#     "security_token": "CAISpAN1q6Ft5B2yfSjIr5bHGtzngosQ37qxdh+E12olZ/Vcrr3Zpjz2IHxKfHJtBukfs/synWtY7P4elpUoRsBMGhbINccstZoKoAqoM9Gb6pPp4OwP2c2vSTSeUEGq1ZTYPL2nEIqBI670ZluUnyQoh6P8enO+WkT9hDVoQCYgPLotRQCdQWdsq740T1IQAaZ4WFLVMfGySDeI5kPbEEtvvCdllGp78t7R68aA6x3Y/hyYr+gOvNbJP4SDZcthN4sdI9Cux75ffK3bzAtN7wRL7K5skJFc/TDOsquAYT9r7g6BLvDf//B2MQZ9fdJaIaNfq+XmnvAKi47sno/smRFWJrMXAWaNSoSxmJOdXfi1Mcwweru8YHmS24/VOsH571gqPCMSPVMRIYt+dnIgAk18QGGGJ/T4qVmRaFj7FfTcjPhviJd+n1zjppySIVfJX7CB815BYcNlNxxyZ0JHhTOwLf9eSWEWLQM7XYTyZJ5ocRVTpZnvuQDvTSB6xhlVxaaiOauN5/9GMNigA8sdgdBFOI4lvW87Ck/rTKinhUoE+J+r/3PICMMagAGS1Fzpp9+iSHjA8FQ0GKWeLqGIewHIijtDrjVAlXMikLPUiFJfZB9b0bO/9fUuFj8cmVEwF3uGsMfuaAorJ8oQzRkeVz87B67W391gwlx92P1KRtppvUxv0ic7lJI6nlp0Spd4hhpe3m80KYKG1LpVl7ZJBg2f+4CJ71yJsVmlQg=="
# }
#
# auth = oss2.StsAuth(tokens.get('access_key_id'), tokens.get('access_key_secret'), tokens.get('security_token'))
# bucket_get = oss2.Bucket(auth, tokens.get('endpoint'), tokens.get('bucket'))
# bucket_get.copy_object(tokens.get('bucket'), '3e7a72d0d43f59aa832974e8c98b84e3a0b305fc2d7a11ec96de.jpg', 'xxxx.jpg')
# res = bucket_get
# print(res)
# exit(1)

udid_test_s = [
    "f81a3a4170cf8e6c71d525464e175049134a6dbc",
    "6bae15671c8fe7096a40752071d87c6a837dd132",
    "7dd77d8cf13789e3f547f28ceb3e0c67b8694e37",
    "53e663905fcd81887abffc0d92e5c116ea2bfe5c",
    "00008101-001325EE1188001E",
    "f55df38afe5c1242b8bc478d0182bbd0d7d08929",
    "00008020-000951C40C12002E",
    "760862a7367dea986542dae17ee31cd139e454ad",
    "079d0e46eab5369184830d37cbed345f664e835a",
    "00008030-000E6CC122D2402E"
]

postudid(udid="41d1b77e3a831f82a0ca306beaceeb955280b57a", short='vcdp')
exit()


def call_function_try_attempts(try_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(try_attempts):
                print('111111111111111111111111111111111111111111111111', _)
                res = func(*args, **kwargs)
                status, result = res
                if status:
                    return res
                time.sleep(1)
            return res

        return wrapper

    return decorator


# @call_function_try_attempts()
# def aaaa(x,y):
#     if random.randrange(1,10) == sum([x,y]):
#         return True,True
#     return False,False
#
# print(aaaa(4,2))


if __name__ == '__main__':
    for i in range(9):
        for udid in udid_test_s:
            with ThreadPoolExecutor(max_workers=20) as executor:
                future = executor.submit(postudid, random.choice(short_list), udid)

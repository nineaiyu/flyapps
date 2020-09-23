<template>
    <div id="download" ref="download">
        <router-view></router-view>
    </div>
</template>

<script>

    export default {
        name: 'download',
        data() {
            return {}
        },
    }
</script>

<style>
    body {
        background-color: rgba(0, 166, 224, 0.18)
    }

    @font-face {
        font-family: "iconfont";
        src: url('./assets/icon/iconfont.eot?t=1583637102320'); /* IE9 */
        src: url('./assets/icon/iconfont.eot?t=1583637102320#iefix') format('embedded-opentype'), /* IE6-IE8 */ url('data:application/x-font-woff2;charset=utf-8;base64,d09GMgABAAAAAAnUAAsAAAAAEXwAAAmIAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHEIGVgCEIAqUYJBKATYCJAMoCxYABCAFhG0HdhuGDlGUL1aT7CuMW3giIDU2lBZVYzMmA6BYbBoB4AIAvsWyNCR1ZYRAPDyt/e/cmdn1b4KYdG+eSCaJRMWjWPVE6ZTyQkZL4P/W2j938EFdZvf2bG4F1UgXqyQeKfBIqpGQb4i2eQ/W/4P6Ek9oYwayNWYT2liwtS7KBWzNL+pBXQarNpcN/6uINB8EdIMjCcASCSSx4cAb7oGJPvjzf6maMe0OLEmbbAtQ1TLH+t2bjwpcoLGH1RZY9/OCWElqEp69Ctt/lUoZgKMJ9DZKJTpb39oLSoVQBWoeMPQUKGtmZQQOra7u2bKID6DSppeMC3hP7x//HA0lSZWJNS/fr5uFyp+QiaT/uZpYwYv1OWFuR8Z+oBDfe93f5Fy5n9R9H1g8BBYZNWVZ128wWubBX4gsc00C/+npXSCHRbkuqBVJ6GSNo/zjETVVPQL/ONPxMyIeNT9HHoWfyzwSPzeo8DQ7IF5OsxdGGZpzMGqgeQOjCpoJxHejmz7ZYhE4AvIjgLIWhPY8ORu1xKf7mSXfEqJWz1lFqu4IsUVclojNFtvZeZZJWCxfTwc225MLw+IOJVu9jIhlZydks0WD2YzVCGJDzZv3bRWtVSPgFM6ZTJDKjCPGrSIdax2dlWgymUleOEnitJKXpPyEKz9ri1IZTMalepIwQ/od1OvB5hq3QpDBcnCLkASgX+Ot37xvI9/Ep9QGC7EF1DMQNJgws3VoBmqIDgCbNXYuVd01lKFvR5CqnITxPpi1Z23gbKCzVCYzT3meaFLvhr5kmfWJDrV+iz8KDo/ogiAUbGoo8SKbLBDTGVnfLmB0BpiGzuEVMxCPpJitnaqi7QPc/I2nEGN6Yb7eUj2voN2qcKHuJxEIVUb7HLspkHcwNKgtsk9XrLzLL2qnl/syr6WbOyffau0FeKUntEq8bGeo+bLsHFVv2IggXAm3BxcRKD4qQJAKpPFED97cegA2kUtJkufhEa5hguf0l6KbAjfRsqUoyisV/sajng+9Tg8sp/2sVPRImnYco2IPWCUbqfgT1lSrrW/7VfTgedn+s9KD1yN30pCRKrXQnuutQZutHvvpsYD3WcPOT9ADl+8K2mVNPnAp9cSF3FNUNnVr4DitOXmXd5BOI2x9VwM0UXRJJ6U6MWENSmG19tlu9tF0g83WkJw35hw1brVGEXTtxk4RtKzrdEcwaG7N+s0ANrPfcth3vHWoM7SOzosxLcPNKMmLbqN7xpoDCR7Zwo26aAOV2mziKs4ZG1WmpTzlGUXJPpWdjSaDmSD1S9EsUryx0/OqplwYy9vjrrPyxLZUyHbAlg4UBYchLJdPRqKr5WY1GnenBYElwhrjZsE0UWXitVtXau4B6TbsEETKTYgqW7ca11skHotAqCLSqu8TzTldome82Wsp5a2lPn03qYZV0HrRfaYtuR2xJ6W3pQhPi8Xyezqa3c8TyNnMNv1zOy+QUBFrb8+Yo3hUiDsBt4OTRPQOeXLy11deWJbq1+OgVrJp8JITpcISj+p5aa9SJ5TKi/o2VKD37G/xu1ERehnQt/bKk+LfZZ2Li48XXAy/KLjDXTbqabKD0+DFjk5YidPrAw8b+ADh3wm7wHd0BAD7RC6YL3I63Np/w+1uHZyLbhdOOgWY4JsQi8aE33JgNDJJFCsKnToP+Ain5hLZJ+oMIeJY0aRZzy41NiRiiRkNlwIzZVR8UKZ6gjrOx1Oy55plBcn64P+UtFEhJJwsTRaRKlKkLQ6TIVFajgW4FybDoZ1loaLkI+ACamn7vt5/X1BiF1y1/8m85UFdNdyaAG6A7phsAKgEUNljkEgZGhJqDY7/TQBeHCUBQ7bM3HwgbX2hUHhqbn3VDsIVYcAoomY1TISKHcKariNO2PbaZgyX5N6oC/OHfNjxXzabV+91hR2d90zbk6bWotfUxzuvZ/mWE2AIgaUsOMde5snf/NxBElNVPnB045As1kLdjhRM0wCJH8X384+4FiQpzJ3tlufDTZydm1/k+xI80DKzs7INNcWemo9FflMbU70a5MXSzpiaiJeyfPP74Jjso8dKNQbLzDuiJKZjVebQuSV4UtxHuc94mSgx1kfuDXSn54cWlI/IC901zzN/UFheSAz85UPeQ4W6cPeJ5Z7Qz3V1Yf4DxUwcjVMOHNy/Z7VCcnVNu+RhrCZm2Pgc/PekHiDmSxhpaVX/Zpb3ybTr7gmq/SQPHuhYh85ZyzAgS9bhdbCcmeKbiAdODfLT8OYfiitWlDYqpvArls3WTlgMAt2/dHlh2PKgTf9C3xZ6SfMPf4H/e/DeeBU9YTHXud+QEcczVOuLHD+8pR7Q4ItaA4rCDaqSE1PLB/c/6xOQwt8fF5DmMMYhIFW6P8A/ZWWSDlR+AvKkAZJcuA2ThltOqtHilt0hhX74CCiuz12fJrwJOm/kar23PmgzaH21LlvtP7SQMKjJ4X3Ge4emTB16l/FuniAh5KR716vKe+sOOlsSWpJUK/6+4R1UkQDelaH4e4fnCqZB8Dwv3HAbkMo7II0h+zH2kPQAT7diZzA60R6o3IB2E8hUwxCdENuicNkw3pQ1YR3AhGA9UOqmhVWC7/HngiboCBZbg4KDzga9uu/nfkayyrXNtb5N0LO3U5vStQ1TJl+Jq2M/00nrlp1baILFTn7eSQjGzoIaSRi7V5FYhGUuwcaARMOYt59wXsE8J7+YWJonyFWLkc/AlG4gigJdJjGTQJ1iCbNXk56FOQWmJZOoT+UzxdQWBqaOatItGSBI3E3MxD40KfmrXQpS5vyRCZc+X53Qn98Zz0aZ+yj0f0oB601pJcIT/LFKmMNKINMsffEGFomXauqjNqtKllBO4+/UP+993doltuQfXLtU0pPGBnrW2o4u+P30yuA4vdY6Qe/t07D9YAFHIkqHvfYUeph1RU+m/aBns24EEAD/Rq8s+xcelTUkEMB7JTjY42BnMOokDk8JeBZNLyFmhvio0Caos9puTM95priqjCj9mOOZGMpKz2zmGrAPc+tYh5+nswWBQhRHvKheOR72eAjyc8SFZ4R0pyD4izMyqL5102eIF9TO4GBThIR9FjJtiZ8xg/ChkAXq1tt3w2hzPKZwI736/P0wDo+ZPZIlXSYD3aD2sXrdF5A3j5ZNUJ0UFHXkEF5IverEPDJNIP7+xVywGYJ0ziWSfsUy1NEorjp9+1rvrS37se5DXLePFDlKVFFHE2100cegueWb5QgzqyRdljFPtoQhvCSjo0cKVVaMkK2o4rlyAAA=') format('woff2'),
        url('./assets/icon/iconfont.woff?t=1583637102320') format('woff'),
        url('./assets/icon/iconfont.ttf?t=1583637102320') format('truetype'), /* chrome, firefox, opera, Safari, Android, iOS 4.2+ */ url('./assets/icon/iconfont.svg?t=1583637102320#iconfont') format('svg'); /* iOS 4.1- */
    }

    .iconfont {
        font-family: "iconfont" !important;
        font-size: 16px;
        font-style: normal;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    .icon-android:before {
        content: "\e61d";
    }

    .icon-android1:before {
        content: "\e616";
    }

    .icon-android2:before {
        content: "\e62a";
    }

    .icon-ios:before {
        content: "\e60c";
    }

    .icon-IOS:before {
        content: "\e68c";
    }

    .icon-ios1:before {
        content: "\e601";
    }

    .icon-ios2:before {
        content: "\e64b";
    }

    .icon-Android:before {
        content: "\e6d4";
    }

    .icon-android3:before {
        content: "\e625";
    }


</style>

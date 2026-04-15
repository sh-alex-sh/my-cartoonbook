申请API密钥之后，需要在每次请求API接口的查询字符串中固定传递以下参数：
参数
类型
是否必需
说明
AccessKey
String
是
开通开放平台授权的访问AccessKey
Signature
String
是
加密请求参数生成的签名，签名公式见下节“生成签名”
Timestamp
String
是
生成签名时的毫秒时间戳，整数字符串，有效期5分钟
SignatureNonce
String
是
生成签名时的随机字符串
如请求地址：https://test.xxx.com/api/genImg?AccessKey=KIQMFXjHaobx7wqo9XvYKA&Signature=test1232132&Timestamp=1725458584000&SignatureNonce=random1232
2.4.2 生成签名
签名生成公式如下：
# 1. 用"&"拼接参数
# URL地址：以上方请求地址为例，为“/api/genImg”
# 毫秒时间戳：即上节“使用密钥”中要传递的“Timestamp”
# 随机字符串：即上节“使用密钥”中要传递的“SignatureNonce”
原文 = URL地址 + "&" + 毫秒时间戳 + "&" + 随机字符串
# 2. 用SecretKey加密原文，使用hmacsha1算法
密文 = hmacSha1(原文, SecretKey)
# 3. 生成url安全的base64签名
# 注：base64编码时不要补全位数
签名 = encodeBase64URLSafeString(密文)
Java生成签名示例，以访问上方“使用密钥”的请求地址为例：
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import org.apache.commons.codec.binary.Base64;
import org.apache.commons.lang3.RandomStringUtils;

public class SignUtil {

    /**
     * 生成请求签名
     * 其中相关变量均为示例，请替换为您的实际数据
     */
    public static String makeSign() {

        // API访问密钥
        String secretKey = "KppKsn7ezZxhi6lIDjbo7YyVYzanSu2d";
        
        // 请求API接口的uri地址
        String uri = "/api/generate/webui/text2img";
        // 当前毫秒时间戳
        Long timestamp = System.currentTimeMillis();
        // 随机字符串
        String signatureNonce = RandomStringUtils.randomAlphanumeric(10);
        // 拼接请求数据
        String content = uri + "&" + timestamp + "&" + signatureNonce;
    
        try {
            // 生成签名
            SecretKeySpec secret = new SecretKeySpec(secretKey.getBytes(), "HmacSHA1");
            Mac mac = Mac.getInstance("HmacSHA1");
            mac.init(secret);
            return Base64.encodeBase64URLSafeString(mac.doFinal(content.getBytes()));
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("no such algorithm");
        } catch (InvalidKeyException e) {
            throw new RuntimeException(e);
        }
    }
}
Python生成签名示例，以访问上方“使用密钥”的请求地址为例：
import hmac
from hashlib import sha1
import base64
import time
import uuid

def make_sign():
    """
    生成签名
    """

    # API访问密钥
    secret_key = 'KppKsn7ezZxhi6lIDjbo7YyVYzanSu2d'

    # 请求API接口的uri地址
    uri = "/api/genImg"
    # 当前毫秒时间戳
    timestamp = str(int(time.time() * 1000))
    # 随机字符串
    signature_nonce= str(uuid.uuid4())
    # 拼接请求数据
    content = '&'.join((uri, timestamp, signature_nonce))
    
    # 生成签名
    digest = hmac.new(secret_key.encode(), content.encode(), sha1).digest()
    # 移除为了补全base64位数而填充的尾部等号
    sign = base64.urlsafe_b64encode(digest).rstrip(b'=').decode()
    return sign

NodeJs 生成签名示例，以访问上方“使用密钥”的请求地址为例：
const hmacsha1 = require("hmacsha1");
const randomString = require("string-random");
// 生成签名
const urlSignature = (url) => {
  if (!url) return;
  const timestamp = Date.now(); // 当前时间戳
  const signatureNonce = randomString(16); // 随机字符串，你可以任意设置，这个没有要求
  // 原文 = URl地址 + "&" + 毫秒时间戳 + "&" + 随机字符串
  const str = `${url}&${timestamp}&${signatureNonce}`;
  const secretKey = "官网上的 SecretKey "; // 下单后在官网中，找到自己的 SecretKey'
  const hash = hmacsha1(secretKey, str);
  // 最后一步： encodeBase64URLSafeString(密文)
  // 这一步很重要，生成安全字符串。java、Python 以外的语言，可以参考这个 JS 的处理
  let signature = hash
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
  return {
    signature,
    timestamp,
    signatureNonce,
  };
};
// 例子：原本查询生图进度接口是 https://openapi.liblibai.cloud/api/generate/webui/status
// 加密后，url 就变更为 https://openapi.liblibai.cloud/api/generate/webui/status?AccessKey={YOUR_ACCESS_KEY}&Signature={签名}&Timestamp={时间戳}&SignatureNonce={随机字符串}
const getUrl = () => {
  const url = "/api/generate/webui/status";
  const { signature, timestamp, signatureNonce } = urlSignature(url);
  const accessKey = "替换自己的 AccessKey"; // '下单后在官网中，找到自己的 AccessKey'
  return `${url}?AccessKey=${accessKey}&Signature=${signature}&Timestamp=${timestamp}&SignatureNonce=${signatureNonce}`;
};
星流Star-3 Alpha文生图​
￼
•
接口：POST /api/generate/webui/text2img/ultra​
•
headers：​
​
header​
value​
备注​
Content-Type​
application/json​
​
￼
￼
￼
​
￼
•
请求body：​
​
参数​
类型​
是否必需​
说明​
备注​
templateUuid​
string​
是​
•
星流Star-3 Alpha文生图：5d7e67009b344550bc1aa6ccbfa1d7f4​
​
generateParams​
object​
是​
生图参数，json结构​
参数中的图片字段需提供可访问的完整图片地址​
￼
￼
￼
​
￼
•
返回值：​
​
参数​
类型​
备注​
generateUuid​
string​
生图任务uuid，使用该uuid查询生图进度​
￼
￼
￼
​
￼
•
参数说明​
​
变量名​
格式​
备注​
数值范围​
必填​
示例​
prompt​
​
string​
正向提示词，文本​
•
不超过2000字符​
•
纯英文文本​
是​
​
代码块​
JSON
￼
复制
￼
​
​
aspectRatio​
string​
图片宽高比预设​
，与imageSize二选一配置即可​
1.
square：​
◦
宽高比：1:1，通用​
◦
具体尺寸：1024*1024​
2.
portrait：​
a.
宽高比：3:4，适合人物肖像​
b.
具体尺寸：768*1024​
3.
landscape：​
a.
宽高比：16:9，适合影视画幅​
b.
具体尺寸：1280*720​
二选一配置​
​
imageSize​
Object​
图片具体宽高，与aspectRatio二选一配置即可​
1.
width：int，512~2048​
2.
height：int，512~2048​
imgCount​
int​
单次生图张数​
1 ~ 4​
是​
controlnet​
Object​
构图控制​
1.
controlType：​
a.
line：线稿轮廓​
b.
depth：空间关系​
c.
pose：人物姿态​
d.
IPAdapter：风格迁移​
2.
controlImage：参考图可公网访问的完整URL​
否​
￼
￼
￼
​
3.1.2
星流Star-3 Alpha图生图​
￼
•
接口：POST /api/generate/webui/img2img/ultra​
•
headers：​
​
header​
value​
备注​
Content-Type​
application/json​
​
￼
￼
￼
​
￼
•
请求body：​
​
参数​
类型​
是否必需​
说明​
备注​
templateUUID​
string​
是​
•
星流Star-3 Alpha图生图：07e00af4fc464c7ab55ff906f8acf1b7​
​
generateParams​
object​
是​
生图参数，json结构​
参数中的图片字段需提供可访问的完整图片地址​
￼
￼
￼
​
￼
•
返回值：​
​
参数​
类型​
备注​
generateUuid​
string​
生图任务uuid，使用该uuid查询生图进度​
￼
￼
￼
​
￼
•
参数说明​
​
变量名​
格式​
备注​
数值范围​
必填​
示例​
prompt​
​
string​
正向提示词，文本​
•
不超过2000字符​
•
纯英文文本​
是​
​
​
￼
​
代码块​
JSON
￼
复制
￼
​
￼
￼
￼
​
sourceImage​
string​
参考图URL​
参考图可公网访问的完整URL​
是​
imgCount​
int​
单次生图张数​
1 ~ 4​
是​
controlnet​
Object​
构图控制​
1.
controlType：​
a.
line：线稿轮廓​
b.
depth：空间关系​
c.
pose：人物姿态​
d.
IPAdapter：风格迁移​
2.
controlImage：参考图可公网访问的完整URL​
否​
￼
￼
￼
​
￼
​
￼
￼
​
代码块​
JSON
￼
复制
￼
​
￼
￼
￼
​
￼
星流Star-3 Alpha图生图 - 简易版本​
￼
​
￼
￼
​
代码块​
JSON
￼
复制
￼
4        "prompt": "In the center of the picture, there is an unfolding old book with yellow pages and curled edges. The spine of the book is wrapped with luminous blue energy. A quill pen is inserted obliquely from the page. The ink dripping from the tip of the pen condenses in the air into a star orbit, extending to the broken space-time fragments floating in the distance. The background is a deep starry sky, in which there are gear-shaped hourglass devices floating and translucent purple nebulls rotating slowly between gears, there is a translucent magic circle outline on the left side of the close view, and frozen butterfly specimens and burning feathers are scattered on the right side. The ground is covered with shredded and reorganized fragments of the book page. The word \"Time\" in different fonts looms on each fragments. The shadow cast by the quill pen forms a luminous Latin poem on the page. Above the book floats a phoenix outline outlined by light points, and its tail feathers are composed of flowing words, the digital illustration style is adopted as a whole. The main colors are indigo and gilt. The light and shadow are concentrated at the junction of books and quill pens, creating a fantastic feeling of knowledge and magic. The picture is used for the main visual poster of the activity. The title text is inlaid on the top of the book with three-dimensional gilded fonts. The letters have special effects of stardust particles on the edges,",​
5        "promptMagic": 1,​
6        "imgCount": 1,​
7        "steps":30,​
8        "denoisingStrength":0.5,​
9        "sourceImage": "https://liblibai-online.liblib.cloud/img/081e9f07d9bd4c2ba090efde163518f9/b3bc151da17b2b99da11190b40734ca4eb10104b294963ca24919923da4208b8.png", ​
10        // 高级设置，可不填写​
11        
"controlnet":{​
12            "controlType":"IPAdapter",​
13            "controlImage": "https://liblibai-online.liblib.cloud/img/081e9f07d9bd4c2ba090efde163518f9/bf3ce70bf40d578317855bda64b0393c76c41599c856dabceaab41db1f6f8641.png",​
14        }                   ​
15    }​
16}​
​
￼
￼
￼
​
￼
F.1 - 主体参考参数示例（仅支持文生图）​
￼
•
接口：POST /api/generate/webui/text2img/ultra​
​
￼
代码块​
JSON
￼
复制
￼
1
￼ 
{​
2    "templateUuid":"5d7e67009b344550bc1aa6ccbfa1d7f4",​
3
￼    
"generateParams":{​
4        "prompt": "A fluffy cat lounges on a plush cushion.",​
5        "promptMagic": 1,​
6        "aspectRatio":"square",​
7        "imgCount":1 ,​
8​
9
￼        
"controlnet":{​
10            "controlType":"subject",​
11            "controlImage": "https://liblibai-online.liblib.cloud/img/081e9f07d9bd4c2ba090efde163518f9/3c65a38d7df2589c4bf834740385192128cf035c7c779ae2bbbc354bf0efcfcb.png",​
12        }        ​
13    }
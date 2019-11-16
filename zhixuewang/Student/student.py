from . import exam, person
from .models.urlModel import INFO_URL, CHANGE_PASSWORD_URL
from ..models.personModel import classModel, birthdayModel, schoolModel
from ..models.userModel import User


class Student(User):
    def __init__(self, session):
        User.__init__(self, session)
        self._xtoken = ""
        self.role = "student"

    def change_password(self, old_password: str, new_password: str) -> str:
        """
        修改智学网密码
        :param old_password: 旧密码
        :param new_password: 新密码
        :return:
        """
        import execjs
        zxt = execjs.compile(
            """var RSAUtils={};var biRadixBase=2;var biRadixBits=16;var bitsPerDigit=biRadixBits;var biRadix=1<<16;var biHalfRadix=biRadix>>>1;var biRadixSquared=biRadix*biRadix;var maxDigitVal=biRadix-1;var maxInteger=9999999999999998;var maxDigits;var ZERO_ARRAY;var bigZero,bigOne;var BigInt=function(flag){if(typeof flag=="boolean"&&flag==true){this.digits=null}else{this.digits=ZERO_ARRAY.slice(0)}this.isNeg=false};RSAUtils.setMaxDigits=function(value){maxDigits=value;ZERO_ARRAY=new Array(maxDigits);for(var iza=0;iza<ZERO_ARRAY.length;iza++){ZERO_ARRAY[iza]=0}bigZero=new BigInt();bigOne=new BigInt();bigOne.digits[0]=1};RSAUtils.setMaxDigits(20);var dpl10=15;RSAUtils.biFromNumber=function(i){var result=new BigInt();result.isNeg=i<0;i=Math.abs(i);var j=0;while(i>0){result.digits[j++]=i&maxDigitVal;i=Math.floor(i/biRadix)}return result};var lr10=RSAUtils.biFromNumber(1000000000000000);RSAUtils.biFromDecimal=function(s){var isNeg=s.charAt(0)=="-";var i=isNeg?1:0;var result;while(i<s.length&&s.charAt(i)=="0"){++i}if(i==s.length){result=new BigInt()}else{var digitCount=s.length-i;var fgl=digitCount%dpl10;if(fgl==0){fgl=dpl10}result=RSAUtils.biFromNumber(Number(s.substr(i,fgl)));i+=fgl;while(i<s.length){result=RSAUtils.biAdd(RSAUtils.biMultiply(result,lr10),RSAUtils.biFromNumber(Number(s.substr(i,dpl10))));i+=dpl10}result.isNeg=isNeg}return result};RSAUtils.biCopy=function(bi){var result=new BigInt(true);result.digits=bi.digits.slice(0);result.isNeg=bi.isNeg;return result};RSAUtils.reverseStr=function(s){var result="";for(var i=s.length-1;i>-1;--i){result+=s.charAt(i)}return result};var hexatrigesimalToChar=["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"];RSAUtils.biToString=function(x,radix){var b=new BigInt();b.digits[0]=radix;var qr=RSAUtils.biDivideModulo(x,b);var result=hexatrigesimalToChar[qr[1].digits[0]];while(RSAUtils.biCompare(qr[0],bigZero)==1){qr=RSAUtils.biDivideModulo(qr[0],b);digit=qr[1].digits[0];result+=hexatrigesimalToChar[qr[1].digits[0]]}return(x.isNeg?"-":"")+RSAUtils.reverseStr(result)};RSAUtils.biToDecimal=function(x){var b=new BigInt();b.digits[0]=10;var qr=RSAUtils.biDivideModulo(x,b);var result=String(qr[1].digits[0]);while(RSAUtils.biCompare(qr[0],bigZero)==1){qr=RSAUtils.biDivideModulo(qr[0],b);result+=String(qr[1].digits[0])}return(x.isNeg?"-":"")+RSAUtils.reverseStr(result)};var hexToChar=["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"];RSAUtils.digitToHex=function(n){var mask=15;var result="";for(i=0;i<4;++i){result+=hexToChar[n&mask];n>>>=4}return RSAUtils.reverseStr(result)};RSAUtils.biToHex=function(x){var result="";var n=RSAUtils.biHighIndex(x);for(var i=RSAUtils.biHighIndex(x);i>-1;--i){result+=RSAUtils.digitToHex(x.digits[i])}return result};RSAUtils.charToHex=function(c){var ZERO=48;var NINE=ZERO+9;var littleA=97;var littleZ=littleA+25;var bigA=65;var bigZ=65+25;var result;if(c>=ZERO&&c<=NINE){result=c-ZERO}else{if(c>=bigA&&c<=bigZ){result=10+c-bigA}else{if(c>=littleA&&c<=littleZ){result=10+c-littleA}else{result=0}}}return result};RSAUtils.hexToDigit=function(s){var result=0;var sl=Math.min(s.length,4);for(var i=0;i<sl;++i){result<<=4;result|=RSAUtils.charToHex(s.charCodeAt(i))}return result};RSAUtils.biFromHex=function(s){var result=new BigInt();var sl=s.length;for(var i=sl,j=0;i>0;i-=4,++j){result.digits[j]=RSAUtils.hexToDigit(s.substr(Math.max(i-4,0),Math.min(i,4)))}return result};RSAUtils.biFromString=function(s,radix){var isNeg=s.charAt(0)=="-";var istop=isNeg?1:0;var result=new BigInt();var place=new BigInt();place.digits[0]=1;for(var i=s.length-1;i>=istop;i--){var c=s.charCodeAt(i);var digit=RSAUtils.charToHex(c);var biDigit=RSAUtils.biMultiplyDigit(place,digit);result=RSAUtils.biAdd(result,biDigit);place=RSAUtils.biMultiplyDigit(place,radix)}result.isNeg=isNeg;return result};RSAUtils.biDump=function(b){return(b.isNeg?"-":"")+b.digits.join(" ")};RSAUtils.biAdd=function(x,y){var result;if(x.isNeg!=y.isNeg){y.isNeg=!y.isNeg;result=RSAUtils.biSubtract(x,y);y.isNeg=!y.isNeg}else{result=new BigInt();var c=0;var n;for(var i=0;i<x.digits.length;++i){n=x.digits[i]+y.digits[i]+c;result.digits[i]=n%biRadix;c=Number(n>=biRadix)}result.isNeg=x.isNeg}return result};RSAUtils.biSubtract=function(x,y){var result;if(x.isNeg!=y.isNeg){y.isNeg=!y.isNeg;result=RSAUtils.biAdd(x,y);y.isNeg=!y.isNeg}else{result=new BigInt();var n,c;c=0;for(var i=0;i<x.digits.length;++i){n=x.digits[i]-y.digits[i]+c;result.digits[i]=n%biRadix;if(result.digits[i]<0){result.digits[i]+=biRadix}c=0-Number(n<0)}if(c==-1){c=0;for(var i=0;i<x.digits.length;++i){n=0-result.digits[i]+c;result.digits[i]=n%biRadix;if(result.digits[i]<0){result.digits[i]+=biRadix}c=0-Number(n<0)}result.isNeg=!x.isNeg}else{result.isNeg=x.isNeg}}return result};RSAUtils.biHighIndex=function(x){var result=x.digits.length-1;while(result>0&&x.digits[result]==0){--result}return result};RSAUtils.biNumBits=function(x){var n=RSAUtils.biHighIndex(x);var d=x.digits[n];var m=(n+1)*bitsPerDigit;var result;for(result=m;result>m-bitsPerDigit;--result){if((d&32768)!=0){break}d<<=1}return result};RSAUtils.biMultiply=function(x,y){var result=new BigInt();var c;var n=RSAUtils.biHighIndex(x);var t=RSAUtils.biHighIndex(y);var u,uv,k;for(var i=0;i<=t;++i){c=0;k=i;for(j=0;j<=n;++j,++k){uv=result.digits[k]+x.digits[j]*y.digits[i]+c;result.digits[k]=uv&maxDigitVal;c=uv>>>biRadixBits}result.digits[i+n+1]=c}result.isNeg=x.isNeg!=y.isNeg;return result};RSAUtils.biMultiplyDigit=function(x,y){var n,c,uv;result=new BigInt();n=RSAUtils.biHighIndex(x);c=0;for(var j=0;j<=n;++j){uv=result.digits[j]+x.digits[j]*y+c;result.digits[j]=uv&maxDigitVal;c=uv>>>biRadixBits}result.digits[1+n]=c;return result};RSAUtils.arrayCopy=function(src,srcStart,dest,destStart,n){var m=Math.min(srcStart+n,src.length);for(var i=srcStart,j=destStart;i<m;++i,++j){dest[j]=src[i]}};var highBitMasks=[0,32768,49152,57344,61440,63488,64512,65024,65280,65408,65472,65504,65520,65528,65532,65534,65535];RSAUtils.biShiftLeft=function(x,n){var digitCount=Math.floor(n/bitsPerDigit);var result=new BigInt();RSAUtils.arrayCopy(x.digits,0,result.digits,digitCount,result.digits.length-digitCount);var bits=n%bitsPerDigit;var rightBits=bitsPerDigit-bits;for(var i=result.digits.length-1,i1=i-1;i>0;--i,--i1){result.digits[i]=((result.digits[i]<<bits)&maxDigitVal)|((result.digits[i1]&highBitMasks[bits])>>>(rightBits))}result.digits[0]=((result.digits[i]<<bits)&maxDigitVal);result.isNeg=x.isNeg;return result};var lowBitMasks=[0,1,3,7,15,31,63,127,255,511,1023,2047,4095,8191,16383,32767,65535];RSAUtils.biShiftRight=function(x,n){var digitCount=Math.floor(n/bitsPerDigit);var result=new BigInt();RSAUtils.arrayCopy(x.digits,digitCount,result.digits,0,x.digits.length-digitCount);var bits=n%bitsPerDigit;var leftBits=bitsPerDigit-bits;for(var i=0,i1=i+1;i<result.digits.length-1;++i,++i1){result.digits[i]=(result.digits[i]>>>bits)|((result.digits[i1]&lowBitMasks[bits])<<leftBits)}result.digits[result.digits.length-1]>>>=bits;result.isNeg=x.isNeg;return result};RSAUtils.biMultiplyByRadixPower=function(x,n){var result=new BigInt();RSAUtils.arrayCopy(x.digits,0,result.digits,n,result.digits.length-n);return result};RSAUtils.biDivideByRadixPower=function(x,n){var result=new BigInt();RSAUtils.arrayCopy(x.digits,n,result.digits,0,result.digits.length-n);return result};RSAUtils.biModuloByRadixPower=function(x,n){var result=new BigInt();RSAUtils.arrayCopy(x.digits,0,result.digits,0,n);return result};RSAUtils.biCompare=function(x,y){if(x.isNeg!=y.isNeg){return 1-2*Number(x.isNeg)}for(var i=x.digits.length-1;i>=0;--i){if(x.digits[i]!=y.digits[i]){if(x.isNeg){return 1-2*Number(x.digits[i]>y.digits[i])}else{return 1-2*Number(x.digits[i]<y.digits[i])}}}return 0};RSAUtils.biDivideModulo=function(x,y){var nb=RSAUtils.biNumBits(x);var tb=RSAUtils.biNumBits(y);var origYIsNeg=y.isNeg;var q,r;if(nb<tb){if(x.isNeg){q=RSAUtils.biCopy(bigOne);q.isNeg=!y.isNeg;x.isNeg=false;y.isNeg=false;r=biSubtract(y,x);x.isNeg=true;y.isNeg=origYIsNeg}else{q=new BigInt();r=RSAUtils.biCopy(x)}return[q,r]}q=new BigInt();r=x;var t=Math.ceil(tb/bitsPerDigit)-1;var lambda=0;while(y.digits[t]<biHalfRadix){y=RSAUtils.biShiftLeft(y,1);++lambda;++tb;t=Math.ceil(tb/bitsPerDigit)-1}r=RSAUtils.biShiftLeft(r,lambda);nb+=lambda;var n=Math.ceil(nb/bitsPerDigit)-1;var b=RSAUtils.biMultiplyByRadixPower(y,n-t);while(RSAUtils.biCompare(r,b)!=-1){++q.digits[n-t];r=RSAUtils.biSubtract(r,b)}for(var i=n;i>t;--i){var ri=(i>=r.digits.length)?0:r.digits[i];var ri1=(i-1>=r.digits.length)?0:r.digits[i-1];var ri2=(i-2>=r.digits.length)?0:r.digits[i-2];var yt=(t>=y.digits.length)?0:y.digits[t];var yt1=(t-1>=y.digits.length)?0:y.digits[t-1];if(ri==yt){q.digits[i-t-1]=maxDigitVal}else{q.digits[i-t-1]=Math.floor((ri*biRadix+ri1)/yt)}var c1=q.digits[i-t-1]*((yt*biRadix)+yt1);var c2=(ri*biRadixSquared)+((ri1*biRadix)+ri2);while(c1>c2){--q.digits[i-t-1];c1=q.digits[i-t-1]*((yt*biRadix)|yt1);c2=(ri*biRadix*biRadix)+((ri1*biRadix)+ri2)}b=RSAUtils.biMultiplyByRadixPower(y,i-t-1);r=RSAUtils.biSubtract(r,RSAUtils.biMultiplyDigit(b,q.digits[i-t-1]));if(r.isNeg){r=RSAUtils.biAdd(r,b);--q.digits[i-t-1]}}r=RSAUtils.biShiftRight(r,lambda);q.isNeg=x.isNeg!=origYIsNeg;if(x.isNeg){if(origYIsNeg){q=RSAUtils.biAdd(q,bigOne)}else{q=RSAUtils.biSubtract(q,bigOne)}y=RSAUtils.biShiftRight(y,lambda);r=RSAUtils.biSubtract(y,r)}if(r.digits[0]==0&&RSAUtils.biHighIndex(r)==0){r.isNeg=false}return[q,r]};RSAUtils.biDivide=function(x,y){return RSAUtils.biDivideModulo(x,y)[0]};RSAUtils.biModulo=function(x,y){return RSAUtils.biDivideModulo(x,y)[1]};RSAUtils.biMultiplyMod=function(x,y,m){return RSAUtils.biModulo(RSAUtils.biMultiply(x,y),m)};RSAUtils.biPow=function(x,y){var result=bigOne;var a=x;while(true){if((y&1)!=0){result=RSAUtils.biMultiply(result,a)}y>>=1;if(y==0){break}a=RSAUtils.biMultiply(a,a)}return result};RSAUtils.biPowMod=function(x,y,m){var result=bigOne;var a=x;var k=y;while(true){if((k.digits[0]&1)!=0){result=RSAUtils.biMultiplyMod(result,a,m)}k=RSAUtils.biShiftRight(k,1);if(k.digits[0]==0&&RSAUtils.biHighIndex(k)==0){break}a=RSAUtils.biMultiplyMod(a,a,m)}return result};BarrettMu=function(m){this.modulus=RSAUtils.biCopy(m);this.k=RSAUtils.biHighIndex(this.modulus)+1;var b2k=new BigInt();b2k.digits[2*this.k]=1;this.mu=RSAUtils.biDivide(b2k,this.modulus);this.bkplus1=new BigInt();this.bkplus1.digits[this.k+1]=1;this.modulo=BarrettMu_modulo;this.multiplyMod=BarrettMu_multiplyMod;this.powMod=BarrettMu_powMod};function BarrettMu_modulo(x){var $dmath=RSAUtils;var q1=$dmath.biDivideByRadixPower(x,this.k-1);var q2=$dmath.biMultiply(q1,this.mu);var q3=$dmath.biDivideByRadixPower(q2,this.k+1);var r1=$dmath.biModuloByRadixPower(x,this.k+1);var r2term=$dmath.biMultiply(q3,this.modulus);var r2=$dmath.biModuloByRadixPower(r2term,this.k+1);var r=$dmath.biSubtract(r1,r2);if(r.isNeg){r=$dmath.biAdd(r,this.bkplus1)}var rgtem=$dmath.biCompare(r,this.modulus)>=0;while(rgtem){r=$dmath.biSubtract(r,this.modulus);rgtem=$dmath.biCompare(r,this.modulus)>=0}return r}function BarrettMu_multiplyMod(x,y){var xy=RSAUtils.biMultiply(x,y);return this.modulo(xy)}function BarrettMu_powMod(x,y){var result=new BigInt();result.digits[0]=1;var a=x;var k=y;while(true){if((k.digits[0]&1)!=0){result=this.multiplyMod(result,a)}k=RSAUtils.biShiftRight(k,1);if(k.digits[0]==0&&RSAUtils.biHighIndex(k)==0){break}a=this.multiplyMod(a,a)}return result}var RSAKeyPair=function(encryptionExponent,decryptionExponent,modulus){var $dmath=RSAUtils;this.e=$dmath.biFromHex(encryptionExponent);this.d=$dmath.biFromHex(decryptionExponent);this.m=$dmath.biFromHex(modulus);this.chunkSize=2*$dmath.biHighIndex(this.m);this.radix=16;this.barrett=new BarrettMu(this.m)};RSAUtils.getKeyPair=function(encryptionExponent,decryptionExponent,modulus){return new RSAKeyPair(encryptionExponent,decryptionExponent,modulus)};if(typeof twoDigit==="undefined"){twoDigit=function(n){return(n<10?"0":"")+String(n)}}RSAUtils.encryptedString=function(key,s){var a=[];var sl=s.length;var i=0;while(i<sl){a[i]=s.charCodeAt(i);i++}while(a.length%key.chunkSize!=0){a[i++]=0}var al=a.length;var result="";var j,k,block;for(i=0;i<al;i+=key.chunkSize){block=new BigInt();j=0;for(k=i;k<i+key.chunkSize;++j){block.digits[j]=a[k++];block.digits[j]+=a[k++]<<8}var crypt=key.barrett.powMod(block,key.e);var text=key.radix==16?RSAUtils.biToHex(crypt):RSAUtils.biToString(crypt,key.radix);result+=text+" "}var r="";var blocks=result.split(" ");for(k=blocks.length;k>=1;k--){r+=blocks[k-1]}return r};RSAUtils.decryptedString=function(key,s){var blocks=s.split(" ");var result="";var i,j,block;for(i=0;i<blocks.length;++i){var bi;if(key.radix==16){bi=RSAUtils.biFromHex(blocks[i])}else{bi=RSAUtils.biFromString(blocks[i],key.radix)}block=key.barrett.powMod(bi,key.d);for(j=0;j<=RSAUtils.biHighIndex(block);++j){result+=String.fromCharCode(block.digits[j]&255,block.digits[j]>>8)}}if(result.charCodeAt(result.length-1)==0){result=result.substring(0,result.length-1)}return result};RSAUtils.setMaxDigits(130);function get_data(msg){return RSAUtils.encryptedString(RSAUtils.getKeyPair("10001","","c9a49a5478a2df0ed8db5829788bd185"),msg)}""")
        old_password = zxt.call("get_data", old_password)
        new_password = zxt.call("get_data", new_password)
        r = self._session.post(CHANGE_PASSWORD_URL, data={
            "oldPassword": old_password,
            "newPassword": new_password
        })
        if r.json()["result"] != "success":
            return r.json()["message"]
        else:
            return "success"

    def _get_info(self) -> bool:
        """
        获取账户基本信息, 如用户id, 姓名, 学校等
        :return:
        """
        r = self._session.get(INFO_URL,
                              params={"userId": self.id})
        json_data = r.json().get("student")
        if not json_data.get("clazz", False):
            return False
        self.code = json_data.get("code")
        self.name = json_data.get("name")
        self.avatar = json_data.get("avatar")
        self.gender = "男" if json_data.get("gender") == "1" else "女"
        self.user_name = json_data.get("loginName")
        self.id = json_data.get("id")
        self.mobile = json_data.get("mobile")
        self.email = json_data.get("email")
        self.qq_number = json_data.get("im")
        self.clazz = classModel(
            json_data["clazz"]["id"],
            json_data["clazz"]["name"]
        )
        self.school = schoolModel(
            json_data["clazz"]["division"]["school"]["id"],
            json_data["clazz"]["division"]["school"]["name"]
        )
        birthday = int(json_data.get("birthday", 0)) / 1000
        if birthday > 0:
            self.birthday = birthdayModel(
                t=birthday
            )
        return True


Student.__get_auth_header = exam.__get_auth_header
Student.get_exam_id = exam.get_exam_id
Student.__get_page_exam_data = exam.__get_page_exam_data
Student.get_latest_exam = exam.get_latest_exam
Student.get_exams = exam.get_exams
Student.get_self_mark = exam.get_self_mark
Student.get_mark_with_weight = exam.get_mark_with_weight
Student.__get_paper_id = exam.__get_paper_id
Student.get_original = exam.get_original
Student.get_one_original_url = exam.get_one_original_url

Student.get_classmates = person.get_classmates
Student.get_friends = person.get_friends
Student.invite_friend = person.invite_friend
Student.remove_friend = person.remove_friend
Student.get_clazzs = person.get_clazzs
# Student.get_teachers = person.get_teachers
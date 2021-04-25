   function XML_Load(url, method, req_params, uparams) {
    this.XMLo=null;
    this.url = url;
    this.method = method;
    this.uparams = uparams;
    this.req_params = req_params;

    try { this.XMLo = new XMLHttpRequest(); }
    catch (e) { this.XMLo=null; }
    if (this.XMLo!=null) {
       while (this.XMLo.readyState != 4 && this.XMLo.readyState != 0) {}
    }
   }

   XML_Load.prototype.IsReady=function() {
    if (this.XMLo==null) return false;
    return true;
   }

   XML_Load.prototype.Load=function() {
    if (this.method == "POST") {
        this.XMLo.open("POST", this.url, true);
        this.XMLo.setRequestHeader('Content-Type','application/x-www-form-urlencoded; charset=utf-8');
    } else if (this.method == "GET") {
        this.XMLo.open("GET", this.url+'?'+this.req_params, true);
    }

    var eobj=this;

    this.XMLo.onreadystatechange = function () {
     var eclass = eobj;
     var eXMLo = eclass.XMLo;

     if (eXMLo.readyState == 4) {
         if (eXMLo.status == 200) {
             eclass.OnReady("", eclass.uparams, eXMLo.responseText);
             delete eXMLo;
             delete eclass;
         } else {
             eclass.OnReady("There was a problem retrieving data:\n" + eXMLo.statusText,eclass.uparams, eXMLo.responseText);
             delete eXMLo;
             delete eclass;
         }
      }
    }

    if (this.method == 'POST') this.XMLo.send(this.req_params);
    else if (this.method == 'GET') this.XMLo.send(null);

   }

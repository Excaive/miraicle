(self.webpackChunkmiraicle_document=self.webpackChunkmiraicle_document||[]).push([[445],{3905:function(e,t,n){"use strict";n.d(t,{Zo:function(){return l},kt:function(){return d}});var r=n(7294);function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){i(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function p(e,t){if(null==e)return{};var n,r,i=function(e,t){if(null==e)return{};var n,r,i={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(i[n]=e[n]);return i}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(i[n]=e[n])}return i}var c=r.createContext({}),m=function(e){var t=r.useContext(c),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},l=function(e){var t=m(e.components);return r.createElement(c.Provider,{value:t},e.children)},s={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},u=r.forwardRef((function(e,t){var n=e.components,i=e.mdxType,a=e.originalType,c=e.parentName,l=p(e,["components","mdxType","originalType","parentName"]),u=m(n),d=i,f=u["".concat(c,".").concat(d)]||u[d]||s[d]||a;return n?r.createElement(f,o(o({ref:t},l),{},{components:n})):r.createElement(f,o({ref:t},l))}));function d(e,t){var n=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var a=n.length,o=new Array(a);o[0]=u;var p={};for(var c in t)hasOwnProperty.call(t,c)&&(p[c]=t[c]);p.originalType=e,p.mdxType="string"==typeof e?e:i,o[1]=p;for(var m=2;m<a;m++)o[m]=n[m];return r.createElement.apply(null,o)}return r.createElement.apply(null,n)}u.displayName="MDXCreateElement"},1977:function(e,t,n){"use strict";n.r(t),n.d(t,{frontMatter:function(){return p},contentTitle:function(){return c},metadata:function(){return m},toc:function(){return l},default:function(){return u}});var r=n(2122),i=n(9756),a=(n(7294),n(3905)),o=["components"],p={sidebar_position:2},c="\u51c6\u5907",m={unversionedId:"guides/prepare",id:"guides/prepare",isDocsHomePage:!1,title:"\u51c6\u5907",description:"miraicle \u662f\u57fa\u4e8e mirai-api-http \u7684\uff0cmirai-api-http \u53c8\u662f mirai-console \u7684\u4e00\u4e2a\u63d2\u4ef6\u3002\u5728\u4f7f\u7528 miraicle \u4e4b\u524d\uff0c\u8bf7\u6309\u7167 mirai-api-http \u7684\u6587\u6863\u8fdb\u884c\u73af\u5883\u642d\u5efa\u548c\u63d2\u4ef6\u914d\u7f6e\u3002",source:"@site/docs/guides/prepare.md",sourceDirName:"guides",slug:"/guides/prepare",permalink:"/miraicle/docs/guides/prepare",editUrl:"https://github.com/facebook/docusaurus/edit/master/website/docs/guides/prepare.md",version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2},sidebar:"guides",previous:{title:"\u5b89\u88c5",permalink:"/miraicle/docs/guides/install"},next:{title:"\u5f00\u59cb\u4f7f\u7528",permalink:"/miraicle/docs/guides/start-to-use"}},l=[],s={toc:l};function u(e){var t=e.components,n=(0,i.Z)(e,o);return(0,a.kt)("wrapper",(0,r.Z)({},s,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"\u51c6\u5907"},"\u51c6\u5907"),(0,a.kt)("p",null,(0,a.kt)("inlineCode",{parentName:"p"},"miraicle")," \u662f\u57fa\u4e8e ",(0,a.kt)("a",{parentName:"p",href:"https://github.com/project-mirai/mirai-api-http"},"mirai-api-http")," \u7684\uff0c",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u53c8\u662f ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-console")," \u7684\u4e00\u4e2a\u63d2\u4ef6\u3002\u5728\u4f7f\u7528 ",(0,a.kt)("inlineCode",{parentName:"p"},"miraicle")," \u4e4b\u524d\uff0c\u8bf7\u6309\u7167 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u7684\u6587\u6863\u8fdb\u884c\u73af\u5883\u642d\u5efa\u548c\u63d2\u4ef6\u914d\u7f6e\u3002"),(0,a.kt)("p",null,"\u4f60\u53ef\u4ee5\u4f7f\u7528 ",(0,a.kt)("a",{parentName:"p",href:"https://github.com/iTXTech/mirai-console-loader"},"mirai-console-loader")," \uff0c\u5b83\u4f1a\u5bf9 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-console")," \u8fdb\u884c\u4e00\u952e\u542f\u52a8\u548c\u81ea\u52a8\u66f4\u65b0\u3002\u5b89\u88c5\u597d ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u4e4b\u540e\uff0c\u5c06 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"setting.yml")," \u6a21\u677f\u590d\u5236\u7c98\u8d34\u5230\u914d\u7f6e\u6587\u4ef6\u91cc\uff0c\u5e76\u81ea\u5df1\u8bbe\u7f6e\u4e00\u4e2a ",(0,a.kt)("inlineCode",{parentName:"p"},"verifyKey")," \u548c ",(0,a.kt)("inlineCode",{parentName:"p"},"port"),"\u3002"),(0,a.kt)("div",{className:"admonition admonition-info alert alert--info"},(0,a.kt)("div",{parentName:"div",className:"admonition-heading"},(0,a.kt)("h5",{parentName:"div"},(0,a.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,a.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,a.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M7 2.3c3.14 0 5.7 2.56 5.7 5.7s-2.56 5.7-5.7 5.7A5.71 5.71 0 0 1 1.3 8c0-3.14 2.56-5.7 5.7-5.7zM7 1C3.14 1 0 4.14 0 8s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm1 3H6v5h2V4zm0 6H6v2h2v-2z"}))),"\u6ce8\u610f")),(0,a.kt)("div",{parentName:"div",className:"admonition-content"},(0,a.kt)("p",{parentName:"div"},(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u76ee\u524d\u5df2\u7ecf\u66f4\u65b0\u5230 ",(0,a.kt)("inlineCode",{parentName:"p"},"2.x")," \u7248\u672c\uff0c\u8fd9\u4e0e ",(0,a.kt)("inlineCode",{parentName:"p"},"1.x")," \u7248\u672c\u76f8\u6bd4\u6709\u4e0d\u5c11\u53d8\u52a8\u3002",(0,a.kt)("inlineCode",{parentName:"p"},"miraicle")," \u4ec5\u652f\u6301 ",(0,a.kt)("inlineCode",{parentName:"p"},"2.x")," \u7248\u672c\u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \uff0c\u8bf7\u68c0\u67e5\u4f60\u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u7248\u672c\u662f\u5426\u6b63\u786e\u3002"))))}u.isMDXComponent=!0}}]);
(self.webpackChunkmiraicle_document=self.webpackChunkmiraicle_document||[]).push([[897],{3905:function(e,t,n){"use strict";n.d(t,{Zo:function(){return m},kt:function(){return u}});var i=n(7294);function r(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var i=Object.getOwnPropertySymbols(e);t&&(i=i.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,i)}return n}function o(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){r(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function p(e,t){if(null==e)return{};var n,i,r=function(e,t){if(null==e)return{};var n,i,r={},a=Object.keys(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||(r[n]=e[n]);return r}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(i=0;i<a.length;i++)n=a[i],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(r[n]=e[n])}return r}var l=i.createContext({}),c=function(e){var t=i.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):o(o({},t),e)),n},m=function(e){var t=c(e.components);return i.createElement(l.Provider,{value:t},e.children)},s={inlineCode:"code",wrapper:function(e){var t=e.children;return i.createElement(i.Fragment,{},t)}},d=i.forwardRef((function(e,t){var n=e.components,r=e.mdxType,a=e.originalType,l=e.parentName,m=p(e,["components","mdxType","originalType","parentName"]),d=c(n),u=r,f=d["".concat(l,".").concat(u)]||d[u]||s[u]||a;return n?i.createElement(f,o(o({ref:t},m),{},{components:n})):i.createElement(f,o({ref:t},m))}));function u(e,t){var n=arguments,r=t&&t.mdxType;if("string"==typeof e||r){var a=n.length,o=new Array(a);o[0]=d;var p={};for(var l in t)hasOwnProperty.call(t,l)&&(p[l]=t[l]);p.originalType=e,p.mdxType="string"==typeof e?e:r,o[1]=p;for(var c=2;c<a;c++)o[c]=n[c];return i.createElement.apply(null,o)}return i.createElement.apply(null,n)}d.displayName="MDXCreateElement"},5473:function(e,t,n){"use strict";n.r(t),n.d(t,{frontMatter:function(){return p},contentTitle:function(){return l},metadata:function(){return c},toc:function(){return m},default:function(){return d}});var i=n(2122),r=n(9756),a=(n(7294),n(3905)),o=["components"],p={sidebar_position:2},l="\u73af\u5883\u642d\u5efa",c={unversionedId:"guides/install",id:"guides/install",isDocsHomePage:!1,title:"\u73af\u5883\u642d\u5efa",description:"\u5b89\u88c5 miraicle",source:"@site/docs/guides/2-install.md",sourceDirName:"guides",slug:"/guides/install",permalink:"/miraicle/docs/guides/install",editUrl:"https://github.com/facebook/docusaurus/edit/master/website/docs/guides/2-install.md",version:"current",sidebarPosition:2,frontMatter:{sidebar_position:2},sidebar:"guides",previous:{title:"\u7b80\u4ecb",permalink:"/miraicle/docs/guides/intro"},next:{title:"\u5f00\u59cb\u4f7f\u7528",permalink:"/miraicle/docs/guides/start-to-use"}},m=[{value:"\u5b89\u88c5 miraicle",id:"\u5b89\u88c5-miraicle",children:[]},{value:"\u5b89\u88c5\u548c\u914d\u7f6e mirai-api-http",id:"\u5b89\u88c5\u548c\u914d\u7f6e-mirai-api-http",children:[]}],s={toc:m};function d(e){var t=e.components,n=(0,r.Z)(e,o);return(0,a.kt)("wrapper",(0,i.Z)({},s,n,{components:t,mdxType:"MDXLayout"}),(0,a.kt)("h1",{id:"\u73af\u5883\u642d\u5efa"},"\u73af\u5883\u642d\u5efa"),(0,a.kt)("h2",{id:"\u5b89\u88c5-miraicle"},"\u5b89\u88c5 miraicle"),(0,a.kt)("p",null,"\u548c\u5f88\u591a\u5176\u4ed6\u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"Python")," \u7b2c\u4e09\u65b9\u5e93\u4e00\u6837\uff0c\u4f60\u53ef\u4ee5\u4ece ",(0,a.kt)("inlineCode",{parentName:"p"},"PyPi")," \u5b89\u88c5 ",(0,a.kt)("inlineCode",{parentName:"p"},"miraicle"),"\uff0c\u8fd9\u9700\u8981\u4f60\u7684\u7248\u672c\u5728 3.6 \u6216\u4ee5\u4e0a\u3002"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-bash"},"pip install miraicle\n")),(0,a.kt)("p",null,"\u5982\u679c\u4f60\u5df2\u7ecf\u5b89\u88c5\u4e86 ",(0,a.kt)("inlineCode",{parentName:"p"},"miraicle"),"\uff0c\u60f3\u8981\u628a\u5b83\u66f4\u65b0\u5230\u6700\u65b0\u7248\u672c\uff0c\u4f60\u53ef\u4ee5\u8f93\u5165\uff1a"),(0,a.kt)("pre",null,(0,a.kt)("code",{parentName:"pre",className:"language-bash"},"pip install --upgrade miraicle\n")),(0,a.kt)("h2",{id:"\u5b89\u88c5\u548c\u914d\u7f6e-mirai-api-http"},"\u5b89\u88c5\u548c\u914d\u7f6e mirai-api-http"),(0,a.kt)("p",null,(0,a.kt)("inlineCode",{parentName:"p"},"miraicle")," \u662f\u57fa\u4e8e ",(0,a.kt)("a",{parentName:"p",href:"https://github.com/project-mirai/mirai-api-http"},(0,a.kt)("inlineCode",{parentName:"a"},"mirai-api-http"))," \u7684\uff0c",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u53c8\u662f ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-console")," \u7684\u4e00\u4e2a\u63d2\u4ef6\u3002\u5728\u4f7f\u7528 ",(0,a.kt)("inlineCode",{parentName:"p"},"miraicle")," \u4e4b\u524d\uff0c\u8bf7\u6309\u7167 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u7684\u6587\u6863\u8fdb\u884c\u73af\u5883\u642d\u5efa\u548c\u63d2\u4ef6\u914d\u7f6e\u3002"),(0,a.kt)("p",null,"\u4f60\u53ef\u4ee5\u4f7f\u7528 ",(0,a.kt)("a",{parentName:"p",href:"https://github.com/iTXTech/mirai-console-loader"},(0,a.kt)("inlineCode",{parentName:"a"},"mirai-console-loader"))," \uff0c\u5b83\u4f1a\u5bf9 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-console")," \u8fdb\u884c\u4e00\u952e\u542f\u52a8\u548c\u81ea\u52a8\u66f4\u65b0\u3002\u5b89\u88c5\u597d ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u4e4b\u540e\uff0c\u5c06 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"setting.yml")," \u6a21\u677f\u590d\u5236\u7c98\u8d34\u5230\u914d\u7f6e\u6587\u4ef6\u91cc\uff0c\u5e76\u81ea\u5df1\u8bbe\u7f6e\u4e00\u4e2a ",(0,a.kt)("inlineCode",{parentName:"p"},"verifyKey")," \u548c ",(0,a.kt)("inlineCode",{parentName:"p"},"port"),"\u3002"),(0,a.kt)("div",{className:"admonition admonition-info alert alert--info"},(0,a.kt)("div",{parentName:"div",className:"admonition-heading"},(0,a.kt)("h5",{parentName:"div"},(0,a.kt)("span",{parentName:"h5",className:"admonition-icon"},(0,a.kt)("svg",{parentName:"span",xmlns:"http://www.w3.org/2000/svg",width:"14",height:"16",viewBox:"0 0 14 16"},(0,a.kt)("path",{parentName:"svg",fillRule:"evenodd",d:"M7 2.3c3.14 0 5.7 2.56 5.7 5.7s-2.56 5.7-5.7 5.7A5.71 5.71 0 0 1 1.3 8c0-3.14 2.56-5.7 5.7-5.7zM7 1C3.14 1 0 4.14 0 8s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm1 3H6v5h2V4zm0 6H6v2h2v-2z"}))),"\u6ce8\u610f")),(0,a.kt)("div",{parentName:"div",className:"admonition-content"},(0,a.kt)("p",{parentName:"div"},(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u76ee\u524d\u5df2\u7ecf\u66f4\u65b0\u5230 ",(0,a.kt)("inlineCode",{parentName:"p"},"2.x")," \u7248\u672c\uff0c\u8fd9\u4e0e ",(0,a.kt)("inlineCode",{parentName:"p"},"1.x")," \u7248\u672c\u76f8\u6bd4\u6709\u4e0d\u5c11\u53d8\u52a8\u3002",(0,a.kt)("inlineCode",{parentName:"p"},"miraicle")," \u4ec5\u652f\u6301 ",(0,a.kt)("inlineCode",{parentName:"p"},"2.x")," \u7248\u672c\u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \uff0c\u8bf7\u68c0\u67e5\u4f60\u7684 ",(0,a.kt)("inlineCode",{parentName:"p"},"mirai-api-http")," \u7248\u672c\u662f\u5426\u6b63\u786e\u3002"))))}d.isMDXComponent=!0}}]);
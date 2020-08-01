# python-scrapy rrys2019.com
A simple python scrapy project to crawl dynamic loaded data on a website


Goal:Find out the total traffics for the 24 hour download section


By inspecting the resource code in Chrome Dev tool, we can see the resource_views has not been directly writen into the html code. 
So it is very possibly that the data was attracted via a js http request(AJAX) then dynamically added to the DOM. 


We then go to the XHR section in Network(which refers to XMLHttpRequest object in js) but didn't find it.


Refilter to All and filter out unrelated css and images, we finally found a file named resource.js which records resource view.
By loading the js in Source panel, we can see this line:
//浏览数
  if(!GLOBAL.Empty(index_info.views))$('label#resource_views').html(index_info.views);
which pretty much gives us a cue of how it's being generated.

Let's print the global variable "index_info" in console, we can see
{cate_ranks: Array(8), hot_user: Array(5), similar: Array(0), followed: 0, manage: "", …}


We also found a js file named tv
From the headers tab in Network, we can see the request URL is:
Request URL: http://www.rrys2020.com/resource/index_json/rid/40528/channel/tv
which is exactly the json datawe saw in index_info



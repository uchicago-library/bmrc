// function toggleBurger() {
//     var burger = $('.burger');
//     var menu = $('.navbar-menu');
//     burger.toggleClass('is-active');
//     menu.toggleClass('is-active');
// }

/*************************************
 * VIEW MORE / VIEW ALL FACETS LINKS *
 *************************************/

// get the view less and view more limits from data attributes.
var view_less_limit = 0;
var view_more_limit = 0;
if (document.getElementById('facets')) {
    view_less_limit = parseInt(document.getElementById('facets').dataset.sidebar_view_less_facet_count);
    view_more_limit = parseInt(document.getElementById('facets').dataset.sidebar_view_more_facet_count);
}

var facets = document.getElementsByClassName('facet');
for (var i = 0; i < facets.length; i++) {
    var facet_name = facets[i].dataset.facet;

    var ul = facets[i].querySelector('ul');
    var lis = facets[i].querySelectorAll('li:not([view_link])');
    var lis_length = lis.length;

    for (var j = lis.length - 1; j >= 0; j--) {
        if (j >= view_more_limit) {
            lis[j].parentNode.removeChild(lis[j]);
        } else if (j >= view_less_limit) {
            lis[j].classList.add('view_more');
            lis[j].style.display = 'none';
        }
    }

    if (lis_length > view_less_limit) {
        ul.innerHTML += '<li class="view_link"><a class="view_more_link" href="#">View more ' + facet_name + ' >></a></li>';
        ul.innerHTML += '<li class="view_link"><a class="view_less_link" href="#"><< View less ' + facet_name + '</a></li>';
        ul.querySelector('.view_less_link').parentNode.style.display = 'none';
    }
    if (lis_length > view_more_limit) {
        ul.innerHTML += '<li class="view_link"><a class="view_all_link" href="#">View all relevant ' + facet_name + ' >></a></li>';
        ul.querySelector('.view_all_link').parentNode.style.display = 'none';
    }
}

// view less links.
var view_less_links = document.getElementsByClassName('view_less_link');
for (var i = 0; i < view_less_links.length; i++) {
    view_less_links[i].onclick = function (e) {
        e.preventDefault();

        var a = this;

        var div = a.parentNode.parentNode.parentNode;

        // get the facet name, e.g. "Organizations", from link text.
        var facet_name = div.dataset.facet;

        // get the "view more" <li>s for this facet.
        var lis = a.parentNode.parentNode.querySelectorAll('li[class="view_more"]');

        // turn off view more links.
        for (var j = 0; j < lis.length; j++) {
            lis[j].style.display = 'none';
        }

        div.querySelector('.view_less_link').parentNode.style.display = 'none';
        div.querySelector('.view_more_link').parentNode.style.display = 'block';
        div.querySelector('.view_all_link').parentNode.style.display = 'none';
    };
}

// view more links.
var view_more_links = document.getElementsByClassName('view_more_link');
for (var i = 0; i < view_more_links.length; i++) {
    view_more_links[i].onclick = function (e) {
        e.preventDefault();

        var a = this;

        var div = a.parentNode.parentNode.parentNode;

        // get the facet name, e.g. "Organizations", from link text.
        var facet_name = div.dataset.facet;

        // get the "view more" <li>s for this facet.
        var lis = a.parentNode.parentNode.querySelectorAll('li[class="view_more"]');

        // turn on view more links.
        for (var j = 0; j < lis.length; j++) {
            lis[j].style.display = 'block';
        }

        div.querySelector('.view_less_link').parentNode.style.display = 'block';
        div.querySelector('.view_more_link').parentNode.style.display = 'none';
        div.querySelector('.view_all_link').parentNode.style.display = 'block';
    };
}

/****************************
 * MODAL OVERLAY FOR FACETS *
 ****************************/

var overlay = document.querySelector('.modal-content');

var view_all_links = document.getElementsByClassName('view_all_link');
for (var i = 0; i < view_all_links.length; i++) {
    view_all_links[i].onclick = function (e) {
        e.preventDefault();

        var a = this;

        // e.g. "people"
        var facet_name = a.parentNode.parentNode.parentNode.dataset.facet;

        document.querySelector('.modal').classList.add('is-active');

        document.querySelector('.modal-content').innerHTML = '<div class="loader-wrapper"><div class="loader is-large is-loading"></div></div>';

        var xml_http = new XMLHttpRequest();
        xml_http.onreadystatechange = function () {
            if (xml_http.readyState == 4 && xml_http.status == 200) {
                overlay.innerHTML = xml_http.responseText;

                var sort_links = document.getElementsByClassName('facet_overlay_sort');
                for (var j = 0; j < sort_links.length; j++) {
                    sort_links[j].onclick = function (e) {
                        e.preventDefault();

                        document.querySelector('.modal-content').innerHTML = '<div class="loader-wrapper"><div class="loader is-loading"></div></div>';

                        var a = this;

                        var facet_uri = 'https://bmrc.lib.uchicago.edu/' + facet_name + '/';

                        var params = window.location.search;
                        if (params) {
                            params += '&'
                        } else {
                            params += '?'
                        }
                        params += 'fsort=' + encodeURIComponent(a.dataset.sort);
                        params += '&a=' + encodeURIComponent(facet_uri)

                        var url = '/portal/facet_view_all/' + params;
                        overlay.dataset.url = url;
                        xml_http.open('GET', url);
                        xml_http.send(null);
                    }
                }
            }
        }
        var facet_uri = 'https://bmrc.lib.uchicago.edu/' + facet_name + '/';
        var params = window.location.search;
        if (params) {
            params += '&a=' + encodeURIComponent(facet_uri)
        } else {
            params = '?a=' + encodeURIComponent(facet_uri)
        }
        var url = '/portal/facet_view_all/' + params;
        overlay.dataset.url = url;
        xml_http.open('GET', url);
        xml_http.send(null);
    }
}

// need the x to close out the overlay.
close_modal = function (e) {
    e.preventDefault();
    document.querySelector('.modal').classList.remove('is-active');
}

document.querySelector('.modal-background').onclick = close_modal;
document.querySelector('.modal-close').onclick = close_modal;

# -*- coding: utf-8 -*-
import scrapy


class ZomatoSpider(scrapy.Spider):
    name = 'zomato_from_us'
    start_urls = ['https://www.zomato.com/united-states']

    def parse(self, response):
        css = 'a[style="flex-grow: 1;"]::attr(href)'
        for href in response.css(css).extract():
            yield scrapy.Request(href + "/restaurants/", callback=self.parse_city)

    def parse_city(self, response):
        css = 'a[class="result-title hover_feedback zred bold ln24   fontsize0 "]::attr(href)'
        for href in response.css(css):
            yield response.follow(href, callback=self.parse_res)

        css = 'a[class="paginator_item   next item"]::attr(href)'
        for href in response.css(css):
            yield response.follow(href, callback=self.parse_city)

    def parse_res(self, response):
        yield {
            'location': response.css('a[itemprop="item"] span::text').extract()[1:],
            'name': response.css('a[class="ui large header left"]::attr(title)').extract_first(),
            'phone': response.css('span[class="tel"]::text').extract_first(),
            'cuisines': response.css('a[class="zred"][title]::text').extract(),
            'cost': response.css('div.res-info-detail span[tabindex]::text').extract(),
            'website': response.css('a[rel="noopener"]::attr(href)').extract_first(),
            'open_hours': response.css('table[style="border:0"] tr td::text').extract(),
            'address': response.css('div.resinfo-icon span::text').extract() +
                       response.css('div.resinfo-icon span a::text').extract(),
            'more_info': response.css('div.res-info-feature-text::text').extract()
        }

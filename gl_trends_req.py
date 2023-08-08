import contextlib
import time
import requests
import pandas as pd
from pytrends.request import TrendReq
from selenium import webdriver

requests_args = {
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/108.0.0.0 Safari/537.36'
    }
}


class _TrendReq(TrendReq):
    pass
    # ... rewriting class functionality to make it work ...


@contextlib.contextmanager
def _requests_get_as_post():
    # replacing methods
    requests.get, requests_get = requests.post, requests.get
    try:
        yield
    finally:
        requests.get = requests_get


# using _TrendReq instead of TrendReq
with _requests_get_as_post():
    pytrends = _TrendReq()


# pt = TrendReq(hl="en-US", tz=360)
# kw_list = ["патчи для глаз"]
# pt.build_payload(kw_list, timeframe='today 5-y', geo='RU', gprop='')
# massive = pt.interest_over_time()
# print(massive.tail(20))


class Common_trends:
    """Getting data from Google Trends about selected keywords."""
    def __init__(self, kw_list=[], timeframe='today 5-y', region='US', savedir=None):
        """
           Creating base element to request data from Google Trends.

            Args:
                kw_list (list): list of keywords for request
                timeframe (string): time for collection of statistics
                region (string): two-letter designation of the region
                savedir (string): path to save results of requests

            Returns:
                None
        """
        self.pt = TrendReq(retries=5,timeout=(5, 10))

        # self.pt = TrendReq(hl="en-US", tz=360,requests_args=requests_args)
        self.kw_list = kw_list
        self.timeframe = timeframe
        self.region = region
        self.savedir = savedir + '\\'

    def get_region(self):
        """Get data on relative interest in the selected key for a period of time in the specified region, if the region is
        not specified, the global trend is returned."""
        massive = pd.DataFrame()
        if len(self.kw_list) > 5:
            blocks = [self.kw_list[i:i + 5] for i in range(0, len(self.kw_list), 5)]
            for i in range(len(blocks)):
                self.pt.build_payload(blocks[i], timeframe=self.timeframe, geo=self.region, gprop='')
                temp = self.pt.interest_over_time()
                if massive.empty:
                    massive = temp
                else:
                    massive = pd.concat([massive, temp], axis=1)
                time.sleep(10)
        else:
            self.pt.build_payload(self.kw_list, timeframe=self.timeframe, geo=self.region, gprop='')
            massive = self.pt.interest_over_time()
        massive.to_excel(self.savedir + self.region+'_trends.xlsx')

    def get_global(self):
        """Get data on relative interest in the selected key for a period of time by countries"""
        by_country = pd.DataFrame()
        if len(self.kw_list) > 5:
            blocks = [self.kw_list[i:i + 5] for i in range(0, len(self.kw_list), 5)]
            for i in range(len(blocks)):
                self.pt.build_payload(blocks[i], timeframe=self.timeframe, gprop='')
                temp = self.pt.interest_by_region("COUNTRY", inc_low_vol=True, inc_geo_code=True)
                # by_country = pd.merge(by_country, temp, left_index=True, right_index=True)
                if by_country.empty:
                    by_country = temp
                else:
                    by_country = pd.concat([by_country, temp], axis=1)
                time.sleep(10)
        else:
            self.pt.build_payload(self.kw_list, timeframe=self.timeframe, gprop='')
            by_country = self.pt.interest_by_region("COUNTRY", inc_low_vol=True, inc_geo_code=True)
        by_country.to_excel(self.savedir + 'intr_by_country.xlsx')

    def get_by_country(self):
        """Get data on relative interest in the selected key for a period of time
        by subregions in selected region(country)"""
        by_city = pd.DataFrame()
        by_region = pd.DataFrame()
        by_dma = pd.DataFrame()
        if len(self.kw_list) > 5:
            blocks = [self.kw_list[i:i + 5] for i in range(0, len(self.kw_list), 5)]
            for i in range(len(blocks)):
                self.pt.build_payload(blocks[i], timeframe=self.timeframe, geo=self.region, gprop='')
                temp_city = self.pt.interest_by_region("CITY", inc_low_vol=True, inc_geo_code=True)
                temp_region = self.pt.interest_by_region("REGION", inc_low_vol=True, inc_geo_code=True)
                temp_dma = self.pt.interest_by_region("DMA", inc_low_vol=True, inc_geo_code=True)
                if by_city.empty:
                    by_city = temp_city
                    by_region = temp_region
                    by_dma = temp_dma
                else:
                    by_city = pd.merge(by_city, temp_city, left_index=True, right_index=True)
                    by_region = pd.merge(by_region, temp_region, left_index=True, right_index=True)
                    by_dma = pd.merge(by_dma, temp_dma, left_index=True, right_index=True)
        else:
            self.pt.build_payload(self.kw_list, timeframe=self.timeframe, geo=self.region, gprop='')
            by_city = self.pt.interest_by_region("CITY", inc_low_vol=True, inc_geo_code=True)
            by_region = self.pt.interest_by_region("REGION", inc_low_vol=True, inc_geo_code=True)
            by_dma = self.pt.interest_by_region("DMA", inc_low_vol=True, inc_geo_code=True)
        with pd.ExcelWriter(self.savedir + 'trends_by_county.xlsx', engine='xlsxwriter') as writer:
            by_region.to_excel(writer, sheet_name='Region', index=True)
            by_city.to_excel(writer, sheet_name='City', index=True)
            by_dma.to_excel(writer, sheet_name='DMA', index=True)

    def related_topics(self, ):
        """Get data about related topics, suggested by Google to the selected key"""
        rising = pd.DataFrame()
        top = pd.DataFrame()
        for kw in self.kw_list:
            kw_list = []
            kw_list.append(kw)
            self.pt.build_payload(kw_list, timeframe='today 1-y', geo=self.region, gprop='')
            rt = self.pt.related_topics()
            rt[kw]['rising']['key'] = kw
            rising = pd.concat([rising, rt[kw]['rising']], ignore_index=True)
            rt[kw]['top']['key'] = kw
            top = pd.concat([rising, rt[kw]['top']], ignore_index=True)
        with pd.ExcelWriter(self.savedir + 'Related topics.xlsx', engine='xlsxwriter') as writer:
            rising.to_excel(writer, sheet_name='rising', index=True)
            top.to_excel(writer, sheet_name='top', index=True)

        # self.pt.build_payload(self.kw_list, timeframe=self.timeframe, geo=self.region, gprop='')

    def related_searches(self):
        """Get data about related searches, suggested by Google to the selected key"""
        rising = pd.DataFrame()
        top = pd.DataFrame()
        for kw in self.kw_list:
            kw_list = []
            kw_list.append(kw)

            self.pt.build_payload(kw_list, timeframe='today 1-y', geo=self.region, gprop='')
            rt = self.pt.related_queries()
            if rt[kw]['rising'] is not None:
                rt[kw]['rising']['key'] = kw
                rising = pd.concat([rising, rt[kw]['rising']], ignore_index=True)
            if rt[kw]['top']is not None:
                rt[kw]['top']['key'] = kw
                top = pd.concat([rising, rt[kw]['top']], ignore_index=True)
        with pd.ExcelWriter(self.savedir + 'Related searches '+'.xlsx', engine='xlsxwriter') as writer:
            rising.to_excel(writer, sheet_name='rising', index=True)
            top.to_excel(writer, sheet_name='top', index=True)

        # self.pt.build_payload(self.kw_list, timeframe=self.timeframe, geo=self.region, gprop='')

    def suggested_topics(self):
        """Get data about suggested topics Google to the selected key"""
        sugg = pd.DataFrame()
        for kw in self.kw_list:
            topics = self.pt.suggestions(kw)
            temp = pd.DataFrame(topics)
            temp['key'] = kw
            sugg = pd.concat([sugg, temp], ignore_index=True)
        sugg.to_excel(self.savedir + 'Suggested topics.xlsx')

# test = Common_trends(kw_list=['iphone', 'ios'],savedir='C:\\Users\\aos.user5\\Desktop')
# test.get_region()
# test.related_searches()
# test.suggested_topics()

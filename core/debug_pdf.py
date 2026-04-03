import requests

PDF_URL = "https://www.energizect.com/ect-offer.pdf"

COOKIES = {
    "_gcl_au": "1.1.657596300.1770939545",
    "_tt_enable_cookie": "1",
    "_ttp": "01KHA3HY39245ZT6GBESABKF6K_.tt.1",
    "_fbp": "fb.1.1770939545798.123441726250878494",
    "_ga": "GA1.2.374940309.1770939545",
    "_gid": "GA1.2.61179921.1771200573",
    "ttcsid": "1771200572777::6IAAtOWUEBsZqQM-BYa7.4.1771202155533.0",
    "ttcsid_CJJU1UJC77U5TJETGS4G": "1771200572777::M-niay5x-7_YaD6eVkki.4.1771202155533.0",
    "_ga_RLRWBKWE8W": "GS2.1.s1771200572$o4$g1$t1771202155$j51$l0$h0",
    "_ga_T115VXTNM2": "GS2.1.s1771200572$o4$g1$t1771202155$j60$l0$h0",
    "_ga_NF0YV9R0LC": "GS2.2.s1771200572$o3$g1$t1771202155$j60$l0$h0",
    "_gat_UA-37521649-1": "1",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Referer": "https://www.energizect.com/rate-board/compare-energy-supplier-rates",
}

resp = requests.get(PDF_URL, cookies=COOKIES, headers=headers)
open("ct_real.pdf", "wb").write(resp.content)

print("Downloaded", len(resp.content), "bytes")